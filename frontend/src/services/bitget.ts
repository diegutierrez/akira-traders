/**
 * Servicio para obtener datos de traders de Bitget Copy Trading
 */

import { supabase } from '../lib/supabase';

const EDGE_FUNCTION_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/fetch-bitget-traders`;

export interface BitgetTraderMetrics {
  roi_pct: number;
  pnl: number;
  win_rate_pct: number;
  copiers: number;
  aum: number;
  drawdown_pct: number;
}

export interface BitgetTrader {
  id: string;
  display_name: string;
  bitget_uid: string;
  profile_url: string;
  avatar_url?: string;
  metrics: BitgetTraderMetrics;
}

/**
 * Obtiene traders del leaderboard de Bitget
 */
export async function fetchBitgetTraders(
  limit: number = 20
): Promise<BitgetTrader[]> {
  const response = await fetch(`${EDGE_FUNCTION_URL}?limit=${limit}`);

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || data.suggestion || 'Error al obtener traders de Bitget');
  }

  return data.traders;
}

/**
 * Sincroniza traders de Bitget con Supabase
 */
export async function syncBitgetTraders(
  limit: number = 20
): Promise<{ created: number; updated: number; traders: BitgetTrader[] }> {
  const bitgetTraders = await fetchBitgetTraders(limit);

  let created = 0;
  let updated = 0;
  const now = new Date().toISOString();

  for (const trader of bitgetTraders) {
    // Verificar si ya existe (por bitget_uid guardado en binance_uid field)
    const { data: existing } = await supabase
      .from('traders')
      .select('id')
      .eq('binance_uid', trader.bitget_uid)
      .single();

    // Mapear métricas de Bitget al formato de la base de datos
    const metricsToSave = {
      roi_30d_pct: trader.metrics.roi_pct, // ROI general de Bitget
      roi_90d_pct: trader.metrics.roi_pct, // Usamos el mismo ya que Bitget no diferencia
      max_drawdown_pct: trader.metrics.drawdown_pct,
      win_rate_pct: trader.metrics.win_rate_pct,
      avg_leverage: 0, // Bitget no proporciona este dato
      copiers: trader.metrics.copiers,
      days_active: 0,
      // Campos adicionales de Bitget
      pnl: trader.metrics.pnl,
      aum: trader.metrics.aum,
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
        .eq('binance_uid', trader.bitget_uid);
      updated++;
    } else {
      await supabase
        .from('traders')
        .insert({
          display_name: trader.display_name,
          binance_uid: trader.bitget_uid, // Reutilizamos el campo
          binance_profile_url: trader.profile_url,
          latest_metrics: metricsToSave,
          metrics_updated_at: now,
          trading_style: 'mixed',
          is_active: true,
        });
      created++;
    }
  }

  return { created, updated, traders: bitgetTraders };
}
