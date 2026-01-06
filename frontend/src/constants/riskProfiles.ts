import type { SelectionCriteria, RiskProfile } from '../types/trader';

export const RISK_PROFILE_DEFAULTS: Record<RiskProfile, SelectionCriteria> = {
  conservative: {
    roi_90d_range_pct: [10, 30],
    max_drawdown_pct_lte: 10,
    win_rate_pct_gte: 60,
    min_days_active: 90,
    leverage_range: [1, 2],
    min_copiers: 100,
  },
  moderate: {
    roi_90d_range_pct: [20, 60],
    max_drawdown_pct_lte: 20,
    win_rate_pct_gte: 55,
    min_days_active: 60,
    leverage_range: [1, 3],
    min_copiers: 50,
  },
  aggressive: {
    roi_90d_range_pct: [40, 200],
    max_drawdown_pct_lte: 35,
    win_rate_pct_gte: 50,
    min_days_active: 30,
    leverage_range: [1, 5],
    min_copiers: 20,
  },
};

export const RISK_PROFILE_LABELS: Record<RiskProfile, string> = {
  conservative: 'Conservador',
  moderate: 'Moderado',
  aggressive: 'Agresivo',
};

export const TRADING_STYLE_LABELS: Record<string, string> = {
  scalping: 'Scalping',
  swing: 'Swing',
  'trend-following': 'Trend Following',
  arbitrage: 'Arbitraje',
  mixed: 'Mixto',
};

export const COPY_MODE_LABELS: Record<string, string> = {
  fixed: 'Fijo (USDT)',
  ratio: 'Proporcional (%)',
};
