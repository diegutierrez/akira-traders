/**
 * Servicio para ejecutar scripts de Python desde el frontend
 *
 * Este servicio proporciona una interfaz para ejecutar los scripts de validación,
 * análisis y consolidación de traders.
 */

import { TraderEvaluation, TraderAnalysis, ConsolidatedReport, ValidationResult } from '@/types/trader';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api';

/**
 * Obtiene los headers con autenticación si está disponible
 */
function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

/**
 * Valida una evaluación de trader usando el script validate.py
 */
export async function validateTraderEvaluation(
  evaluation: TraderEvaluation
): Promise<ValidationResult> {
  try {
    const response = await fetch(`${API_URL}/validate`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(evaluation),
    });

    if (!response.ok) {
      throw new Error(`Error en validación: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al validar evaluación:', error);
    throw error;
  }
}

/**
 * Analiza las métricas de un trader usando el script analyze_metrics.py
 */
export async function analyzeTraderMetrics(
  evaluation: TraderEvaluation,
  riskProfile?: string
): Promise<TraderAnalysis> {
  try {
    const response = await fetch(`${API_URL}/analyze`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        evaluation,
        risk_profile: riskProfile || evaluation.risk_profile,
      }),
    });

    if (!response.ok) {
      throw new Error(`Error en análisis: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al analizar métricas:', error);
    throw error;
  }
}

/**
 * Analiza múltiples traders y genera un ranking
 */
export async function analyzeMultipleTraders(
  evaluations: TraderEvaluation[],
  riskProfile?: string
): Promise<{
  ranking: TraderAnalysis[];
  portfolio_metrics: any;
}> {
  try {
    const response = await fetch(`${API_URL}/analyze/multiple`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        evaluations,
        risk_profile: riskProfile,
      }),
    });

    if (!response.ok) {
      throw new Error(`Error en análisis múltiple: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al analizar múltiples traders:', error);
    throw error;
  }
}

/**
 * Consolida evaluaciones usando el script consolidate.py
 */
export async function consolidateEvaluations(
  month?: string,
  riskProfile?: string
): Promise<ConsolidatedReport> {
  try {
    const params = new URLSearchParams();
    if (month) params.append('month', month);
    if (riskProfile) params.append('profile', riskProfile);

    const response = await fetch(`${API_URL}/consolidate?${params.toString()}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Error en consolidación: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al consolidar evaluaciones:', error);
    throw error;
  }
}

/**
 * Obtiene todas las evaluaciones almacenadas
 */
export async function getAllEvaluations(): Promise<TraderEvaluation[]> {
  try {
    const response = await fetch(`${API_URL}/evaluations`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Error al obtener evaluaciones: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al obtener evaluaciones:', error);
    throw error;
  }
}

/**
 * Guarda una nueva evaluación
 */
export async function saveEvaluation(
  evaluation: TraderEvaluation
): Promise<{ success: boolean; message: string; filename?: string }> {
  try {
    const response = await fetch(`${API_URL}/evaluations`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(evaluation),
    });

    if (response.status === 401) {
      throw new Error('No autorizado - Inicia sesión nuevamente');
    }

    if (!response.ok) {
      throw new Error(`Error al guardar evaluación: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al guardar evaluación:', error);
    throw error;
  }
}

/**
 * Actualiza una evaluación existente
 */
export async function updateEvaluation(
  filename: string,
  evaluation: TraderEvaluation
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_URL}/evaluations/${filename}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(evaluation),
    });

    if (response.status === 401) {
      throw new Error('No autorizado - Inicia sesión nuevamente');
    }

    if (!response.ok) {
      throw new Error(`Error al actualizar evaluación: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al actualizar evaluación:', error);
    throw error;
  }
}

/**
 * Elimina una evaluación
 */
export async function deleteEvaluation(
  filename: string
): Promise<{ success: boolean; message: string }> {
  try {
    const response = await fetch(`${API_URL}/evaluations/${filename}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (response.status === 401) {
      throw new Error('No autorizado - Inicia sesión nuevamente');
    }

    if (!response.ok) {
      throw new Error(`Error al eliminar evaluación: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error al eliminar evaluación:', error);
    throw error;
  }
}
