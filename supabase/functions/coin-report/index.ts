import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const GEMINI_API_URL =
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type",
};

// Retry con exponential backoff para manejar rate limits (429)
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(url, options);

    if (response.status === 429 && attempt < maxRetries) {
      // Esperar con backoff exponencial: 2s, 4s, 8s + jitter
      const delay = Math.pow(2, attempt + 1) * 1000 + Math.random() * 1000;
      console.log(
        `Rate limited (429). Retry ${attempt + 1}/${maxRetries} in ${Math.round(delay)}ms`
      );
      await new Promise((resolve) => setTimeout(resolve, delay));
      continue;
    }

    return response;
  }

  // No deberia llegar aqui, pero por seguridad
  throw new Error("Max retries exceeded");
}

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const apiKey = Deno.env.get("GEMINI_API_KEY");
    if (!apiKey) {
      return new Response(
        JSON.stringify({
          success: false,
          error: "GEMINI_API_KEY not configured",
        }),
        {
          status: 500,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const url = new URL(req.url);
    const coin = url.searchParams.get("coin");
    if (!coin) {
      return new Response(
        JSON.stringify({
          success: false,
          error: "coin parameter is required",
        }),
        {
          status: 400,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const traderName = url.searchParams.get("traderName") || "";
    const pnl = url.searchParams.get("pnl") || "";
    const winRate = url.searchParams.get("winRate") || "";

    let statsLine = "";
    if (traderName && pnl) {
      statsLine = `\nContexto: El trader "${traderName}" tiene PnL $${pnl} y Win Rate ${winRate}% operando ${coin} en Hyperliquid.\n`;
    }

    const prompt = `Eres un analista experto de criptomonedas especializado en trading de perpetuos en Hyperliquid DEX.

Analiza la criptomoneda ${coin} para evaluar si es viable para copy trading de perpetuos.
${statsLine}
Responde EXACTAMENTE con estas secciones (usa estos encabezados exactos):

## Descripcion
Que es ${coin}, su proposito, ecosistema y caso de uso principal. Maximo 3 oraciones.

## Analisis de Mercado
Market cap aproximado, volumen 24h, tendencia actual (alcista/bajista/lateral), y contexto del mercado.

## Nivel de Riesgo
Clasifica como: BAJO / MEDIO / ALTO / MUY ALTO. Explica por que en 2-3 oraciones.

## Perpetuos en Hyperliquid
Es buena moneda para operar en perpetuos? Liquidez, spread, volatilidad, y consideraciones especificas de Hyperliquid.

## Soporte y Resistencia
Niveles clave actuales de soporte y resistencia. Si no hay datos confiables recientes, indicar.

## Veredicto
Recomendacion final en 1-2 oraciones para un copy trader.`;

    console.log(`Generating coin report for: ${coin}`);

    const geminiResponse = await fetchWithRetry(
      `${GEMINI_API_URL}?key=${apiKey}`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: prompt }] }],
        }),
      },
      3
    );

    if (!geminiResponse.ok) {
      const errorText = await geminiResponse.text();
      console.error("Gemini API error:", errorText);

      const errorMsg =
        geminiResponse.status === 429
          ? "Limite de requests alcanzado. Espera unos segundos e intenta de nuevo."
          : `Gemini API error: ${geminiResponse.status}`;

      return new Response(
        JSON.stringify({
          success: false,
          error: errorMsg,
        }),
        {
          status: 502,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    const geminiData = await geminiResponse.json();
    const report =
      geminiData.candidates?.[0]?.content?.parts?.[0]?.text || "";

    if (!report) {
      return new Response(
        JSON.stringify({
          success: false,
          error: "Empty response from Gemini",
        }),
        {
          status: 502,
          headers: { ...corsHeaders, "Content-Type": "application/json" },
        }
      );
    }

    return new Response(
      JSON.stringify({
        success: true,
        report,
        coin,
        generatedAt: new Date().toISOString(),
      }),
      {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  } catch (error) {
    console.error("Error generating coin report:", error);
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message || "Unknown error",
      }),
      {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      }
    );
  }
});
