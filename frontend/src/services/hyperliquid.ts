/**
 * Servicio para obtener datos de traders de Hyperliquid DEX
 * Fuente: Datos on-chain reales (gratuito)
 *
 * Incluye validación de fiabilidad basada en:
 * - Edad de la cuenta
 * - Número de trades
 * - Diversificación
 * - Dependencia de trades individuales
 */

import { supabase } from '../lib/supabase';

const EDGE_FUNCTION_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/fetch-hyperliquid-traders`;

export interface HyperliquidTraderMetrics {
  roi_pct: number;
  pnl: number;
  win_rate_pct: number;
  copiers: number;
  aum: number;
  drawdown_pct: number;
  volume: number;
}

export interface TraderValidationMetrics {
  accountAge: number; // días desde primer trade
  totalTrades: number;
  winRate: number;
  avgTradeSize: number;
  largestWinPct: number; // % del PnL del mayor trade
  diversification: number; // coins distintos
}

export interface CoinPerformance {
  coin: string;
  pnl: number;
  trades: number;
  winRate: number;
}

export interface TraderValidation {
  address: string;
  isReliable: boolean;
  reasons: string[];
  metrics: TraderValidationMetrics;
  topCoins?: CoinPerformance[];
}

export interface HyperliquidTrader {
  id: string;
  display_name: string;
  platform_uid: string;
  profile_url: string;
  platform: 'hyperliquid';
  rank?: number;
  metrics: HyperliquidTraderMetrics;
  validation?: TraderValidation;
  is_reliable?: boolean;
}

export interface FetchOptions {
  limit?: number;
  validate?: boolean; // Obtener métricas de validación (más lento)
  minPnl?: number; // PnL mínimo en USD
  minRoi?: number; // ROI mínimo (ej: 0.1 = 10%)
  onlyReliable?: boolean; // Solo traders que pasan validación
}

/**
 * Obtiene traders del leaderboard de Hyperliquid
 */
export async function fetchHyperliquidTraders(
  options: FetchOptions = {},
): Promise<HyperliquidTrader[]> {
  const { limit = 20, validate = false, minPnl = 0, minRoi = 0, onlyReliable = false } = options;

  const params = new URLSearchParams({
    limit: limit.toString(),
    validate: validate.toString(),
    minPnl: minPnl.toString(),
    minRoi: minRoi.toString(),
  });

  const response = await fetch(`${EDGE_FUNCTION_URL}?${params}`);
  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Error al obtener traders de Hyperliquid');
  }

  let traders: HyperliquidTrader[] = data.traders;

  // Filtrar solo confiables si se solicita
  if (onlyReliable && validate) {
    traders = traders.filter((t) => t.is_reliable);
  }

  return traders;
}

/**
 * Obtiene traders validados (con métricas de fiabilidad)
 * Wrapper conveniente para fetchHyperliquidTraders con validate=true
 */
export async function fetchValidatedTraders(
  limit: number = 20,
  onlyReliable: boolean = true,
): Promise<HyperliquidTrader[]> {
  return fetchHyperliquidTraders({
    limit,
    validate: true,
    onlyReliable,
  });
}

/**
 * Sincroniza traders de Hyperliquid con Supabase
 */
export async function syncHyperliquidTraders(
  options: FetchOptions = { limit: 20, validate: true },
): Promise<{ created: number; updated: number; traders: HyperliquidTrader[] }> {
  const hlTraders = await fetchHyperliquidTraders(options);

  let created = 0;
  let updated = 0;
  const now = new Date().toISOString();

  for (const trader of hlTraders) {
    // Verificar si ya existe (por platform_uid guardado en binance_uid field)
    const { data: existing } = await supabase
      .from('traders')
      .select('id')
      .eq('binance_uid', trader.platform_uid)
      .single();

    // Mapear metricas de Hyperliquid al formato de la base de datos
    const metricsToSave = {
      roi_30d_pct: trader.metrics.roi_pct,
      roi_90d_pct: trader.metrics.roi_pct,
      max_drawdown_pct: trader.metrics.drawdown_pct,
      win_rate_pct: trader.metrics.win_rate_pct,
      avg_leverage: 0,
      copiers: trader.metrics.copiers,
      days_active: trader.validation?.metrics.accountAge || 0,
      pnl: trader.metrics.pnl,
      aum:
        typeof trader.metrics.aum === 'string'
          ? parseFloat(trader.metrics.aum)
          : trader.metrics.aum,
      volume: trader.metrics.volume,
      platform: 'hyperliquid',
      // Datos de validación adicionales
      total_trades: trader.validation?.metrics.totalTrades || 0,
      diversification: trader.validation?.metrics.diversification || 0,
      largest_win_pct: trader.validation?.metrics.largestWinPct || 0,
      is_reliable: trader.is_reliable || false,
      validation_reasons: trader.validation?.reasons || [],
      // Mejores monedas del trader
      top_coins: trader.validation?.topCoins || [],
    };

    if (existing) {
      await supabase
        .from('traders')
        .update({
          display_name: trader.display_name,
          binance_profile_url: trader.profile_url,
          latest_metrics: metricsToSave,
          metrics_updated_at: now,
          updated_at: now,
        })
        .eq('binance_uid', trader.platform_uid);
      updated++;
    } else {
      await supabase.from('traders').insert({
        display_name: trader.display_name,
        binance_uid: trader.platform_uid,
        binance_profile_url: trader.profile_url,
        latest_metrics: metricsToSave,
        metrics_updated_at: now,
        trading_style: 'mixed',
        is_active: true,
      });
      created++;
    }
  }

  return { created, updated, traders: hlTraders };
}

/**
 * Obtiene detalles de un trader específico por su dirección
 */
export async function getTraderDetails(address: string): Promise<HyperliquidTrader | null> {
  const traders = await fetchHyperliquidTraders({
    limit: 100,
    validate: true,
  });

  return traders.find((t) => t.platform_uid.toLowerCase() === address.toLowerCase()) || null;
}
