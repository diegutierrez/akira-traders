/**
 * Servicio de evaluaciones usando Supabase directo
 */

import { supabase } from '../lib/supabase';

// ============================================
// TIPOS
// ============================================

export interface TraderMetrics {
  roi_30d_pct?: number;
  roi_90d_pct?: number;
  max_drawdown_pct?: number;
  win_rate_pct?: number;
  avg_leverage?: number;
  copiers?: number;
  days_active?: number;
}

export interface Trader {
  id: string;
  display_name: string;
  binance_uid?: string;
  binance_profile_url?: string;
  trading_style?: 'scalping' | 'swing' | 'trend-following' | 'arbitrage' | 'mixed';
  notes?: string;
  tags?: string[];
  is_active: boolean;
  latest_metrics?: TraderMetrics;
  metrics_updated_at?: string;
  created_at: string;
  updated_at: string;
}

export interface EvaluationMetrics {
  roi_30d_pct: number;
  roi_90d_pct: number;
  roi_180d_pct?: number | null;
  max_drawdown_pct: number;
  win_rate_pct: number;
  avg_leverage: number;
  copiers: number;
  days_active?: number;
}

export interface SelectionCriteria {
  roi_90d_range_pct: [number, number];
  max_drawdown_pct_lte: number;
  win_rate_pct_gte: number;
  min_days_active: number;
  leverage_range: [number, number];
  min_copiers: number;
}

export interface CopySettings {
  copy_mode: 'fixed' | 'ratio';
  order_size_usdt: number;
  daily_loss_cap_pct: number;
  stop_copy_drawdown_pct: number;
  assets_whitelist?: string[];
}

export interface Evaluation {
  id: string;
  created_at: string;
  updated_at: string;
  user_id: string;
  trader_id: string;
  evaluated_at: string;
  risk_profile: 'conservative' | 'moderate' | 'aggressive';
  selection_criteria: SelectionCriteria;
  metrics: EvaluationMetrics;
  copy_settings: CopySettings;
  decision?: 'approved' | 'rejected' | 'watchlist';
  total_score?: number;
  notes?: string;
}

export interface EvaluationSummary {
  id: string;
  created_at: string;
  evaluated_at: string;
  trader_id: string;
  trader_name: string;
  trading_style: string;
  binance_profile_url: string;
  trader_tags: string[];
  risk_profile: string;
  decision: string;
  total_score: number;
  roi_30d: number;
  roi_90d: number;
  roi_180d: number | null;
  max_drawdown: number;
  win_rate: number;
  avg_leverage: number;
  copiers: number;
  copy_mode: string;
  order_size_usdt: number;
  notes: string;
}

export type RiskProfile = 'conservative' | 'moderate' | 'aggressive';

// ============================================
// TRADERS
// ============================================

/**
 * Busca o crea un trader por nombre
 */
export async function findOrCreateTrader(
  displayName: string,
  binanceUrl?: string,
  style?: string
): Promise<string> {
  const { data, error } = await supabase.rpc('find_or_create_trader', {
    p_display_name: displayName,
    p_binance_url: binanceUrl || null,
    p_style: style || null,
  });

  if (error) {
    console.error('Error finding/creating trader:', error);
    throw error;
  }

  return data;
}

/**
 * Obtiene todos los traders
 */
export async function getAllTraders(): Promise<Trader[]> {
  const { data, error } = await supabase
    .from('traders')
    .select('*')
    .eq('is_active', true)
    .order('display_name');

  if (error) {
    console.error('Error fetching traders:', error);
    throw error;
  }

  return data || [];
}

/**
 * Busca traders por nombre
 */
export async function searchTraders(query: string): Promise<Trader[]> {
  const { data, error } = await supabase
    .from('traders')
    .select('*')
    .ilike('display_name', `%${query}%`)
    .eq('is_active', true)
    .limit(10);

  if (error) {
    console.error('Error searching traders:', error);
    throw error;
  }

  return data || [];
}

// ============================================
// EVALUATIONS
// ============================================

/**
 * Obtiene todas las evaluaciones del usuario (usando la vista)
 */
export async function getAllEvaluations(): Promise<EvaluationSummary[]> {
  const { data, error } = await supabase
    .from('v_evaluations_summary')
    .select('*')
    .order('evaluated_at', { ascending: false });

  if (error) {
    console.error('Error fetching evaluations:', error);
    throw error;
  }

  return data || [];
}

/**
 * Obtiene una evaluación por ID
 */
export async function getEvaluationById(id: string): Promise<Evaluation | null> {
  const { data, error } = await supabase
    .from('evaluations')
    .select('*')
    .eq('id', id)
    .single();

  if (error) {
    console.error('Error fetching evaluation:', error);
    throw error;
  }

  return data;
}

/**
 * Obtiene criterios por defecto según perfil de riesgo
 */
export async function getDefaultCriteria(riskProfile: RiskProfile): Promise<SelectionCriteria> {
  const { data, error } = await supabase.rpc('get_default_criteria', {
    p_risk_profile: riskProfile,
  });

  if (error) {
    console.error('Error fetching default criteria:', error);
    throw error;
  }

  return data;
}

/**
 * Crea una nueva evaluación
 */
export async function createEvaluation(params: {
  traderName: string;
  binanceUrl?: string;
  tradingStyle?: string;
  riskProfile: RiskProfile;
  selectionCriteria: SelectionCriteria;
  metrics: EvaluationMetrics;
  copySettings: CopySettings;
  decision?: 'approved' | 'rejected' | 'watchlist';
  notes?: string;
}): Promise<Evaluation> {
  // Primero buscar o crear el trader
  const traderId = await findOrCreateTrader(
    params.traderName,
    params.binanceUrl,
    params.tradingStyle
  );

  // Obtener el usuario actual
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    throw new Error('Usuario no autenticado');
  }

  // Crear la evaluación
  const { data, error } = await supabase
    .from('evaluations')
    .insert({
      user_id: user.id,
      trader_id: traderId,
      risk_profile: params.riskProfile,
      selection_criteria: params.selectionCriteria,
      metrics: params.metrics,
      copy_settings: params.copySettings,
      decision: params.decision,
      notes: params.notes,
    })
    .select()
    .single();

  if (error) {
    console.error('Error creating evaluation:', error);
    throw error;
  }

  return data;
}

/**
 * Actualiza una evaluación existente
 */
export async function updateEvaluation(
  id: string,
  updates: Partial<{
    risk_profile: RiskProfile;
    selection_criteria: SelectionCriteria;
    metrics: EvaluationMetrics;
    copy_settings: CopySettings;
    decision: 'approved' | 'rejected' | 'watchlist';
    notes: string;
  }>
): Promise<Evaluation> {
  const { data, error } = await supabase
    .from('evaluations')
    .update(updates)
    .eq('id', id)
    .select()
    .single();

  if (error) {
    console.error('Error updating evaluation:', error);
    throw error;
  }

  return data;
}

/**
 * Elimina una evaluación
 */
export async function deleteEvaluation(id: string): Promise<void> {
  const { error } = await supabase
    .from('evaluations')
    .delete()
    .eq('id', id);

  if (error) {
    console.error('Error deleting evaluation:', error);
    throw error;
  }
}

/**
 * Calcula el score de una evaluación (usando la función de Supabase)
 */
export async function calculateScore(
  metrics: EvaluationMetrics,
  criteria: SelectionCriteria
): Promise<number> {
  const { data, error } = await supabase.rpc('calculate_evaluation_score', {
    p_metrics: metrics,
    p_criteria: criteria,
  });

  if (error) {
    console.error('Error calculating score:', error);
    throw error;
  }

  return data;
}
