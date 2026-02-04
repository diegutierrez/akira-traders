import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { z } from 'zod';
import { RISK_PROFILE_DEFAULTS, RISK_PROFILE_LABELS, TRADING_STYLE_LABELS, COPY_MODE_LABELS } from '../constants/riskProfiles';
import { FormInput, FormSelect, FormSection, FormTextarea } from '../components/forms';
import { createEvaluation, type RiskProfile } from '../services/evaluations';

const COMMON_ASSETS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC'];

// Schema de validación
const formSchema = z.object({
  // Trader info
  trader_name: z.string().min(1, 'Nombre requerido'),
  binance_url: z.string().url('URL inválida').optional().or(z.literal('')),
  trading_style: z.enum(['scalping', 'swing', 'trend-following', 'arbitrage', 'mixed']),

  // Evaluation context
  risk_profile: z.enum(['conservative', 'moderate', 'aggressive']),

  // Selection criteria
  roi_90d_min: z.number(),
  roi_90d_max: z.number(),
  max_drawdown_pct_lte: z.number().min(0).max(100),
  win_rate_pct_gte: z.number().min(0).max(100),
  min_days_active: z.number().min(1),
  leverage_min: z.number().min(1),
  leverage_max: z.number().max(125),
  min_copiers: z.number().min(0),

  // Metrics
  roi_30d_pct: z.number(),
  roi_90d_pct: z.number(),
  roi_180d_pct: z.number().optional(),
  max_drawdown_pct: z.number().min(0),
  win_rate_pct: z.number().min(0).max(100),
  avg_leverage: z.number().min(1),
  copiers: z.number().min(0),
  days_active: z.number().min(0).optional(),

  // Copy settings
  copy_mode: z.enum(['fixed', 'ratio']),
  order_size_usdt: z.number().min(10, 'Mínimo 10 USDT'),
  daily_loss_cap_pct: z.number().min(0).max(100),
  stop_copy_drawdown_pct: z.number().min(0).max(100),

  // Decision
  decision: z.enum(['approved', 'rejected', 'watchlist']).optional(),

  // Notes
  notes: z.string().optional(),
});

type FormData = z.infer<typeof formSchema>;

export function NewEvaluation() {
  const navigate = useNavigate();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [selectedAssets, setSelectedAssets] = useState<string[]>([]);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      trading_style: 'swing',
      risk_profile: 'moderate',
      ...flattenCriteria(RISK_PROFILE_DEFAULTS.moderate),
      roi_30d_pct: 0,
      roi_90d_pct: 0,
      max_drawdown_pct: 0,
      win_rate_pct: 0,
      avg_leverage: 1,
      copiers: 0,
      copy_mode: 'fixed',
      order_size_usdt: 50,
      daily_loss_cap_pct: 5,
      stop_copy_drawdown_pct: 15,
    },
  });

  const riskProfile = watch('risk_profile');

  // Auto-completar criterios según perfil de riesgo
  useEffect(() => {
    if (riskProfile && RISK_PROFILE_DEFAULTS[riskProfile as RiskProfile]) {
      const defaults = RISK_PROFILE_DEFAULTS[riskProfile as RiskProfile];
      const flat = flattenCriteria(defaults);
      Object.entries(flat).forEach(([key, value]) => {
        setValue(key as keyof FormData, value);
      });
    }
  }, [riskProfile, setValue]);

  function flattenCriteria(criteria: typeof RISK_PROFILE_DEFAULTS.moderate) {
    return {
      roi_90d_min: criteria.roi_90d_range_pct[0],
      roi_90d_max: criteria.roi_90d_range_pct[1],
      max_drawdown_pct_lte: criteria.max_drawdown_pct_lte,
      win_rate_pct_gte: criteria.win_rate_pct_gte,
      min_days_active: criteria.min_days_active,
      leverage_min: criteria.leverage_range[0],
      leverage_max: criteria.leverage_range[1],
      min_copiers: criteria.min_copiers,
    };
  }

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    try {
      await createEvaluation({
        traderName: data.trader_name,
        binanceUrl: data.binance_url || undefined,
        tradingStyle: data.trading_style,
        riskProfile: data.risk_profile,
        selectionCriteria: {
          roi_90d_range_pct: [data.roi_90d_min, data.roi_90d_max],
          max_drawdown_pct_lte: data.max_drawdown_pct_lte,
          win_rate_pct_gte: data.win_rate_pct_gte,
          min_days_active: data.min_days_active,
          leverage_range: [data.leverage_min, data.leverage_max],
          min_copiers: data.min_copiers,
        },
        metrics: {
          roi_30d_pct: data.roi_30d_pct,
          roi_90d_pct: data.roi_90d_pct,
          roi_180d_pct: data.roi_180d_pct,
          max_drawdown_pct: data.max_drawdown_pct,
          win_rate_pct: data.win_rate_pct,
          avg_leverage: data.avg_leverage,
          copiers: data.copiers,
          days_active: data.days_active,
        },
        copySettings: {
          copy_mode: data.copy_mode,
          order_size_usdt: data.order_size_usdt,
          daily_loss_cap_pct: data.daily_loss_cap_pct,
          stop_copy_drawdown_pct: data.stop_copy_drawdown_pct,
          assets_whitelist: selectedAssets.length > 0 ? selectedAssets : undefined,
        },
        decision: data.decision,
        notes: data.notes,
      });

      toast.success('Evaluación creada exitosamente');
      navigate('/traders');
    } catch (error) {
      console.error(error);
      toast.error('Error al crear la evaluación');
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleAsset = (asset: string) => {
    setSelectedAssets(prev =>
      prev.includes(asset)
        ? prev.filter(a => a !== asset)
        : [...prev, asset]
    );
  };

  return (
    <div className="py-8 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold text-text-primary mb-8">
        Nueva Evaluación
      </h1>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Información del Trader */}
        <FormSection title="Información del Trader" description="Datos del trader a evaluar">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormInput
              label="Nombre del Trader"
              {...register('trader_name')}
              error={errors.trader_name?.message}
              placeholder="Ej: CryptoMaster123"
              required
            />
            <FormInput
              label="URL Perfil Binance"
              {...register('binance_url')}
              error={errors.binance_url?.message}
              placeholder="https://www.binance.com/es/copy-trading/..."
            />
            <FormSelect
              label="Estilo de Trading"
              options={Object.entries(TRADING_STYLE_LABELS).map(([value, label]) => ({
                value,
                label,
              }))}
              {...register('trading_style')}
              error={errors.trading_style?.message}
              required
            />
            <FormSelect
              label="Perfil de Riesgo"
              options={Object.entries(RISK_PROFILE_LABELS).map(([value, label]) => ({
                value,
                label,
              }))}
              {...register('risk_profile')}
              error={errors.risk_profile?.message}
              required
            />
          </div>
        </FormSection>

        {/* Criterios de Selección */}
        <FormSection
          title="Criterios de Selección"
          description="Se auto-completan según el perfil de riesgo"
        >
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-text-secondary">
                ROI 90d Rango (%)
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary"
                  {...register('roi_90d_min', { valueAsNumber: true })}
                  placeholder="Min"
                />
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary"
                  {...register('roi_90d_max', { valueAsNumber: true })}
                  placeholder="Max"
                />
              </div>
            </div>
            <FormInput
              label="Max Drawdown (%)"
              type="number"
              step="0.1"
              {...register('max_drawdown_pct_lte', { valueAsNumber: true })}
              error={errors.max_drawdown_pct_lte?.message}
            />
            <FormInput
              label="Win Rate Mínimo (%)"
              type="number"
              step="0.1"
              {...register('win_rate_pct_gte', { valueAsNumber: true })}
              error={errors.win_rate_pct_gte?.message}
            />
            <FormInput
              label="Días Activo Mínimo"
              type="number"
              {...register('min_days_active', { valueAsNumber: true })}
              error={errors.min_days_active?.message}
            />
            <div className="space-y-1">
              <label className="block text-sm font-medium text-text-secondary">
                Rango Leverage
              </label>
              <div className="flex gap-2">
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary"
                  {...register('leverage_min', { valueAsNumber: true })}
                  placeholder="Min"
                />
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary"
                  {...register('leverage_max', { valueAsNumber: true })}
                  placeholder="Max"
                />
              </div>
            </div>
            <FormInput
              label="Copiadores Mínimo"
              type="number"
              {...register('min_copiers', { valueAsNumber: true })}
              error={errors.min_copiers?.message}
            />
          </div>
        </FormSection>

        {/* Métricas del Trader */}
        <FormSection title="Métricas del Trader" description="Datos de rendimiento actuales">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <FormInput
              label="ROI 30 días (%)"
              type="number"
              step="0.01"
              {...register('roi_30d_pct', { valueAsNumber: true })}
              error={errors.roi_30d_pct?.message}
              required
            />
            <FormInput
              label="ROI 90 días (%)"
              type="number"
              step="0.01"
              {...register('roi_90d_pct', { valueAsNumber: true })}
              error={errors.roi_90d_pct?.message}
              required
            />
            <FormInput
              label="ROI 180 días (%)"
              type="number"
              step="0.01"
              {...register('roi_180d_pct', { valueAsNumber: true })}
              hint="Opcional"
            />
            <FormInput
              label="Max Drawdown (%)"
              type="number"
              step="0.01"
              {...register('max_drawdown_pct', { valueAsNumber: true })}
              error={errors.max_drawdown_pct?.message}
              required
            />
            <FormInput
              label="Win Rate (%)"
              type="number"
              step="0.01"
              {...register('win_rate_pct', { valueAsNumber: true })}
              error={errors.win_rate_pct?.message}
              required
            />
            <FormInput
              label="Leverage Promedio"
              type="number"
              step="0.1"
              {...register('avg_leverage', { valueAsNumber: true })}
              error={errors.avg_leverage?.message}
              required
            />
            <FormInput
              label="Copiadores"
              type="number"
              {...register('copiers', { valueAsNumber: true })}
              error={errors.copiers?.message}
              required
            />
            <FormInput
              label="Días Activo"
              type="number"
              {...register('days_active', { valueAsNumber: true })}
              hint="Opcional"
            />
          </div>
        </FormSection>

        {/* Configuración de Copia */}
        <FormSection title="Configuración de Copia" description="Parámetros recomendados para copiar">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <FormSelect
              label="Modo de Copia"
              options={Object.entries(COPY_MODE_LABELS).map(([value, label]) => ({
                value,
                label,
              }))}
              {...register('copy_mode')}
              error={errors.copy_mode?.message}
              required
            />
            <FormInput
              label="Tamaño Orden (USDT)"
              type="number"
              step="1"
              {...register('order_size_usdt', { valueAsNumber: true })}
              error={errors.order_size_usdt?.message}
              hint="Mínimo 10 USDT"
              required
            />
            <FormInput
              label="Cap Pérdida Diaria (%)"
              type="number"
              step="0.1"
              {...register('daily_loss_cap_pct', { valueAsNumber: true })}
              error={errors.daily_loss_cap_pct?.message}
              required
            />
            <FormInput
              label="Stop Copy Drawdown (%)"
              type="number"
              step="0.1"
              {...register('stop_copy_drawdown_pct', { valueAsNumber: true })}
              error={errors.stop_copy_drawdown_pct?.message}
              required
            />
          </div>
        </FormSection>

        {/* Assets */}
        <FormSection title="Activos Permitidos" description="Opcional - Activos que opera el trader">
          <div className="flex flex-wrap gap-2">
            {COMMON_ASSETS.map(asset => (
              <button
                key={asset}
                type="button"
                onClick={() => toggleAsset(asset)}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  selectedAssets.includes(asset)
                    ? 'bg-primary text-bg-primary'
                    : 'bg-bg-tertiary text-text-secondary hover:bg-bg-secondary'
                }`}
              >
                {asset}
              </button>
            ))}
          </div>
          {selectedAssets.length > 0 && (
            <p className="text-sm text-text-tertiary">
              Seleccionados: {selectedAssets.join(', ')}
            </p>
          )}
        </FormSection>

        {/* Decisión */}
        <FormSection title="Decisión" description="Resultado de la evaluación">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormSelect
              label="Decisión"
              options={[
                { value: 'approved', label: 'Aprobado - Copiar' },
                { value: 'watchlist', label: 'Watchlist - Monitorear' },
                { value: 'rejected', label: 'Rechazado - No copiar' },
              ]}
              {...register('decision')}
              hint="Opcional - El score se calcula automáticamente"
            />
          </div>
        </FormSection>

        {/* Notas */}
        <FormSection title="Notas" description="Observaciones adicionales">
          <FormTextarea
            label="Notas"
            {...register('notes')}
            placeholder="Observaciones sobre el trader, estrategia, condiciones de mercado..."
            hint="Opcional"
          />
        </FormSection>

        {/* Botones */}
        <div className="flex gap-4 pt-4 border-t border-border">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="px-6 py-2 bg-bg-tertiary text-text-secondary rounded-lg hover:bg-bg-secondary transition-colors"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            className="px-6 py-2 bg-primary text-bg-primary font-semibold rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? 'Guardando...' : 'Guardar Evaluación'}
          </button>
        </div>
      </form>
    </div>
  );
}
