import { z } from 'zod';

export const riskProfileSchema = z.enum(['conservative', 'moderate', 'aggressive']);
export const tradingStyleSchema = z.enum([
  'scalping',
  'swing',
  'trend-following',
  'arbitrage',
  'mixed',
]);
export const copyModeSchema = z.enum(['fixed', 'ratio']);

export const selectionCriteriaSchema = z.object({
  roi_90d_range_pct: z.tuple([z.number(), z.number()]),
  max_drawdown_pct_lte: z.number().min(0).max(100),
  win_rate_pct_gte: z.number().min(0).max(100),
  min_days_active: z.number().min(1),
  leverage_range: z.tuple([z.number().min(1), z.number().max(125)]),
  min_copiers: z.number().min(0),
});

export const traderMetricsSchema = z.object({
  roi_30d_pct: z.number(),
  roi_90d_pct: z.number(),
  roi_180d_pct: z.number().nullable().optional(),
  max_drawdown_pct: z.number().min(0),
  win_rate_pct: z.number().min(0).max(100),
  avg_leverage: z.number().min(1),
  copiers: z.number().min(0),
});

export const traderCandidateSchema = z.object({
  display_name: z.string().min(1, 'Nombre requerido'),
  binance_profile_url: z
    .string()
    .url('URL inválida')
    .regex(/binance\.com/, 'Debe ser URL de Binance'),
  metrics: traderMetricsSchema,
  style: tradingStyleSchema,
  assets_whitelist: z.array(z.string()).optional(),
  copy_mode_suggestion: copyModeSchema,
  order_size_suggestion_usdt: z.number().min(10, 'Mínimo 10 USDT'),
  daily_loss_cap_pct: z.number().min(0).max(100),
  stop_copy_drawdown_pct: z.number().min(0).max(100),
  notes: z.string().optional(),
});

export const evaluationSchema = z.object({
  as_of_utc: z.string().min(1, 'Fecha requerida'),
  risk_profile: riskProfileSchema,
  selection_criteria: selectionCriteriaSchema,
  candidate: traderCandidateSchema,
});

export type EvaluationFormData = z.infer<typeof evaluationSchema>;
