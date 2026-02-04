/**
 * Servicio para generar reportes de monedas usando Gemini AI
 */

const EDGE_FUNCTION_URL = `${import.meta.env.VITE_SUPABASE_URL}/functions/v1/coin-report`;

export interface CoinReport {
  report: string;
  coin: string;
  generatedAt: string;
}

export interface CoinReportParams {
  coin: string;
  traderName?: string;
  pnl?: number;
  winRate?: number;
}

export interface ReportSection {
  title: string;
  content: string;
}

/**
 * Llama al edge function para generar un reporte de moneda con Gemini
 */
export async function fetchCoinReport(params: CoinReportParams): Promise<CoinReport> {
  const searchParams = new URLSearchParams({ coin: params.coin });

  if (params.traderName) searchParams.set('traderName', params.traderName);
  if (params.pnl !== undefined) searchParams.set('pnl', params.pnl.toString());
  if (params.winRate !== undefined) searchParams.set('winRate', params.winRate.toString());

  const response = await fetch(`${EDGE_FUNCTION_URL}?${searchParams}`);
  const data = await response.json();

  if (!data.success) {
    throw new Error(data.error || 'Error al generar reporte de moneda');
  }

  return {
    report: data.report,
    coin: data.coin,
    generatedAt: data.generatedAt,
  };
}

/**
 * Parsea el reporte markdown en secciones estructuradas
 */
export function parseReportSections(report: string): ReportSection[] {
  const sections: ReportSection[] = [];
  const parts = report.split(/^## /m).filter(Boolean);

  for (const part of parts) {
    const newlineIndex = part.indexOf('\n');
    if (newlineIndex === -1) continue;

    const title = part.substring(0, newlineIndex).trim();
    const content = part.substring(newlineIndex + 1).trim();
    sections.push({ title, content });
  }

  return sections;
}
