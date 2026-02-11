/**
 * Utilidades para formatear datos
 */

/**
 * Formatea un número como porcentaje
 */
export function formatPercent(value: number | null | undefined, decimals: number = 1): string {
  if (value === null || value === undefined) return 'N/A';
  return `${value.toFixed(decimals)}%`;
}

/**
 * Formatea un número con separadores de miles
 */
export function formatNumber(value: number | null | undefined, decimals: number = 0): string {
  if (value === null || value === undefined) return 'N/A';
  return new Intl.NumberFormat('es-ES', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Formatea una cantidad en USDT
 */
export function formatUSDT(value: number | null | undefined, decimals: number = 2): string {
  if (value === null || value === undefined) return 'N/A';
  return `${formatNumber(value, decimals)} USDT`;
}

/**
 * Formatea una fecha en formato legible
 */
export function formatDate(date: string | Date, includeTime: boolean = false): string {
  const d = typeof date === 'string' ? new Date(date) : date;

  if (isNaN(d.getTime())) return 'Fecha inválida';

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  };

  if (includeTime) {
    options.hour = '2-digit';
    options.minute = '2-digit';
  }

  return new Intl.DateTimeFormat('es-ES', options).format(d);
}

/**
 * Formatea una fecha relativa (hace X días)
 */
export function formatRelativeDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  const now = new Date();
  const diffMs = now.getTime() - d.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return 'Hoy';
  if (diffDays === 1) return 'Ayer';
  if (diffDays < 7) return `Hace ${diffDays} días`;
  if (diffDays < 30) return `Hace ${Math.floor(diffDays / 7)} semanas`;
  if (diffDays < 365) return `Hace ${Math.floor(diffDays / 30)} meses`;
  return `Hace ${Math.floor(diffDays / 365)} años`;
}

/**
 * Formatea el leverage (ej: 2.5× → 2.5×)
 */
export function formatLeverage(value: number | null | undefined): string {
  if (value === null || value === undefined) return 'N/A';
  return `${value.toFixed(1)}×`;
}

/**
 * Obtiene el color para un valor de ROI
 */
export function getROIColor(roi: number): string {
  if (roi > 0) return 'text-success';
  if (roi < 0) return 'text-danger';
  return 'text-text-secondary';
}

/**
 * Obtiene el color para un score
 */
export function getScoreColor(score: number): string {
  if (score >= 85) return 'text-success';
  if (score >= 70) return 'text-info';
  if (score >= 55) return 'text-warning';
  return 'text-danger';
}

/**
 * Obtiene la clasificación de un score
 */
export function getScoreClassification(score: number): {
  label: string;
  color: string;
  variant: 'success' | 'info' | 'warning' | 'danger';
} {
  if (score >= 85) {
    return { label: 'Excelente', color: 'text-success', variant: 'success' };
  }
  if (score >= 70) {
    return { label: 'Bueno', color: 'text-info', variant: 'info' };
  }
  if (score >= 55) {
    return { label: 'Aceptable', color: 'text-warning', variant: 'warning' };
  }
  if (score >= 40) {
    return { label: 'Marginal', color: 'text-danger', variant: 'danger' };
  }
  return { label: 'Pobre', color: 'text-danger', variant: 'danger' };
}

/**
 * Trunca un texto largo
 */
export function truncateText(text: string, maxLength: number = 50): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

/**
 * Capitaliza la primera letra de cada palabra
 */
export function capitalize(text: string): string {
  return text
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

/**
 * Formatea el perfil de riesgo
 */
export function formatRiskProfile(profile: string): string {
  const profiles: Record<string, string> = {
    conservative: 'Conservador',
    moderate: 'Moderado',
    aggressive: 'Agresivo',
  };
  return profiles[profile] || capitalize(profile);
}

/**
 * Formatea el estilo de trading
 */
export function formatTradingStyle(style: string): string {
  const styles: Record<string, string> = {
    scalping: 'Scalping',
    swing: 'Swing Trading',
    'trend-following': 'Seguimiento de Tendencia',
    arbitrage: 'Arbitraje',
    mixed: 'Mixto',
  };
  return styles[style] || capitalize(style);
}
