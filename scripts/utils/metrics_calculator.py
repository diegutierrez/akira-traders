"""
Calculadora de métricas para evaluaciones de traders.

Este módulo proporciona funcionalidades para calcular métricas derivadas,
scores de riesgo y realizar análisis comparativos de traders.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TraderMetrics:
    """Clase para almacenar métricas de un trader."""

    display_name: str
    roi_30d: Optional[float] = None
    roi_90d: Optional[float] = None
    roi_180d: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    avg_leverage: Optional[float] = None
    copiers: Optional[int] = None


class MetricsCalculator:
    """Calculadora de métricas derivadas y scores."""

    # Pesos por perfil de riesgo para el scoring
    SCORING_WEIGHTS = {
        "conservative": {
            "max_drawdown": 0.30,
            "win_rate": 0.25,
            "roi": 0.15,
            "consistency": 0.20,
            "rar": 0.10,
        },
        "moderate": {
            "max_drawdown": 0.25,
            "win_rate": 0.20,
            "roi": 0.25,
            "consistency": 0.15,
            "rar": 0.15,
        },
        "aggressive": {
            "max_drawdown": 0.20,
            "win_rate": 0.15,
            "roi": 0.30,
            "consistency": 0.10,
            "rar": 0.25,
        },
    }

    @staticmethod
    def calculate_risk_adjusted_return(
        roi: float, max_drawdown: float, risk_free_rate: float = 0.0
    ) -> float:
        """
        Calcula el retorno ajustado por riesgo (similar a Sharpe Ratio).

        Args:
            roi: Retorno sobre inversión (%)
            max_drawdown: Máximo drawdown (%)
            risk_free_rate: Tasa libre de riesgo (%, default 0)

        Returns:
            Risk-Adjusted Return (RAR)

        Formula:
            RAR = (ROI - Risk-Free Rate) / Max Drawdown
        """
        if max_drawdown == 0:
            return 0.0

        return (roi - risk_free_rate) / max_drawdown

    @staticmethod
    def calculate_consistency_score(
        roi_30d: Optional[float],
        roi_90d: Optional[float],
        roi_180d: Optional[float] = None,
    ) -> float:
        """
        Calcula un score de consistencia basado en la variación de ROIs.

        Args:
            roi_30d: ROI de 30 días
            roi_90d: ROI de 90 días
            roi_180d: ROI de 180 días (opcional)

        Returns:
            Consistency score (0-1, donde 1 es más consistente)

        Formula:
            Consistency = 1 - (StdDev / Mean)
        """
        rois = [r for r in [roi_30d, roi_90d, roi_180d] if r is not None]

        if len(rois) < 2:
            return 0.5  # Score neutral si no hay suficientes datos

        mean_roi = sum(rois) / len(rois)
        if mean_roi == 0:
            return 0.0

        # Calcular desviación estándar
        variance = sum((r - mean_roi) ** 2 for r in rois) / len(rois)
        std_dev = variance ** 0.5

        # Calcular consistency score
        consistency = 1 - (std_dev / abs(mean_roi))
        return max(0.0, min(1.0, consistency))  # Limitar entre 0 y 1

    @staticmethod
    def calculate_recovery_factor(roi_total: float, max_drawdown: float) -> float:
        """
        Calcula el factor de recuperación.

        Args:
            roi_total: ROI total (%)
            max_drawdown: Máximo drawdown (%)

        Returns:
            Recovery Factor

        Formula:
            Recovery Factor = ROI Total / Max Drawdown
        """
        if max_drawdown == 0:
            return 0.0

        return roi_total / max_drawdown

    @staticmethod
    def normalize_metric(
        value: float,
        min_val: float,
        max_val: float,
        inverse: bool = False,
    ) -> float:
        """
        Normaliza una métrica a escala 0-100.

        Args:
            value: Valor a normalizar
            min_val: Valor mínimo del rango
            max_val: Valor máximo del rango
            inverse: Si True, invierte la escala (menor es mejor)

        Returns:
            Valor normalizado (0-100)
        """
        if max_val == min_val:
            return 50.0

        normalized = (value - min_val) / (max_val - min_val)
        normalized = max(0.0, min(1.0, normalized))

        if inverse:
            normalized = 1.0 - normalized

        return normalized * 100

    def calculate_trader_score(
        self,
        metrics: TraderMetrics,
        risk_profile: str = "moderate",
    ) -> Dict[str, float]:
        """
        Calcula el score total de un trader basado en múltiples métricas.

        Args:
            metrics: Métricas del trader
            risk_profile: Perfil de riesgo (conservative, moderate, aggressive)

        Returns:
            Diccionario con scores individuales y total
        """
        weights = self.SCORING_WEIGHTS.get(risk_profile, self.SCORING_WEIGHTS["moderate"])

        scores = {}

        # Score de Max Drawdown (menor es mejor)
        if metrics.max_drawdown is not None:
            scores["drawdown_score"] = self.normalize_metric(
                metrics.max_drawdown, 0, 50, inverse=True
            )
        else:
            scores["drawdown_score"] = 0.0

        # Score de Win Rate
        if metrics.win_rate is not None:
            scores["win_rate_score"] = self.normalize_metric(
                metrics.win_rate, 40, 80
            )
        else:
            scores["win_rate_score"] = 0.0

        # Score de ROI
        if metrics.roi_90d is not None:
            scores["roi_score"] = self.normalize_metric(
                metrics.roi_90d, 0, 100
            )
        else:
            scores["roi_score"] = 0.0

        # Score de Consistencia
        consistency = self.calculate_consistency_score(
            metrics.roi_30d, metrics.roi_90d, metrics.roi_180d
        )
        scores["consistency_score"] = consistency * 100

        # Score de RAR
        if metrics.roi_90d is not None and metrics.max_drawdown is not None:
            rar = self.calculate_risk_adjusted_return(
                metrics.roi_90d, metrics.max_drawdown
            )
            scores["rar_score"] = self.normalize_metric(rar, 0, 5)
        else:
            scores["rar_score"] = 0.0

        # Calcular score total ponderado
        total_score = (
            scores["drawdown_score"] * weights["max_drawdown"]
            + scores["win_rate_score"] * weights["win_rate"]
            + scores["roi_score"] * weights["roi"]
            + scores["consistency_score"] * weights["consistency"]
            + scores["rar_score"] * weights["rar"]
        )

        scores["total_score"] = round(total_score, 2)

        return scores

    @staticmethod
    def classify_score(score: float) -> Tuple[str, str]:
        """
        Clasifica un score en categorías.

        Args:
            score: Score total (0-100)

        Returns:
            Tupla con (clasificación, recomendación)
        """
        if score >= 85:
            return "Excelente", "Aprobación inmediata"
        elif score >= 70:
            return "Bueno", "Aprobación con revisión"
        elif score >= 55:
            return "Aceptable", "Revisión detallada requerida"
        elif score >= 40:
            return "Marginal", "Rechazar o monitorear"
        else:
            return "Pobre", "Rechazar"

    def compare_traders(
        self,
        traders: List[TraderMetrics],
        risk_profile: str = "moderate",
    ) -> List[Dict[str, any]]:
        """
        Compara múltiples traders y genera un ranking.

        Args:
            traders: Lista de métricas de traders
            risk_profile: Perfil de riesgo

        Returns:
            Lista de traders ordenados por score (mayor a menor)
        """
        results = []

        for trader in traders:
            scores = self.calculate_trader_score(trader, risk_profile)
            classification, recommendation = self.classify_score(
                scores["total_score"]
            )

            results.append({
                "trader": trader.display_name,
                "total_score": scores["total_score"],
                "classification": classification,
                "recommendation": recommendation,
                "scores": scores,
                "metrics": {
                    "roi_90d": trader.roi_90d,
                    "max_drawdown": trader.max_drawdown,
                    "win_rate": trader.win_rate,
                    "avg_leverage": trader.avg_leverage,
                },
            })

        # Ordenar por score total (mayor a menor)
        results.sort(key=lambda x: x["total_score"], reverse=True)

        return results

    @staticmethod
    def calculate_portfolio_metrics(
        traders: List[Dict[str, any]],
        allocations: Optional[List[float]] = None,
    ) -> Dict[str, float]:
        """
        Calcula métricas agregadas de un portafolio de traders.

        Args:
            traders: Lista de traders con sus métricas
            allocations: Lista de asignaciones (%, suma debe ser 100)

        Returns:
            Diccionario con métricas del portafolio
        """
        if not traders:
            return {}

        n = len(traders)

        # Si no se proporcionan asignaciones, usar distribución igual
        if allocations is None:
            allocations = [100 / n] * n

        # Normalizar asignaciones
        total_allocation = sum(allocations)
        if total_allocation > 0:
            allocations = [a / total_allocation for a in allocations]

        # Calcular métricas ponderadas
        weighted_roi = 0.0
        weighted_dd = 0.0
        weighted_wr = 0.0
        weighted_leverage = 0.0

        for trader, allocation in zip(traders, allocations):
            metrics = trader.get("metrics", {})
            weighted_roi += metrics.get("roi_90d", 0) * allocation
            weighted_dd += metrics.get("max_drawdown", 0) * allocation
            weighted_wr += metrics.get("win_rate", 0) * allocation
            weighted_leverage += metrics.get("avg_leverage", 0) * allocation

        return {
            "portfolio_roi_90d": round(weighted_roi, 2),
            "portfolio_max_dd": round(weighted_dd, 2),
            "portfolio_win_rate": round(weighted_wr, 2),
            "portfolio_avg_leverage": round(weighted_leverage, 2),
            "num_traders": n,
        }

    @staticmethod
    def estimate_slippage(trading_style: str) -> Tuple[float, float]:
        """
        Estima el slippage esperado según el estilo de trading.

        Args:
            trading_style: Estilo de trading (scalping, swing, trend-following, etc.)

        Returns:
            Tupla con (slippage_min, slippage_max) en porcentaje
        """
        slippage_estimates = {
            "scalping": (0.5, 2.0),
            "swing": (0.1, 0.5),
            "trend-following": (0.05, 0.2),
            "arbitrage": (0.1, 0.3),
            "mixed": (0.2, 0.8),
        }

        return slippage_estimates.get(trading_style, (0.1, 0.5))

    def __repr__(self) -> str:
        """Representación en string del calculador."""
        return "MetricsCalculator()"