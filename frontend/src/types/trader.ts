/**
 * Tipos TypeScript basados en los schemas de evaluación de traders
 */

export type RiskProfile = 'conservative' | 'moderate' | 'aggressive';

export type TradingStyle = 'scalping' | 'swing' | 'trend-following' | 'arbitrage' | 'mixed';

export type CopyMode = 'fixed' | 'ratio';

export interface TraderMetrics {
  roi_30d_pct: number;
  roi_90d_pct: number;
  roi_180d_pct?: number | null;
  max_drawdown_pct: number;
  win_rate_pct: number;
  avg_leverage: number;
  copiers: number;
}

export interface SelectionCriteria {
  roi_90d_range_pct: [number, number];
  max_drawdown_pct_lte: number;
  win_rate_pct_gte: number;
  min_days_active: number;
  leverage_range: [number, number];
  min_copiers: number;
}

export interface TraderCandidate {
  display_name: string;
  binance_profile_url: string;
  metrics: TraderMetrics;
  style: TradingStyle;
  assets_whitelist?: string[];
  copy_mode_suggestion: CopyMode;
  order_size_suggestion_usdt: number;
  daily_loss_cap_pct: number;
  stop_copy_drawdown_pct: number;
  notes?: string;
}

export interface TraderEvaluation {
  as_of_utc: string;
  risk_profile: RiskProfile;
  selection_criteria: SelectionCriteria;
  candidate: TraderCandidate;
  _source_file?: string;
}

export interface TraderScores {
  drawdown_score: number;
  win_rate_score: number;
  roi_score: number;
  consistency_score: number;
  rar_score: number;
  total_score: number;
}

export interface TraderAnalysis {
  trader: string;
  risk_profile: RiskProfile;
  total_score: number;
  classification: string;
  recommendation: string;
  scores: TraderScores;
  metrics: {
    roi_90d: number;
    max_drawdown: number;
    win_rate: number;
    avg_leverage: number;
    copiers?: number;
  };
  source_file?: string;
}

export interface PortfolioMetrics {
  portfolio_roi_90d: number;
  portfolio_max_dd: number;
  portfolio_win_rate: number;
  portfolio_avg_leverage: number;
  num_traders: number;
}

export interface ConsolidatedReport {
  report_metadata: {
    generated_at: string;
    total_evaluations: number;
    risk_profiles: RiskProfile[];
    filter_applied?: RiskProfile | null;
  };
  summary_statistics: {
    total_traders: number;
    roi_90d: StatsSummary;
    max_drawdown: StatsSummary;
    win_rate: StatsSummary;
    avg_leverage: StatsSummary;
    copiers: StatsSummary;
  };
  traders_ranking: TraderAnalysis[];
  by_risk_profile: Record<
    RiskProfile,
    {
      count: number;
      statistics: Record<string, StatsSummary>;
    }
  >;
}

export interface StatsSummary {
  min: number;
  max: number;
  avg: number;
  median: number;
}

export interface ValidationError {
  field: string;
  message: string;
  severity: 'error' | 'warning';
}

export interface ValidationResult {
  valid: boolean;
  errors: ValidationError[];
  warnings: ValidationError[];
}
