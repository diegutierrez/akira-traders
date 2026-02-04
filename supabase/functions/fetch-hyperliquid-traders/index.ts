import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const HYPERLIQUID_INFO_API = "https://api.hyperliquid.xyz/info";
const HYPERLIQUID_LEADERBOARD_URL = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

interface WindowPerformance {
  pnl: string;
  roi: string;
  vlm: string;
}

interface LeaderboardEntry {
  ethAddress: string;
  accountValue: string;
  displayName?: string | null;
  windowPerformances: [string, WindowPerformance][];
}

// Helper para extraer métricas de windowPerformances
function getPerformance(entry: LeaderboardEntry, window: string = "allTime"): { pnl: number; roi: number; vlm: number } {
  const perf = entry.windowPerformances?.find(([w]) => w === window);
  if (!perf) return { pnl: 0, roi: 0, vlm: 0 };
  return {
    pnl: parseFloat(perf[1].pnl) || 0,
    roi: parseFloat(perf[1].roi) || 0,
    vlm: parseFloat(perf[1].vlm) || 0,
  };
}

interface TraderValidation {
  address: string;
  isReliable: boolean;
  reasons: string[];
  metrics: {
    accountAge: number; // días desde primer trade
    totalTrades: number;
    winRate: number;
    avgTradeSize: number;
    largestWinPct: number; // % del PnL total del mayor trade
    diversification: number; // número de coins distintos
  };
}

interface UserFill {
  coin: string;
  px: string;
  sz: string;
  side: string;
  time: number;
  closedPnl: string;
  dir: string;
  hash: string;
  fee: string;
}

// Obtener historial de fills de un trader
async function getUserFills(address: string, limit = 500): Promise<UserFill[]> {
  try {
    const response = await fetch(HYPERLIQUID_INFO_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "userFills",
        user: address,
      }),
    });

    if (!response.ok) return [];

    const fills = await response.json();
    return Array.isArray(fills) ? fills.slice(0, limit) : [];
  } catch {
    return [];
  }
}

// Obtener estado de la cuenta
async function getUserState(address: string): Promise<any> {
  try {
    const response = await fetch(HYPERLIQUID_INFO_API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        type: "clearinghouseState",
        user: address,
      }),
    });

    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

// Calcular PnL por moneda y retornar top performers
interface CoinPerformance {
  coin: string;
  pnl: number;
  trades: number;
  winRate: number;
}

function calculateTopCoins(fills: UserFill[], limit = 3): CoinPerformance[] {
  const coinStats: Record<string, { pnl: number; wins: number; total: number }> = {};

  for (const fill of fills) {
    const pnl = parseFloat(fill.closedPnl) || 0;
    if (pnl === 0) continue; // Solo trades cerrados

    if (!coinStats[fill.coin]) {
      coinStats[fill.coin] = { pnl: 0, wins: 0, total: 0 };
    }

    coinStats[fill.coin].pnl += pnl;
    coinStats[fill.coin].total += 1;
    if (pnl > 0) coinStats[fill.coin].wins += 1;
  }

  // Convertir a array y ordenar por PnL
  const coinPerformances: CoinPerformance[] = Object.entries(coinStats)
    .map(([coin, stats]) => ({
      coin,
      pnl: stats.pnl,
      trades: stats.total,
      winRate: stats.total > 0 ? (stats.wins / stats.total) * 100 : 0,
    }))
    .sort((a, b) => b.pnl - a.pnl)
    .slice(0, limit);

  return coinPerformances;
}

// Calcular drawdown máximo desde fills
function calculateMaxDrawdown(fills: UserFill[]): number {
  if (fills.length === 0) return 0;

  // Ordenar por tiempo
  const sortedFills = [...fills].sort((a, b) => a.time - b.time);

  // Calcular curva de PnL acumulado
  let cumulativePnl = 0;
  let peak = 0;
  let maxDrawdown = 0;

  for (const fill of sortedFills) {
    const pnl = parseFloat(fill.closedPnl) || 0;
    cumulativePnl += pnl;

    if (cumulativePnl > peak) {
      peak = cumulativePnl;
    }

    if (peak > 0) {
      const drawdown = ((peak - cumulativePnl) / peak) * 100;
      if (drawdown > maxDrawdown) {
        maxDrawdown = drawdown;
      }
    }
  }

  return maxDrawdown;
}

// Validar trader basado en su historial
async function validateTrader(address: string, leaderboardPnl: number): Promise<TraderValidation & { maxDrawdown: number; topCoins: CoinPerformance[] }> {
  const fills = await getUserFills(address, 1000);

  const validation: TraderValidation & { maxDrawdown: number; topCoins: CoinPerformance[] } = {
    address,
    isReliable: true,
    reasons: [],
    maxDrawdown: 0,
    topCoins: [],
    metrics: {
      accountAge: 0,
      totalTrades: fills.length,
      winRate: 0,
      avgTradeSize: 0,
      largestWinPct: 0,
      diversification: 0,
    },
  };

  if (fills.length === 0) {
    validation.isReliable = false;
    validation.reasons.push("No trade history available");
    return validation;
  }

  // Calcular edad de la cuenta (días desde primer trade)
  const timestamps = fills.map((f) => f.time);
  const oldestTrade = Math.min(...timestamps);
  const newestTrade = Math.max(...timestamps);
  const accountAgeMs = Date.now() - oldestTrade;
  validation.metrics.accountAge = Math.floor(accountAgeMs / (1000 * 60 * 60 * 24));

  // Calcular win rate
  const closedTrades = fills.filter((f) => parseFloat(f.closedPnl) !== 0);
  const wins = closedTrades.filter((f) => parseFloat(f.closedPnl) > 0);
  validation.metrics.winRate = closedTrades.length > 0
    ? (wins.length / closedTrades.length) * 100
    : 0;

  // Calcular diversificación (coins únicos)
  const uniqueCoins = new Set(fills.map((f) => f.coin));
  validation.metrics.diversification = uniqueCoins.size;

  // Calcular el % del PnL que viene del mayor trade
  if (closedTrades.length > 0 && leaderboardPnl > 0) {
    const pnls = closedTrades.map((f) => parseFloat(f.closedPnl));
    const maxPnl = Math.max(...pnls);
    validation.metrics.largestWinPct = (maxPnl / leaderboardPnl) * 100;
  }

  // Calcular tamaño promedio de trade
  const tradeSizes = fills.map((f) => parseFloat(f.sz) * parseFloat(f.px));
  validation.metrics.avgTradeSize = tradeSizes.reduce((a, b) => a + b, 0) / tradeSizes.length;

  // Calcular max drawdown
  validation.maxDrawdown = calculateMaxDrawdown(fills);

  // Calcular mejores monedas
  validation.topCoins = calculateTopCoins(fills, 3);

  // Aplicar filtros de fiabilidad

  // 1. Cuenta muy nueva (< 30 días)
  if (validation.metrics.accountAge < 30) {
    validation.isReliable = false;
    validation.reasons.push(`Account too new: ${validation.metrics.accountAge} days`);
  }

  // 2. Muy pocos trades (< 50)
  if (validation.metrics.totalTrades < 50) {
    validation.isReliable = false;
    validation.reasons.push(`Too few trades: ${validation.metrics.totalTrades}`);
  }

  // 3. PnL depende mucho de un solo trade (> 40%)
  if (validation.metrics.largestWinPct > 40) {
    validation.isReliable = false;
    validation.reasons.push(`PnL too dependent on single trade: ${validation.metrics.largestWinPct.toFixed(1)}%`);
  }

  // 4. Poca diversificación (< 3 coins)
  if (validation.metrics.diversification < 3) {
    validation.isReliable = false;
    validation.reasons.push(`Low diversification: only ${validation.metrics.diversification} coins`);
  }

  // 5. Win rate sospechosamente alto (> 90%) o muy bajo (< 30%)
  if (validation.metrics.winRate > 90) {
    validation.reasons.push(`Suspiciously high win rate: ${validation.metrics.winRate.toFixed(1)}%`);
    // No marcamos como unreliable, solo warning
  }

  return validation;
}

// Obtener leaderboard
async function fetchLeaderboard(): Promise<LeaderboardEntry[]> {
  const response = await fetch(HYPERLIQUID_LEADERBOARD_URL);

  if (!response.ok) {
    throw new Error(`Failed to fetch leaderboard: ${response.status}`);
  }

  const data = await response.json();
  return data.leaderboardRows || data || [];
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const url = new URL(req.url);
    const limit = parseInt(url.searchParams.get("limit") || "20");
    const validate = url.searchParams.get("validate") === "true";
    const minPnl = parseFloat(url.searchParams.get("minPnl") || "0");
    const minRoi = parseFloat(url.searchParams.get("minRoi") || "0");

    console.log(`Fetching Hyperliquid leaderboard: limit=${limit}, validate=${validate}`);

    // Obtener leaderboard
    const leaderboard = await fetchLeaderboard();

    // Filtrar por criterios básicos usando allTime performance
    let filtered = leaderboard
      .filter((entry) => {
        const perf = getPerformance(entry, "allTime");
        return perf.pnl >= minPnl && perf.roi >= minRoi;
      })
      .slice(0, validate ? Math.min(limit, 50) : limit); // Limitar si validamos (es lento)

    // Mapear a formato de respuesta
    const traders = await Promise.all(
      filtered.map(async (entry, index) => {
        const allTimePerf = getPerformance(entry, "allTime");
        const monthPerf = getPerformance(entry, "month");

        const trader: any = {
          id: entry.ethAddress,
          display_name: entry.displayName || `Trader ${entry.ethAddress.slice(0, 8)}`,
          platform_uid: entry.ethAddress,
          profile_url: `https://app.hyperliquid.xyz/leaderboard/${entry.ethAddress}`,
          platform: "hyperliquid",
          rank: index + 1,
          metrics: {
            roi_pct: allTimePerf.roi * 100, // Convertir de decimal a porcentaje
            pnl: allTimePerf.pnl,
            aum: parseFloat(entry.accountValue) || 0,
            volume: allTimePerf.vlm,
            // Métricas del mes para comparación
            roi_month_pct: monthPerf.roi * 100,
            pnl_month: monthPerf.pnl,
            // Estos se calculan en validación o se dejan en 0
            win_rate_pct: 0,
            drawdown_pct: 0,
            copiers: 0,
          },
        };

        // Validación opcional (más lenta pero más datos)
        if (validate) {
          const validation = await validateTrader(entry.ethAddress, allTimePerf.pnl);
          trader.validation = validation;
          trader.metrics.win_rate_pct = validation.metrics.winRate;
          trader.metrics.drawdown_pct = validation.maxDrawdown;
          trader.is_reliable = validation.isReliable;
        }

        return trader;
      })
    );

    // Si validamos, ordenar por fiabilidad
    if (validate) {
      traders.sort((a, b) => {
        if (a.is_reliable && !b.is_reliable) return -1;
        if (!a.is_reliable && b.is_reliable) return 1;
        return b.metrics.pnl - a.metrics.pnl;
      });
    }

    return new Response(
      JSON.stringify({
        success: true,
        count: traders.length,
        validated: validate,
        traders,
      }),
      {
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Error fetching Hyperliquid traders:", error);

    return new Response(
      JSON.stringify({
        success: false,
        error: error.message || "Unknown error",
      }),
      {
        status: 500,
        headers: {
          ...corsHeaders,
          "Content-Type": "application/json",
        },
      }
    );
  }
});
