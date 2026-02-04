import { useState, useEffect, useMemo } from 'react';
import { getAllTraders, type Trader } from '../services/evaluations';
import { addTraderByUrl } from '../services/binance';
import { syncHyperliquidTraders } from '../services/hyperliquid';
import { fetchCoinReport, parseReportSections, type CoinReport, type ReportSection } from '../services/gemini';
import toast from 'react-hot-toast';

type ModalType = 'none' | 'addManual' | 'syncHyperliquid' | 'metricsHelp' | 'confirmCopy' | 'coinReport';

type SortColumn = 'name' | 'platform' | 'roi' | 'drawdown' | 'winrate' | 'copiers' | 'trades' | 'days' | 'pnl' | 'reliable' | 'updated';
type SortDirection = 'asc' | 'desc';

interface SortConfig {
  column: SortColumn;
  direction: SortDirection;
}

const SORT_STORAGE_KEY = 'traders-sort-config';
const DEFAULT_SORT: SortConfig = { column: 'roi', direction: 'desc' };

export function Traders() {
  const [traders, setTraders] = useState<Trader[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);
  const [modalType, setModalType] = useState<ModalType>('none');
  const [traderUrl, setTraderUrl] = useState('');
  const [selectedTraderForCopy, setSelectedTraderForCopy] = useState<Trader | null>(null);
  const [showTraderDetails, setShowTraderDetails] = useState(false);

  // State for coin report (Gemini AI)
  const [coinReport, setCoinReport] = useState<CoinReport | null>(null);
  const [coinReportSections, setCoinReportSections] = useState<ReportSection[]>([]);
  const [coinReportLoading, setCoinReportLoading] = useState(false);
  const [coinReportError, setCoinReportError] = useState<string | null>(null);
  const [selectedCoinForReport, setSelectedCoinForReport] = useState<{ coin: string; traderName: string; pnl?: number; winRate?: number } | null>(null);

  // Estado de ordenamiento (auto-guarda en localStorage)
  const [sortConfig, setSortConfig] = useState<SortConfig>(() => {
    const saved = localStorage.getItem(SORT_STORAGE_KEY);
    return saved ? JSON.parse(saved) : DEFAULT_SORT;
  });

  // Auto-guardar cuando cambia el orden
  useEffect(() => {
    localStorage.setItem(SORT_STORAGE_KEY, JSON.stringify(sortConfig));
  }, [sortConfig]);

  // Obtiene info de la plataforma basado en las metricas o URL
  const getPlatformInfo = (trader: Trader) => {
    const platform = (trader.latest_metrics as Record<string, unknown>)?.platform as string | undefined;
    const url = trader.binance_profile_url || '';

    if (platform === 'hyperliquid' || url.includes('hyperliquid')) {
      return { name: 'Hyperliquid', color: 'text-cyan-400', bg: 'bg-cyan-500/20', icon: '⚡' };
    }
    if (platform === 'bybit' || url.includes('bybit')) {
      return { name: 'Bybit', color: 'text-orange-400', bg: 'bg-orange-500/20', icon: '🔶' };
    }
    if (platform === 'bitget' || url.includes('bitget')) {
      return { name: 'Bitget', color: 'text-green-400', bg: 'bg-green-500/20', icon: '🟢' };
    }
    if (url.includes('binance')) {
      return { name: 'Binance', color: 'text-yellow-400', bg: 'bg-yellow-500/20', icon: '🟡' };
    }
    return { name: 'Manual', color: 'text-gray-400', bg: 'bg-gray-500/20', icon: '📝' };
  };

  const loadTraders = async () => {
    try {
      const data = await getAllTraders();
      setTraders(data);
    } catch (error) {
      console.error('Error loading traders:', error);
      toast.error('Error al cargar traders');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTraders();
  }, []);

  // Función para obtener valor de ordenamiento
  const getSortValue = (trader: Trader, column: SortColumn): number | string => {
    const metrics = trader.latest_metrics as Record<string, unknown> | undefined;
    const platformInfo = getPlatformInfo(trader);

    switch (column) {
      case 'name':
        return trader.display_name.toLowerCase();
      case 'platform':
        return platformInfo.name.toLowerCase();
      case 'roi':
        return (metrics?.roi_30d_pct as number) ?? -Infinity;
      case 'drawdown':
        return (metrics?.max_drawdown_pct as number) ?? Infinity;
      case 'winrate':
        return (metrics?.win_rate_pct as number) ?? -Infinity;
      case 'copiers':
        return (metrics?.copiers as number) ?? -Infinity;
      case 'trades':
        return (metrics?.total_trades as number) ?? -Infinity;
      case 'days':
        return (metrics?.days_active as number) ?? -Infinity;
      case 'pnl':
        return (metrics?.pnl as number) ?? -Infinity;
      case 'reliable':
        return (metrics?.is_reliable as boolean) ? 1 : 0;
      case 'updated':
        return trader.metrics_updated_at ? new Date(trader.metrics_updated_at).getTime() : 0;
      default:
        return 0;
    }
  };

  // Traders ordenados
  const sortedTraders = useMemo(() => {
    const sorted = [...traders].sort((a, b) => {
      const aVal = getSortValue(a, sortConfig.column);
      const bVal = getSortValue(b, sortConfig.column);

      let comparison = 0;
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        comparison = aVal.localeCompare(bVal);
      } else {
        comparison = (aVal as number) - (bVal as number);
      }

      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });
    return sorted;
  }, [traders, sortConfig]);

  // Cambiar ordenamiento (se auto-guarda)
  const handleSort = (column: SortColumn) => {
    setSortConfig(prev => ({
      column,
      direction: prev.column === column && prev.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  // Calcular score de un trader para recomendaciones
  // Ajustado para métricas disponibles de Hyperliquid (ROI, DD, WR, copiers, AUM)
  const calculateTraderScore = (trader: Trader): { score: number; reasons: string[] } => {
    const metrics = trader.latest_metrics as Record<string, unknown> | undefined;
    if (!metrics) return { score: 0, reasons: ['Sin datos'] };

    let score = 0;
    const reasons: string[] = [];

    const roi = (metrics.roi_30d_pct as number) ?? 0;
    const dd = (metrics.max_drawdown_pct as number) ?? 100;
    const wr = (metrics.win_rate_pct as number) ?? 0;
    const copiers = (metrics.copiers as number) ?? 0;
    const aum = (metrics.aum as number) ?? 0;
    const volume = (metrics.volume as number) ?? 0;
    const trades = (metrics.total_trades as number) ?? 0;
    const days = (metrics.days_active as number) ?? 0;
    const pnl = (metrics.pnl as number) ?? 0;
    const isReliable = (metrics.is_reliable as boolean) ?? false;

    // Criterios principales (métricas siempre disponibles)
    // ROI: buen retorno pero no extremo (máx 25 pts)
    if (roi >= 50 && roi < 200) { score += 25; reasons.push(`ROI ${roi.toFixed(0)}%`); }
    else if (roi >= 20 && roi < 50) { score += 20; reasons.push(`ROI ${roi.toFixed(0)}%`); }
    else if (roi >= 10) { score += 15; reasons.push(`ROI ${roi.toFixed(0)}%`); }
    else if (roi > 0) { score += 5; }

    // Drawdown: menor es mejor (máx 25 pts)
    if (dd < 10) { score += 25; reasons.push(`DD bajo ${dd.toFixed(0)}%`); }
    else if (dd < 20) { score += 20; reasons.push(`DD ${dd.toFixed(0)}%`); }
    else if (dd < 30) { score += 10; }
    else if (dd < 40) { score += 5; }

    // Win Rate (máx 20 pts)
    if (wr > 60) { score += 20; reasons.push(`WR ${wr.toFixed(0)}%`); }
    else if (wr > 50) { score += 15; reasons.push(`WR ${wr.toFixed(0)}%`); }
    else if (wr > 40) { score += 10; }

    // Copiers: señal de confianza social (máx 15 pts)
    if (copiers >= 100) { score += 15; reasons.push(`${copiers} copiers`); }
    else if (copiers >= 50) { score += 10; reasons.push(`${copiers} copiers`); }
    else if (copiers >= 10) { score += 5; }

    // AUM/Volumen: actividad real (máx 15 pts)
    if (aum >= 100000 || volume >= 1000000) { score += 15; reasons.push('Alto volumen'); }
    else if (aum >= 10000 || volume >= 100000) { score += 10; }
    else if (aum >= 1000 || volume >= 10000) { score += 5; }

    // Métricas adicionales cuando están disponibles
    if (isReliable) { score += 10; reasons.push('Verificado'); }
    if (trades >= 50) { score += 5; reasons.push(`${trades} trades`); }
    if (days >= 30) { score += 5; reasons.push(`${days}d activo`); }
    if (pnl > 10000) { score += 5; reasons.push(`+$${(pnl/1000).toFixed(0)}k`); }

    return { score, reasons };
  };

  // Top 5 traders recomendados
  const topRecommendations = useMemo(() => {
    return traders
      .map(trader => ({
        trader,
        ...calculateTraderScore(trader)
      }))
      .filter(t => t.score >= 25) // Mínimo 25 puntos
      .sort((a, b) => b.score - a.score)
      .slice(0, 5);
  }, [traders]);

  const handleAddTrader = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!traderUrl.trim()) {
      toast.error('Ingresa una URL válida');
      return;
    }

    if (!traderUrl.includes('binance.com') || !traderUrl.includes('lead-details')) {
      toast.error('URL inválida. Debe ser una URL de perfil de trader de Binance Copy Trading');
      return;
    }

    setIsProcessing(true);
    try {
      const result = await addTraderByUrl(traderUrl);
      toast.success(
        result.isNew
          ? `Trader "${result.trader.display_name}" agregado exitosamente`
          : `Trader "${result.trader.display_name}" actualizado`
      );
      setModalType('none');
      setTraderUrl('');
      await loadTraders();
    } catch (error) {
      console.error('Error adding trader:', error);
      toast.error(error instanceof Error ? error.message : 'Error al agregar trader');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSyncHyperliquid = async () => {
    setIsProcessing(true);
    try {
      const result = await syncHyperliquidTraders({ limit: 20, validate: true });
      toast.success(`Hyperliquid: ${result.created} nuevos, ${result.updated} actualizados`);
      setModalType('none');
      await loadTraders();
    } catch (error) {
      console.error('Error syncing Hyperliquid:', error);
      toast.error(error instanceof Error ? error.message : 'Error al sincronizar con Hyperliquid');
    } finally {
      setIsProcessing(false);
    }
  };

  const formatPercent = (value?: number) => {
    if (value === undefined || value === null) return '-';
    const color = value >= 0 ? 'text-green-400' : 'text-red-400';
    return <span className={color}>{value.toFixed(2)}%</span>;
  };

  const formatTimeAgo = (date?: string) => {
    if (!date) return '-';
    const diff = Date.now() - new Date(date).getTime();
    const minutes = Math.floor(diff / 60000);
    if (minutes < 60) return `${minutes}m`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h`;
    const days = Math.floor(hours / 24);
    return `${days}d`;
  };

  // Genera JSON con datos del trader para copy trading
  const generateTraderJson = (trader: Trader) => {
    const metrics = trader.latest_metrics;
    const riskProfile = getRiskProfile(metrics);
    const platformInfo = getPlatformInfo(trader);

    // Detectar plataforma basado en metrics o URL
    const platform = platformInfo.name.toLowerCase();

    const traderData = {
      // Identificacion
      id: trader.id,
      display_name: trader.display_name,
      platform_uid: trader.binance_uid,
      platform: platform,
      profile_url: trader.binance_profile_url,

      // Metricas actuales
      metrics: {
        roi_30d_pct: metrics?.roi_30d_pct || null,
        roi_90d_pct: metrics?.roi_90d_pct || null,
        max_drawdown_pct: metrics?.max_drawdown_pct || null,
        win_rate_pct: metrics?.win_rate_pct || null,
        copiers: metrics?.copiers || null,
        avg_leverage: metrics?.avg_leverage || null,
      },

      // Clasificacion
      risk_profile: riskProfile.level,
      trading_style: trader.trading_style || 'mixed',

      // Configuracion sugerida para copy trading
      suggested_copy_settings: {
        // Basado en el perfil de riesgo
        max_position_size_usdt: riskProfile.level === 'conservador' ? 100 :
                                 riskProfile.level === 'moderado' ? 50 :
                                 riskProfile.level === 'agresivo' ? 25 : 10,
        stop_loss_pct: riskProfile.level === 'conservador' ? 5 :
                       riskProfile.level === 'moderado' ? 10 :
                       riskProfile.level === 'agresivo' ? 15 : 20,
        take_profit_pct: riskProfile.level === 'conservador' ? 10 :
                         riskProfile.level === 'moderado' ? 20 :
                         riskProfile.level === 'agresivo' ? 30 : 50,
        max_daily_trades: riskProfile.level === 'conservador' ? 5 :
                          riskProfile.level === 'moderado' ? 10 : 15,
      },

      // Metadata
      generated_at: new Date().toISOString(),
      metrics_updated_at: trader.metrics_updated_at,
      data_source: 'akira-traders',
    };

    return traderData;
  };

  const handleExportJson = (trader: Trader) => {
    const data = generateTraderJson(trader);
    const json = JSON.stringify(data, null, 2);

    // Copiar al clipboard
    navigator.clipboard.writeText(json).then(() => {
      toast.success(`JSON de "${trader.display_name}" copiado al portapapeles`);
    }).catch(() => {
      // Fallback: descargar archivo
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `trader_${trader.display_name.replace(/\s+/g, '_').toLowerCase()}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`JSON descargado`);
    });
  };

  // Generar reporte AI de una moneda con Gemini
  const handleCoinReport = async (
    coin: string,
    traderName: string,
    coinPnl?: number,
    coinWinRate?: number,
    e?: React.MouseEvent
  ) => {
    if (e) e.stopPropagation();

    setSelectedCoinForReport({ coin, traderName, pnl: coinPnl, winRate: coinWinRate });
    setCoinReport(null);
    setCoinReportSections([]);
    setCoinReportError(null);
    setCoinReportLoading(true);
    setModalType('coinReport');

    try {
      const report = await fetchCoinReport({
        coin,
        traderName,
        pnl: coinPnl,
        winRate: coinWinRate,
      });
      setCoinReport(report);
      setCoinReportSections(parseReportSections(report.report));
    } catch (error) {
      console.error('Error generating coin report:', error);
      setCoinReportError(error instanceof Error ? error.message : 'Error al generar reporte');
      toast.error('Error al generar reporte de la moneda');
    } finally {
      setCoinReportLoading(false);
    }
  };

  // Abrir modal de confirmación para copiar
  const handleAskCopyJson = (trader: Trader) => {
    setSelectedTraderForCopy(trader);
    setShowTraderDetails(false);
    setModalType('confirmCopy');
  };

  // Confirmar y copiar JSON
  const handleConfirmCopy = () => {
    if (selectedTraderForCopy) {
      handleExportJson(selectedTraderForCopy);
      setModalType('none');
      setSelectedTraderForCopy(null);
    }
  };

  // Clasificacion de riesgo basada en metricas
  // Criterios:
  // - CONSERVADOR: DD < 15% AND Win Rate > 55% AND ROI entre 0-50%
  // - MODERADO: DD 15-25% OR (Win Rate 45-55%) OR ROI 50-100%
  // - AGRESIVO: DD 25-35% OR ROI > 100% OR Win Rate 35-45%
  // - PELIGROSO: DD > 35% OR Win Rate < 35% OR (DD > 25% AND Win Rate < 45%)
  const getRiskProfile = (metrics?: { roi_30d_pct?: number; max_drawdown_pct?: number; win_rate_pct?: number }) => {
    if (!metrics) return { level: 'sin datos', color: 'text-text-tertiary', bg: 'bg-gray-500/20' };

    const dd = metrics.max_drawdown_pct || 0;
    const wr = metrics.win_rate_pct || 50;
    const roi = metrics.roi_30d_pct || 0;

    // Peligroso: condiciones de alto riesgo
    if (dd > 35 || wr < 35 || (dd > 25 && wr < 45)) {
      return { level: 'peligroso', color: 'text-red-400', bg: 'bg-red-500/20' };
    }

    // Agresivo: alto rendimiento con riesgo elevado
    if (dd > 25 || roi > 100 || (wr >= 35 && wr < 45)) {
      return { level: 'agresivo', color: 'text-orange-400', bg: 'bg-orange-500/20' };
    }

    // Conservador: bajo riesgo y consistencia
    if (dd < 15 && wr > 55 && roi >= 0 && roi <= 50) {
      return { level: 'conservador', color: 'text-green-400', bg: 'bg-green-500/20' };
    }

    // Moderado: balance entre riesgo y rendimiento
    return { level: 'moderado', color: 'text-yellow-400', bg: 'bg-yellow-500/20' };
  };

  return (
    <div className="py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold text-text-primary">
              Traders
            </h1>
            <button
              onClick={() => setModalType('metricsHelp')}
              className="p-1.5 text-text-tertiary hover:text-primary hover:bg-primary/10 rounded-lg transition-colors"
              title="Ver guia de metricas"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
          </div>
          {traders.length > 0 && (
            <p className="text-text-tertiary text-sm mt-1">
              {traders.length} trader{traders.length !== 1 ? 's' : ''} registrado{traders.length !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        <div className="flex items-center gap-2 flex-wrap">
          <button
            onClick={() => setModalType('syncHyperliquid')}
            className="flex items-center gap-2 px-3 py-2 bg-cyan-600 text-white text-sm rounded-lg hover:bg-cyan-700 transition-colors"
            title="Sincronizar traders de Hyperliquid (datos reales)"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Hyperliquid
          </button>
          <button
            onClick={() => setModalType('addManual')}
            className="flex items-center gap-2 px-3 py-2 bg-primary text-white text-sm rounded-lg hover:bg-primary/90 transition-colors"
            title="Agregar trader manualmente"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Manual
          </button>
        </div>
      </div>

      {/* Modal para agregar trader manual */}
      {modalType === 'addManual' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-bg-secondary rounded-xl border border-border max-w-lg w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Agregar Trader (Binance URL)</h2>
              <button
                onClick={() => setModalType('none')}
                className="text-text-tertiary hover:text-text-primary transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleAddTrader}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-text-secondary mb-2">
                  URL del Trader en Binance Copy Trading
                </label>
                <input
                  type="url"
                  value={traderUrl}
                  onChange={(e) => setTraderUrl(e.target.value)}
                  placeholder="https://www.binance.com/en/copy-trading/lead-details/..."
                  className="w-full px-4 py-3 bg-bg-tertiary border border-border rounded-lg text-text-primary placeholder-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  disabled={isProcessing}
                />
                <p className="text-text-tertiary text-xs mt-2">
                  Copia la URL del perfil del trader desde Binance Copy Trading
                </p>
              </div>

              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => setModalType('none')}
                  className="flex-1 px-4 py-2 bg-bg-tertiary text-text-primary rounded-lg hover:bg-border transition-colors"
                  disabled={isProcessing}
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={isProcessing || !traderUrl.trim()}
                  className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isProcessing ? (
                    <>
                      <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Obteniendo...
                    </>
                  ) : (
                    'Agregar'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal para sincronizar Hyperliquid */}
      {modalType === 'syncHyperliquid' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-bg-secondary rounded-xl border border-border max-w-md w-full p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Sincronizar Hyperliquid</h2>
              <button
                onClick={() => setModalType('none')}
                className="text-text-tertiary hover:text-text-primary transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-6">
              <div className="flex items-center gap-3 p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-lg mb-4">
                <svg className="h-8 w-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                <div>
                  <p className="text-text-primary font-medium">Datos On-Chain Reales</p>
                  <p className="text-text-tertiary text-sm">Hyperliquid DEX - API Publica Gratuita</p>
                </div>
              </div>
              <p className="text-text-secondary text-sm">
                Se importaran los top 20 traders del leaderboard de Hyperliquid con metricas reales verificables on-chain.
              </p>
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setModalType('none')}
                className="flex-1 px-4 py-2 bg-bg-tertiary text-text-primary rounded-lg hover:bg-border transition-colors"
                disabled={isProcessing}
              >
                Cancelar
              </button>
              <button
                onClick={handleSyncHyperliquid}
                disabled={isProcessing}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isProcessing ? (
                  <>
                    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Sincronizando...
                  </>
                ) : (
                  <>
                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    Sincronizar
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal de ayuda de metricas */}
      {modalType === 'metricsHelp' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-bg-secondary rounded-xl border border-border max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-text-primary">Guia de Metricas</h2>
              <button
                onClick={() => setModalType('none')}
                className="text-text-tertiary hover:text-text-primary transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              {/* ROI 30d */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg font-semibold text-text-primary">ROI 30d</span>
                  <span className="text-xs px-2 py-0.5 bg-green-500/20 text-green-400 rounded">Retorno</span>
                </div>
                <p className="text-text-secondary text-sm mb-2">
                  Retorno sobre inversion en los ultimos 30 dias. Si invertiste $100 y el ROI es 15%, ganaste $15.
                </p>
                <div className="flex gap-4 text-xs">
                  <span className="text-green-400">+10% bueno</span>
                  <span className="text-yellow-400">0-10% moderado</span>
                  <span className="text-red-400">&lt;0% perdida</span>
                </div>
              </div>

              {/* Max DD */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg font-semibold text-text-primary">Max DD (Drawdown)</span>
                  <span className="text-xs px-2 py-0.5 bg-red-500/20 text-red-400 rounded">Riesgo</span>
                </div>
                <p className="text-text-secondary text-sm mb-2">
                  Maxima caida desde un pico. Mide cuanto podrias perder en el peor momento. Un DD de 20% significa que en algun punto perdio 20% desde su maximo.
                </p>
                <div className="flex gap-4 text-xs">
                  <span className="text-green-400">&lt;15% conservador</span>
                  <span className="text-yellow-400">15-25% moderado</span>
                  <span className="text-red-400">&gt;30% riesgoso</span>
                </div>
              </div>

              {/* Win Rate */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg font-semibold text-text-primary">Win Rate</span>
                  <span className="text-xs px-2 py-0.5 bg-blue-500/20 text-blue-400 rounded">Consistencia</span>
                </div>
                <p className="text-text-secondary text-sm mb-2">
                  Porcentaje de operaciones ganadoras vs perdedoras. Un 60% significa que de cada 10 trades, 6 son ganadores.
                </p>
                <div className="flex gap-4 text-xs">
                  <span className="text-green-400">&gt;55% consistente</span>
                  <span className="text-yellow-400">40-55% normal</span>
                  <span className="text-red-400">&lt;40% inconsistente</span>
                </div>
              </div>

              {/* Copiers */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg font-semibold text-text-primary">Copiers</span>
                  <span className="text-xs px-2 py-0.5 bg-purple-500/20 text-purple-400 rounded">Popularidad</span>
                </div>
                <p className="text-text-secondary text-sm mb-2">
                  Cantidad de personas copiando al trader. Indica popularidad y confianza de otros usuarios.
                </p>
                <div className="flex gap-4 text-xs">
                  <span className="text-green-400">&gt;500 popular</span>
                  <span className="text-yellow-400">100-500 moderado</span>
                  <span className="text-text-tertiary">&lt;100 nuevo</span>
                </div>
              </div>

              {/* Actualizado */}
              <div className="p-4 bg-bg-tertiary rounded-lg">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg font-semibold text-text-primary">Actualizado</span>
                  <span className="text-xs px-2 py-0.5 bg-gray-500/20 text-gray-400 rounded">Frescura</span>
                </div>
                <p className="text-text-secondary text-sm mb-2">
                  Hace cuanto se actualizaron las metricas. m=minutos, h=horas, d=dias.
                </p>
                <div className="flex gap-4 text-xs">
                  <span className="text-green-400">&lt;1h fresco</span>
                  <span className="text-yellow-400">1-24h reciente</span>
                  <span className="text-red-400">&gt;7d desactualizado</span>
                </div>
              </div>

              {/* Interpretacion */}
              <div className="p-4 bg-primary/10 border border-primary/20 rounded-lg">
                <h3 className="text-sm font-semibold text-primary mb-2">Interpretacion rapida</h3>
                <ul className="text-text-secondary text-sm space-y-1">
                  <li><span className="text-green-400">Conservador:</span> ROI moderado (10-30%), DD bajo (&lt;15%), Win Rate alto (&gt;60%)</li>
                  <li><span className="text-yellow-400">Agresivo:</span> ROI alto (&gt;50%), DD alto (&gt;25%), mas volatil</li>
                  <li><span className="text-red-400">Alerta:</span> DD muy alto + Win Rate bajo = alto riesgo de perdidas</li>
                </ul>
              </div>
            </div>

            <button
              onClick={() => setModalType('none')}
              className="w-full mt-6 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Entendido
            </button>
          </div>
        </div>
      )}

      {/* Modal de confirmación para copiar JSON */}
      {modalType === 'confirmCopy' && selectedTraderForCopy && (() => {
        const traderMetrics = selectedTraderForCopy.latest_metrics as Record<string, unknown> | undefined;
        const traderPlatform = getPlatformInfo(selectedTraderForCopy);
        const traderRisk = getRiskProfile(selectedTraderForCopy.latest_metrics);
        return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className={`bg-bg-secondary rounded-xl border border-border w-full p-6 transition-all ${showTraderDetails ? 'max-w-2xl max-h-[90vh] overflow-y-auto' : 'max-w-md'}`}>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-text-primary">Copiar configuración</h2>
              <button
                onClick={() => {
                  setModalType('none');
                  setSelectedTraderForCopy(null);
                  setShowTraderDetails(false);
                }}
                className="text-text-tertiary hover:text-text-primary transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="mb-6">
              <div className="flex items-center gap-3 p-4 bg-primary/10 border border-primary/20 rounded-lg mb-4">
                <div className={`w-10 h-10 ${traderPlatform.bg} rounded-full flex items-center justify-center`}>
                  <span className="text-lg">{traderPlatform.icon}</span>
                </div>
                <div className="flex-1">
                  <p className="text-text-primary font-medium">{selectedTraderForCopy.display_name}</p>
                  <div className="flex items-center gap-2">
                    <span className={`text-xs ${traderPlatform.color}`}>{traderPlatform.name}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded ${traderRisk.bg} ${traderRisk.color}`}>
                      {traderRisk.level}
                    </span>
                  </div>
                </div>
              </div>

              {/* Botón Ver Detalle */}
              <button
                onClick={() => setShowTraderDetails(!showTraderDetails)}
                className="w-full flex items-center justify-between p-3 bg-bg-tertiary rounded-lg hover:bg-border transition-colors mb-4"
              >
                <span className="text-sm text-text-secondary">Ver toda la información</span>
                <svg
                  className={`h-4 w-4 text-text-tertiary transition-transform ${showTraderDetails ? 'rotate-180' : ''}`}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Detalles expandibles */}
              {showTraderDetails && (
                <div className="space-y-4 mb-4 p-4 bg-bg-tertiary rounded-lg">
                  {/* Métricas principales */}
                  <div>
                    <h3 className="text-sm font-medium text-text-primary mb-2">Métricas de Rendimiento</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">ROI 30d</span>
                        <p className={`text-sm font-medium ${(traderMetrics?.roi_30d_pct as number) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {traderMetrics?.roi_30d_pct !== undefined ? `${(traderMetrics.roi_30d_pct as number).toFixed(2)}%` : '-'}
                        </p>
                      </div>
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">Max Drawdown</span>
                        <p className="text-sm font-medium text-red-400">
                          {traderMetrics?.max_drawdown_pct !== undefined ? `-${(traderMetrics.max_drawdown_pct as number).toFixed(2)}%` : '-'}
                        </p>
                      </div>
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">Win Rate</span>
                        <p className="text-sm font-medium text-text-primary">
                          {traderMetrics?.win_rate_pct !== undefined ? `${(traderMetrics.win_rate_pct as number).toFixed(1)}%` : '-'}
                        </p>
                      </div>
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">PnL Total</span>
                        <p className={`text-sm font-medium ${(traderMetrics?.pnl as number) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {traderMetrics?.pnl !== undefined ? `$${(traderMetrics.pnl as number).toLocaleString(undefined, { maximumFractionDigits: 0 })}` : '-'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Métricas de confiabilidad */}
                  <div>
                    <h3 className="text-sm font-medium text-text-primary mb-2">Métricas de Confiabilidad</h3>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">Total Trades</span>
                        <p className="text-sm font-medium text-text-primary">
                          {traderMetrics?.total_trades !== undefined ? (traderMetrics.total_trades as number).toLocaleString() : '-'}
                        </p>
                      </div>
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">Días Activo</span>
                        <p className="text-sm font-medium text-text-primary">
                          {traderMetrics?.days_active !== undefined ? `${traderMetrics.days_active}d` : '-'}
                        </p>
                      </div>
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">Copiers</span>
                        <p className="text-sm font-medium text-text-primary">
                          {traderMetrics?.copiers !== undefined ? (traderMetrics.copiers as number).toLocaleString() : '-'}
                        </p>
                      </div>
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">Verificado</span>
                        <p className="text-sm font-medium">
                          {traderMetrics?.is_reliable !== undefined ? (
                            traderMetrics.is_reliable ? (
                              <span className="text-green-400">✓ Sí</span>
                            ) : (
                              <span className="text-red-400">✗ No</span>
                            )
                          ) : '-'}
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Mejores Monedas */}
                  {(() => {
                    const topCoins = traderMetrics?.top_coins as Array<{ coin: string; pnl: number; trades: number; winRate: number }> | undefined;
                    if (!topCoins || topCoins.length === 0) return null;
                    return (
                      <div>
                        <h3 className="text-sm font-medium text-text-primary mb-2">Mejores Monedas <span className="text-[10px] text-text-tertiary font-normal">(click para reporte AI)</span></h3>
                        <div className="grid grid-cols-3 gap-2">
                          {topCoins.map((c, i) => (
                            <button
                              key={i}
                              onClick={() => handleCoinReport(c.coin, selectedTraderForCopy!.display_name, c.pnl, c.winRate)}
                              className="p-2 bg-bg-secondary rounded text-left hover:ring-1 hover:ring-primary/50 transition-all cursor-pointer"
                              title={`Click: generar reporte AI de ${c.coin}`}
                            >
                              <div className="flex items-center justify-between mb-1">
                                <span className="text-sm font-medium text-text-primary">{c.coin}</span>
                                <span className={`text-xs font-medium ${c.pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  ${(c.pnl / 1000).toFixed(1)}k
                                </span>
                              </div>
                              <div className="flex items-center justify-between text-[10px] text-text-tertiary">
                                <span>{c.trades} trades</span>
                                <span>WR {c.winRate.toFixed(0)}%</span>
                              </div>
                            </button>
                          ))}
                        </div>
                      </div>
                    );
                  })()}

                  {/* Identificación */}
                  <div>
                    <h3 className="text-sm font-medium text-text-primary mb-2">Identificación</h3>
                    <div className="space-y-2">
                      <div className="p-2 bg-bg-secondary rounded">
                        <span className="text-xs text-text-tertiary">Platform UID</span>
                        <p className="text-sm font-mono text-text-primary break-all">
                          {selectedTraderForCopy.binance_uid || '-'}
                        </p>
                      </div>
                      {selectedTraderForCopy.binance_profile_url && (
                        <div className="p-2 bg-bg-secondary rounded">
                          <span className="text-xs text-text-tertiary">Perfil</span>
                          <a
                            href={selectedTraderForCopy.binance_profile_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary hover:underline break-all block"
                          >
                            {selectedTraderForCopy.binance_profile_url}
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              <p className="text-text-secondary text-sm">
                {showTraderDetails
                  ? 'Revisa la información arriba y haz clic en "Copiar JSON" para copiar la configuración completa.'
                  : '¿Deseas copiar la configuración JSON de este trader al portapapeles?'}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => {
                  setModalType('none');
                  setSelectedTraderForCopy(null);
                  setShowTraderDetails(false);
                }}
                className="flex-1 px-4 py-2 bg-bg-tertiary text-text-primary rounded-lg hover:bg-border transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirmCopy}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copiar JSON
              </button>
            </div>
          </div>
        </div>
        );
      })()}

      {/* Modal: Coin Report (Gemini AI) */}
      {modalType === 'coinReport' && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-bg-secondary rounded-xl border border-border max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-purple-500/20 rounded-full flex items-center justify-center">
                  <svg className="h-5 w-5 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <h2 className="text-xl font-semibold text-text-primary">
                    Reporte AI: {selectedCoinForReport?.coin}
                  </h2>
                  <p className="text-xs text-text-tertiary">
                    Generado con Gemini
                    {selectedCoinForReport?.traderName && ` | Trader: ${selectedCoinForReport.traderName}`}
                  </p>
                </div>
              </div>
              <button
                onClick={() => { setModalType('none'); setCoinReport(null); setCoinReportError(null); }}
                className="text-text-tertiary hover:text-text-primary transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Loading state */}
            {coinReportLoading && (
              <div className="flex flex-col items-center justify-center py-12">
                <svg className="animate-spin h-8 w-8 text-purple-400 mb-4" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <p className="text-text-secondary text-sm">Analizando {selectedCoinForReport?.coin}...</p>
                <p className="text-text-tertiary text-xs mt-1">Esto puede tomar unos segundos</p>
              </div>
            )}

            {/* Error state */}
            {coinReportError && !coinReportLoading && (
              <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-lg">
                <p className="text-red-400 text-sm">{coinReportError}</p>
                <button
                  onClick={() => {
                    if (selectedCoinForReport) {
                      handleCoinReport(
                        selectedCoinForReport.coin,
                        selectedCoinForReport.traderName,
                        selectedCoinForReport.pnl,
                        selectedCoinForReport.winRate
                      );
                    }
                  }}
                  className="mt-3 px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors text-sm"
                >
                  Reintentar
                </button>
              </div>
            )}

            {/* Report content */}
            {coinReport && coinReportSections.length > 0 && !coinReportLoading && (
              <div className="space-y-4">
                {/* Trader context badge */}
                {selectedCoinForReport?.pnl !== undefined && (
                  <div className="flex items-center gap-2 p-3 bg-bg-tertiary rounded-lg">
                    <span className="text-xs text-text-tertiary">Stats del trader:</span>
                    <span className={`text-xs font-medium ${(selectedCoinForReport.pnl ?? 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      PnL ${selectedCoinForReport.pnl?.toLocaleString(undefined, { maximumFractionDigits: 0 })}
                    </span>
                    {selectedCoinForReport.winRate !== undefined && (
                      <span className="text-xs text-text-secondary">
                        | WR {selectedCoinForReport.winRate.toFixed(0)}%
                      </span>
                    )}
                  </div>
                )}

                {/* Rendered sections */}
                {coinReportSections.map((section, index) => {
                  const isRisk = section.title.toLowerCase().includes('riesgo');
                  const isVerdict = section.title.toLowerCase().includes('veredicto');

                  return (
                    <div
                      key={index}
                      className={`p-4 rounded-lg ${
                        isVerdict
                          ? 'bg-primary/10 border border-primary/20'
                          : isRisk
                          ? 'bg-orange-500/10 border border-orange-500/20'
                          : 'bg-bg-tertiary'
                      }`}
                    >
                      <h3 className={`text-sm font-semibold mb-2 ${
                        isVerdict ? 'text-primary' : isRisk ? 'text-orange-400' : 'text-text-primary'
                      }`}>
                        {section.title}
                      </h3>
                      <p className="text-text-secondary text-sm whitespace-pre-line leading-relaxed">
                        {section.content}
                      </p>
                    </div>
                  );
                })}

                {/* Timestamp and disclaimer */}
                <div className="pt-4 border-t border-border">
                  <p className="text-text-tertiary text-[10px]">
                    Generado: {new Date(coinReport.generatedAt).toLocaleString()} | Este reporte es informativo, no constituye consejo financiero.
                  </p>
                </div>
              </div>
            )}

            {/* Close button */}
            <button
              onClick={() => { setModalType('none'); setCoinReport(null); setCoinReportError(null); }}
              className="w-full mt-6 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              Cerrar
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      ) : traders.length === 0 ? (
        <div className="bg-bg-secondary rounded-lg p-8 border border-border text-center">
          <svg className="mx-auto h-12 w-12 text-text-tertiary mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <h3 className="text-lg font-medium text-text-primary mb-2">No hay traders</h3>
          <p className="text-text-secondary mb-6">
            Importa traders de Hyperliquid (datos on-chain reales) o agrega uno manualmente
          </p>
          <div className="flex justify-center gap-2 flex-wrap">
            <button
              onClick={() => setModalType('syncHyperliquid')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 transition-colors"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Hyperliquid
            </button>
            <button
              onClick={() => setModalType('addManual')}
              className="inline-flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Manual
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Top 5 Recomendaciones */}
          {topRecommendations.length > 0 && (
            <div className="mb-6 p-4 bg-bg-secondary rounded-lg border border-border">
              <div className="flex items-center gap-2 mb-4">
                <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
                <h2 className="text-lg font-semibold text-text-primary">Top 5 Recomendados para Copiar</h2>
              </div>
              <p className="text-text-tertiary text-sm mb-4">
                Basado en: ROI equilibrado (10-200%), bajo drawdown (&lt;30%), win rate (&gt;50%), copiers y volumen de trading.
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
                {topRecommendations.map(({ trader, score, reasons }, index) => {
                  const metrics = trader.latest_metrics as Record<string, unknown> | undefined;
                  const platformInfo = getPlatformInfo(trader);
                  return (
                    <button
                      key={trader.id}
                      onClick={() => handleAskCopyJson(trader)}
                      className="relative p-3 bg-bg-tertiary rounded-lg border border-border hover:border-primary hover:bg-bg-tertiary/80 transition-all text-left group"
                      title={`Click para copiar JSON de ${trader.display_name}`}
                    >
                      <div className="absolute -top-2 -left-2 w-6 h-6 bg-yellow-500 text-black text-xs font-bold rounded-full flex items-center justify-center">
                        {index + 1}
                      </div>
                      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        <svg className="h-4 w-4 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`text-xs px-1.5 py-0.5 rounded ${platformInfo.bg} ${platformInfo.color}`}>
                          {platformInfo.icon}
                        </span>
                        <span className="text-sm font-medium text-text-primary truncate" title={trader.display_name}>
                          {trader.display_name.length > 12 ? `${trader.display_name.slice(0, 12)}...` : trader.display_name}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-text-tertiary">Score</span>
                        <span className={`text-sm font-bold ${score >= 70 ? 'text-green-400' : score >= 50 ? 'text-yellow-400' : 'text-orange-400'}`}>
                          {score}/100
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1">
                        {reasons.slice(0, 3).map((reason, i) => (
                          <span key={i} className="text-[10px] px-1.5 py-0.5 bg-primary/20 text-primary rounded">
                            {reason}
                          </span>
                        ))}
                      </div>
                      {/* Top Coins */}
                      {(() => {
                        const topCoins = metrics?.top_coins as Array<{ coin: string; pnl: number; winRate: number }> | undefined;
                        if (!topCoins || topCoins.length === 0) return null;
                        return (
                          <div className="mt-2 pt-2 border-t border-border flex flex-wrap gap-1">
                            {topCoins.slice(0, 3).map((c, i) => (
                              <button
                                key={i}
                                onClick={(e) => { e.stopPropagation(); handleCoinReport(c.coin, trader.display_name, c.pnl, c.winRate, e); }}
                                className="text-[10px] px-1 py-0.5 bg-cyan-500/20 text-cyan-400 rounded hover:ring-1 hover:ring-cyan-400/50 transition-all cursor-pointer"
                                title={`Click: generar reporte AI de ${c.coin}`}
                              >
                                {c.coin}
                              </button>
                            ))}
                          </div>
                        );
                      })()}
                      {metrics?.pnl !== undefined && (
                        <div className="mt-2 pt-2 border-t border-border">
                          <span className={`text-sm font-medium ${(metrics.pnl as number) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            ${((metrics.pnl as number) / 1000).toFixed(1)}k PnL
                          </span>
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
              {topRecommendations.length === 0 && traders.length > 0 && (
                <p className="text-text-tertiary text-sm text-center py-4">
                  No hay traders que cumplan los criterios minimos. Sincroniza datos de Hyperliquid para obtener metricas de validacion.
                </p>
              )}
            </div>
          )}

          {/* Grilla completa */}
          <div className="bg-bg-secondary rounded-lg border border-border overflow-hidden">
            <table className="w-full">
              <thead className="bg-bg-tertiary">
                <tr>
                  <th
                    onClick={() => handleSort('name')}
                    className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center gap-1">
                    Trader
                    {sortConfig.column === 'name' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('platform')}
                  className="px-4 py-3 text-center text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-center gap-1">
                    Fuente
                    {sortConfig.column === 'platform' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-text-secondary uppercase tracking-wider">Perfil</th>
                <th
                  onClick={() => handleSort('roi')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    ROI 30d
                    {sortConfig.column === 'roi' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('drawdown')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    Max DD
                    {sortConfig.column === 'drawdown' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('winrate')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    Win Rate
                    {sortConfig.column === 'winrate' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('copiers')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    Copiers
                    {sortConfig.column === 'copiers' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('trades')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    Trades
                    {sortConfig.column === 'trades' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('days')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    Días
                    {sortConfig.column === 'days' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('pnl')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    PnL
                    {sortConfig.column === 'pnl' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th
                  onClick={() => handleSort('reliable')}
                  className="px-4 py-3 text-center text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-center gap-1">
                    Confiable
                    {sortConfig.column === 'reliable' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Top Coins
                </th>
                <th
                  onClick={() => handleSort('updated')}
                  className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
                >
                  <span className="flex items-center justify-end gap-1">
                    Actualizado
                    {sortConfig.column === 'updated' && (
                      <span className="text-primary">{sortConfig.direction === 'asc' ? '↑' : '↓'}</span>
                    )}
                  </span>
                </th>
                <th className="px-4 py-3 text-center text-xs font-medium text-text-secondary uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {sortedTraders.map((trader) => {
                const metrics = trader.latest_metrics;
                const riskProfile = getRiskProfile(metrics);
                const platformInfo = getPlatformInfo(trader);
                return (
                  <tr key={trader.id} className="hover:bg-bg-tertiary/50 transition-colors cursor-pointer" onClick={() => handleAskCopyJson(trader)}>
                    <td className="px-4 py-4">
                      <div>
                        <div className="text-sm font-medium text-text-primary">{trader.display_name}</div>
                        {trader.trading_style && (
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-primary/20 text-primary mt-1">
                            {trader.trading_style}
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-4 py-4 text-center">
                      <span className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium ${platformInfo.bg} ${platformInfo.color}`}>
                        <span>{platformInfo.icon}</span>
                        {platformInfo.name}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-center">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${riskProfile.bg} ${riskProfile.color} capitalize`}>
                        {riskProfile.level}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-right text-sm">
                      {formatPercent(metrics?.roi_30d_pct)}
                    </td>
                    <td className="px-4 py-4 text-right text-sm">
                      {metrics?.max_drawdown_pct ? (
                        <span className="text-red-400">-{metrics.max_drawdown_pct.toFixed(2)}%</span>
                      ) : '-'}
                    </td>
                    <td className="px-4 py-4 text-right text-sm text-text-primary">
                      {metrics?.win_rate_pct !== undefined ? `${metrics.win_rate_pct.toFixed(1)}%` : '-'}
                    </td>
                    <td className="px-4 py-4 text-right text-sm text-text-primary">
                      {metrics?.copiers !== undefined ? metrics.copiers.toLocaleString() : '-'}
                    </td>
                    <td className="px-4 py-4 text-right text-sm text-text-primary">
                      {(metrics as Record<string, unknown>)?.total_trades !== undefined
                        ? (metrics as Record<string, unknown>).total_trades?.toLocaleString()
                        : '-'}
                    </td>
                    <td className="px-4 py-4 text-right text-sm text-text-primary">
                      {(metrics as Record<string, unknown>)?.days_active !== undefined
                        ? `${(metrics as Record<string, unknown>).days_active}d`
                        : '-'}
                    </td>
                    <td className="px-4 py-4 text-right text-sm">
                      {(metrics as Record<string, unknown>)?.pnl !== undefined ? (
                        <span className={((metrics as Record<string, unknown>).pnl as number) >= 0 ? 'text-green-400' : 'text-red-400'}>
                          ${((metrics as Record<string, unknown>).pnl as number).toLocaleString(undefined, { maximumFractionDigits: 0 })}
                        </span>
                      ) : '-'}
                    </td>
                    <td className="px-4 py-4 text-center">
                      {(metrics as Record<string, unknown>)?.is_reliable !== undefined ? (
                        (metrics as Record<string, unknown>).is_reliable ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                            ✓
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-500/20 text-red-400">
                            ✗
                          </span>
                        )
                      ) : (
                        <span className="text-text-tertiary">-</span>
                      )}
                    </td>
                    <td className="px-4 py-4">
                      {(() => {
                        const topCoins = (metrics as Record<string, unknown>)?.top_coins as Array<{ coin: string; pnl: number; winRate: number }> | undefined;
                        if (!topCoins || topCoins.length === 0) return <span className="text-text-tertiary">-</span>;
                        return (
                          <div className="flex flex-wrap gap-1">
                            {topCoins.slice(0, 3).map((c, i) => (
                              <button
                                key={i}
                                onClick={(e) => handleCoinReport(c.coin, trader.display_name, c.pnl, c.winRate, e)}
                                className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium cursor-pointer hover:ring-1 hover:ring-white/30 transition-all ${
                                  c.pnl >= 0 ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                                }`}
                                title={`Click: reporte AI de ${c.coin} | PnL: $${c.pnl.toLocaleString(undefined, { maximumFractionDigits: 0 })}`}
                              >
                                {c.coin}
                              </button>
                            ))}
                          </div>
                        );
                      })()}
                    </td>
                    <td className="px-4 py-4 text-right text-sm text-text-tertiary">
                      {formatTimeAgo(trader.metrics_updated_at)}
                    </td>
                    <td className="px-4 py-4 text-center">
                      <button
                        onClick={(e) => { e.stopPropagation(); handleAskCopyJson(trader); }}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-primary/20 text-primary rounded-lg hover:bg-primary/30 transition-colors"
                        title="Ver detalle y copiar JSON"
                      >
                        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                        Detalle
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        </>
      )}
    </div>
  );
}
