import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { evaluationSchema, type EvaluationFormData } from '../schemas/evaluationSchema';
import { RISK_PROFILE_DEFAULTS, RISK_PROFILE_LABELS, TRADING_STYLE_LABELS, COPY_MODE_LABELS } from '../constants/riskProfiles';
import { FormInput, FormSelect, FormSection, FormTextarea } from '../components/forms';
import { saveEvaluation } from '../services/pythonScripts';
import type { RiskProfile } from '../types/trader';

const COMMON_ASSETS = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'MATIC'];

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
  } = useForm<EvaluationFormData>({
    resolver: zodResolver(evaluationSchema),
    defaultValues: {
      as_of_utc: new Date().toISOString().slice(0, 16),
      risk_profile: 'moderate',
      selection_criteria: RISK_PROFILE_DEFAULTS.moderate,
      candidate: {
        style: 'swing',
        copy_mode_suggestion: 'fixed',
        order_size_suggestion_usdt: 50,
        daily_loss_cap_pct: 5,
        stop_copy_drawdown_pct: 15,
        metrics: {
          roi_30d_pct: 0,
          roi_90d_pct: 0,
          roi_180d_pct: null,
          max_drawdown_pct: 0,
          win_rate_pct: 0,
          avg_leverage: 1,
          copiers: 0,
        },
      },
    },
  });

  const riskProfile = watch('risk_profile');

  useEffect(() => {
    if (riskProfile && RISK_PROFILE_DEFAULTS[riskProfile as RiskProfile]) {
      const defaults = RISK_PROFILE_DEFAULTS[riskProfile as RiskProfile];
      setValue('selection_criteria', defaults);
    }
  }, [riskProfile, setValue]);

  const onSubmit = async (data: EvaluationFormData) => {
    setIsSubmitting(true);
    try {
      const evaluationData = {
        ...data,
        as_of_utc: new Date(data.as_of_utc).toISOString(),
        candidate: {
          ...data.candidate,
          assets_whitelist: selectedAssets.length > 0 ? selectedAssets : undefined,
        },
      };

      const result = await saveEvaluation(evaluationData);

      if (result.success) {
        toast.success(`Evaluación guardada: ${result.filename}`);
        navigate('/traders');
      } else {
        toast.error(result.message || 'Error al guardar');
      }
    } catch (error) {
      toast.error('Error al guardar la evaluación');
      console.error(error);
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
        {/* Información General */}
        <FormSection title="Información General" description="Datos básicos de la evaluación">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormInput
              label="Fecha de Evaluación"
              type="datetime-local"
              {...register('as_of_utc')}
              error={errors.as_of_utc?.message}
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
          description="Se auto-completan según el perfil de riesgo seleccionado"
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
                  {...register('selection_criteria.roi_90d_range_pct.0', { valueAsNumber: true })}
                  placeholder="Min"
                />
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary"
                  {...register('selection_criteria.roi_90d_range_pct.1', { valueAsNumber: true })}
                  placeholder="Max"
                />
              </div>
            </div>
            <FormInput
              label="Max Drawdown (%)"
              type="number"
              step="0.1"
              {...register('selection_criteria.max_drawdown_pct_lte', { valueAsNumber: true })}
              error={errors.selection_criteria?.max_drawdown_pct_lte?.message}
            />
            <FormInput
              label="Win Rate Mínimo (%)"
              type="number"
              step="0.1"
              {...register('selection_criteria.win_rate_pct_gte', { valueAsNumber: true })}
              error={errors.selection_criteria?.win_rate_pct_gte?.message}
            />
            <FormInput
              label="Días Activo Mínimo"
              type="number"
              {...register('selection_criteria.min_days_active', { valueAsNumber: true })}
              error={errors.selection_criteria?.min_days_active?.message}
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
                  {...register('selection_criteria.leverage_range.0', { valueAsNumber: true })}
                  placeholder="Min"
                />
                <input
                  type="number"
                  step="0.1"
                  className="w-full px-3 py-2 bg-bg-tertiary border border-border rounded-lg text-text-primary"
                  {...register('selection_criteria.leverage_range.1', { valueAsNumber: true })}
                  placeholder="Max"
                />
              </div>
            </div>
            <FormInput
              label="Copiadores Mínimo"
              type="number"
              {...register('selection_criteria.min_copiers', { valueAsNumber: true })}
              error={errors.selection_criteria?.min_copiers?.message}
            />
          </div>
        </FormSection>

        {/* Información del Trader */}
        <FormSection title="Información del Trader" description="Datos del trader a evaluar">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <FormInput
              label="Nombre del Trader"
              {...register('candidate.display_name')}
              error={errors.candidate?.display_name?.message}
              placeholder="Ej: CryptoMaster123"
              required
            />
            <FormInput
              label="URL Perfil Binance"
              {...register('candidate.binance_profile_url')}
              error={errors.candidate?.binance_profile_url?.message}
              placeholder="https://www.binance.com/es/copy-trading/..."
              required
            />
            <FormSelect
              label="Estilo de Trading"
              options={Object.entries(TRADING_STYLE_LABELS).map(([value, label]) => ({
                value,
                label,
              }))}
              {...register('candidate.style')}
              error={errors.candidate?.style?.message}
              required
            />
          </div>
        </FormSection>

        {/* Métricas del Trader */}
        <FormSection title="Métricas del Trader" description="Datos de rendimiento actuales">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <FormInput
              label="ROI 30 días (%)"
              type="number"
              step="0.01"
              {...register('candidate.metrics.roi_30d_pct', { valueAsNumber: true })}
              error={errors.candidate?.metrics?.roi_30d_pct?.message}
              required
            />
            <FormInput
              label="ROI 90 días (%)"
              type="number"
              step="0.01"
              {...register('candidate.metrics.roi_90d_pct', { valueAsNumber: true })}
              error={errors.candidate?.metrics?.roi_90d_pct?.message}
              required
            />
            <FormInput
              label="ROI 180 días (%)"
              type="number"
              step="0.01"
              {...register('candidate.metrics.roi_180d_pct', { valueAsNumber: true })}
              hint="Opcional"
            />
            <FormInput
              label="Max Drawdown (%)"
              type="number"
              step="0.01"
              {...register('candidate.metrics.max_drawdown_pct', { valueAsNumber: true })}
              error={errors.candidate?.metrics?.max_drawdown_pct?.message}
              required
            />
            <FormInput
              label="Win Rate (%)"
              type="number"
              step="0.01"
              {...register('candidate.metrics.win_rate_pct', { valueAsNumber: true })}
              error={errors.candidate?.metrics?.win_rate_pct?.message}
              required
            />
            <FormInput
              label="Leverage Promedio"
              type="number"
              step="0.1"
              {...register('candidate.metrics.avg_leverage', { valueAsNumber: true })}
              error={errors.candidate?.metrics?.avg_leverage?.message}
              required
            />
            <FormInput
              label="Copiadores"
              type="number"
              {...register('candidate.metrics.copiers', { valueAsNumber: true })}
              error={errors.candidate?.metrics?.copiers?.message}
              required
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
              {...register('candidate.copy_mode_suggestion')}
              error={errors.candidate?.copy_mode_suggestion?.message}
              required
            />
            <FormInput
              label="Tamaño Orden (USDT)"
              type="number"
              step="1"
              {...register('candidate.order_size_suggestion_usdt', { valueAsNumber: true })}
              error={errors.candidate?.order_size_suggestion_usdt?.message}
              hint="Mínimo 10 USDT"
              required
            />
            <FormInput
              label="Cap Pérdida Diaria (%)"
              type="number"
              step="0.1"
              {...register('candidate.daily_loss_cap_pct', { valueAsNumber: true })}
              error={errors.candidate?.daily_loss_cap_pct?.message}
              required
            />
            <FormInput
              label="Stop Copy Drawdown (%)"
              type="number"
              step="0.1"
              {...register('candidate.stop_copy_drawdown_pct', { valueAsNumber: true })}
              error={errors.candidate?.stop_copy_drawdown_pct?.message}
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

        {/* Notas */}
        <FormSection title="Notas" description="Observaciones adicionales sobre el trader">
          <FormTextarea
            label="Notas"
            {...register('candidate.notes')}
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
