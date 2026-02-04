/**
 * Servicio para obtener datos de traders de Bybit Copy Trading
 */

import { supabase } from '../lib/supabase';

const EDGE_FUNCTION_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/fetch-bybit-traders`;

export interface BybitTraderMetrics {
  roi_pct: number;
  pnl: number;
  win_rate_pct: number;
  copiers: number;
  aum: number;
  drawdown_pct: number;
}

export interface BybitTrader {
  id: string;
  display_name: string;
  platform_uid: string;
  profile_url: string;
  platform: 'bybit';
  metrics: BybitTraderMetrics;
}

/**
 * Obtiene traders del leaderboard de Bybit
 */
export async function fetchBybitTraders(
  limit: number = 20
): Promise<BybitTrader[]> {
  const response = await fetch(`${EDGE_FUNCTION_URL}?limit=${limit}`);

  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Error al obtener traders de Bybit');
  }

  return data.traders;
}

/**
 * Sincroniza traders de Bybit con Supabase
 */
export async function syncBybitTraders(
  limit: number = 20
): Promise<{ created: number; updated: number; traders: BybitTrader[] }> {
  const bybitTraders = await fetchBybitTraders(limit);

  let created = 0;
  let updated = 0;
  const now = new Date().toISOString();

  for (const trader of bybitTraders) {
    // Verificar si ya existe (por platform_uid guardado en binance_uid field)
    const { data: existing } = await supabase
      .from('traders')
      .select('id')
      .eq('binance_uid', trader.platform_uid)
      .single();

    // Mapear metricas de Bybit al formato de la base de datos
    const metricsToSave = {
      roi_30d_pct: trader.metrics.roi_pct,
      roi_90d_pct: trader.metrics.roi_pct,
      max_drawdown_pct: trader.metrics.drawdown_pct,
      win_rate_pct: trader.metrics.win_rate_pct,
      avg_leverage: 0,
      copiers: trader.metrics.copiers,
      days_active: 0,
      pnl: trader.metrics.pnl,
      aum: trader.metrics.aum,
      platform: 'bybit',
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
      await supabase
        .from('traders')
        .insert({
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

  return { created, updated, traders: bybitTraders };
}
