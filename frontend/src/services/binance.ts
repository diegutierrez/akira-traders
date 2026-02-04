/**
 * Servicio para obtener datos de traders de Binance Copy Trading
 */

import { supabase } from '../lib/supabase';

const EDGE_FUNCTION_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/fetch-binance-traders`;

export interface BinanceTraderMetrics {
  roi_30d_pct: number;
  roi_90d_pct: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  avg_leverage: number;
  copiers: number;
  days_active: number;
}

export interface BinanceTrader {
  id: string;
  display_name: string;
  binance_uid: string;
  binance_profile_url: string;
  metrics: BinanceTraderMetrics;
}

export type PeriodType = 'SEVEN_DAYS' | 'THIRTY_DAYS' | 'NINETY_DAYS';

/**
 * Obtiene traders del ranking de Binance Copy Trading
 */
export async function fetchBinanceTraders(
  period: PeriodType = 'THIRTY_DAYS',
  limit: number = 20
): Promise<BinanceTrader[]> {
  const response = await fetch(`${EDGE_FUNCTION_URL}?period=${period}&limit=${limit}`);

  if (!response.ok) {
    throw new Error(`Error fetching traders: ${response.status}`);
  }

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Error desconocido');
  }

  return data.traders;
}

/**
 * Sincroniza traders de Binance con Supabase
 * - Crea nuevos traders si no existen
 * - Actualiza existentes
 * - Guarda las métricas en la base de datos
 */
export async function syncBinanceTraders(
  period: PeriodType = 'THIRTY_DAYS',
  limit: number = 20
): Promise<{ created: number; updated: number; traders: BinanceTrader[] }> {
  // Obtener traders de Binance
  const binanceTraders = await fetchBinanceTraders(period, limit);

  let created = 0;
  let updated = 0;
  const now = new Date().toISOString();

  for (const trader of binanceTraders) {
    // Verificar si ya existe
    const { data: existing } = await supabase
      .from('traders')
      .select('id')
      .eq('binance_uid', trader.binance_uid)
      .single();

    if (existing) {
      // Actualizar con métricas
      await supabase
        .from('traders')
        .update({
          display_name: trader.display_name,
          binance_profile_url: trader.binance_profile_url,
          latest_metrics: trader.metrics,
          metrics_updated_at: now,
          updated_at: now,
        })
        .eq('binance_uid', trader.binance_uid);
      updated++;
    } else {
      // Crear nuevo con métricas
      await supabase
        .from('traders')
        .insert({
          display_name: trader.display_name,
          binance_uid: trader.binance_uid,
          binance_profile_url: trader.binance_profile_url,
          latest_metrics: trader.metrics,
          metrics_updated_at: now,
          trading_style: 'mixed',
          is_active: true,
        });
      created++;
    }
  }

  return { created, updated, traders: binanceTraders };
}

/**
 * Obtiene un trader por URL de Binance
 */
export async function fetchTraderByUrl(binanceUrl: string): Promise<BinanceTrader | null> {
  const EDGE_FUNCTION_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/fetch-trader-profile`;

  const response = await fetch(`${EDGE_FUNCTION_URL}?url=${encodeURIComponent(binanceUrl)}`);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.error || 'Error al obtener datos del trader');
  }

  const data = await response.json();

  if (!data.success || !data.trader) {
    throw new Error(data.error || 'No se encontró el trader');
  }

  return {
    id: data.trader.binance_uid,
    display_name: data.trader.display_name,
    binance_uid: data.trader.binance_uid,
    binance_profile_url: data.trader.binance_profile_url,
    metrics: data.trader.metrics,
  };
}

/**
 * Agrega un trader por URL de Binance y lo guarda en Supabase
 */
export async function addTraderByUrl(binanceUrl: string): Promise<{ trader: BinanceTrader; isNew: boolean }> {
  // Obtener datos del trader
  const traderData = await fetchTraderByUrl(binanceUrl);

  if (!traderData) {
    throw new Error('No se pudieron obtener los datos del trader');
  }

  const now = new Date().toISOString();

  // Verificar si ya existe
  const { data: existing } = await supabase
    .from('traders')
    .select('id')
    .eq('binance_uid', traderData.binance_uid)
    .single();

  if (existing) {
    // Actualizar
    await supabase
      .from('traders')
      .update({
        display_name: traderData.display_name,
        binance_profile_url: traderData.binance_profile_url,
        latest_metrics: traderData.metrics,
        metrics_updated_at: now,
        updated_at: now,
      })
      .eq('binance_uid', traderData.binance_uid);

    return { trader: traderData, isNew: false };
  } else {
    // Crear nuevo
    await supabase
      .from('traders')
      .insert({
        display_name: traderData.display_name,
        binance_uid: traderData.binance_uid,
        binance_profile_url: traderData.binance_profile_url,
        latest_metrics: traderData.metrics,
        metrics_updated_at: now,
        trading_style: 'mixed',
        is_active: true,
      });

    return { trader: traderData, isNew: true };
  }
}
