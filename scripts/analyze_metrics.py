#!/usr/bin/env python3
"""
Script de análisis de métricas de traders.

Este script analiza las métricas de uno o más traders, calcula scores,
genera rankings y proporciona recomendaciones de asignación.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from utils.metrics_calculator import MetricsCalculator, TraderMetrics


def load_evaluation(filepath: Path) -> Dict[str, Any]:
    """
    Carga una evaluación desde un archivo JSON.

    Args:
        filepath: Ruta al archivo JSON

    Returns:
        Diccionario con los datos de la evaluación

    Raises:
        FileNotFoundError: Si el archivo no existe
        json.JSONDecodeError: Si el archivo no es JSON válido
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_metrics(evaluation: Dict[str, Any]) -> TraderMetrics:
    """
    Extrae las métricas de una evaluación.

    Args:
        evaluation: Diccionario con la evaluación

    Returns:
        Objeto TraderMetrics con las métricas extraídas
    """
    candidate = evaluation.get("candidate", {})
    metrics = candidate.get("metrics", {})

    return TraderMetrics(
        display_name=candidate.get("display_name", "Unknown"),
        roi_30d=metrics.get("roi_30d_pct"),
        roi_90d=metrics.get("roi_90d_pct"),
        roi_180d=metrics.get("roi_180d_pct"),
        max_drawdown=metrics.get("max_drawdown_pct"),
        win_rate=metrics.get("win_rate_pct"),
        avg_leverage=metrics.get("avg_leverage"),
        copiers=metrics.get("copiers"),
    )


def analyze_single_trader(
    filepath: Path,
    risk_profile: str = "moderate",
    verbose: bool = False,
) -> None:
    """
    Analiza un solo trader y muestra los resultados.

    Args:
        filepath: Ruta al archivo de evaluación
        risk_profile: Perfil de riesgo a usar
        verbose: Si es True, muestra información detallada
    """
    try:
        # Cargar evaluación
        evaluation = load_evaluation(filepath)
        metrics = extract_metrics(evaluation)

        # Calcular scores
        calculator = MetricsCalculator()
        scores = calculator.calculate_trader_score(metrics, risk_profile)
        classification, recommendation = calculator.classify_score(
            scores["total_score"]
        )

        # Mostrar resultados
        print(f"\n{'='*70}")
        print(f"ANÁLISIS DE TRADER: {metrics.display_name}")
        print(f"{'='*70}\n")

        print(f"📊 Perfil de Riesgo: {risk_profile.upper()}")
        print(f"📅 Fecha de Evaluación: {evaluation.get('as_of_utc', 'N/A')}\n")

        print("📈 MÉTRICAS PRINCIPALES:")
        print(f"  • ROI 90d: {metrics.roi_90d}%")
        print(f"  • Max Drawdown: {metrics.max_drawdown}%")
        print(f"  • Win Rate: {metrics.win_rate}%")
        print(f"  • Leverage Promedio: {metrics.avg_leverage}×")
        print(f"  • Copiadores: {metrics.copiers}\n")

        print("🎯 SCORES CALCULADOS:")
        print(f"  • Drawdown Score: {scores['drawdown_score']:.2f}/100")
        print(f"  • Win Rate Score: {scores['win_rate_score']:.2f}/100")
        print(f"  • ROI Score: {scores['roi_score']:.2f}/100")
        print(f"  • Consistency Score: {scores['consistency_score']:.2f}/100")
        print(f"  • RAR Score: {scores['rar_score']:.2f}/100\n")

        print(f"⭐ SCORE TOTAL: {scores['total_score']:.2f}/100")
        print(f"📋 Clasificación: {classification}")
        print(f"💡 Recomendación: {recommendation}\n")

        # Métricas derivadas
        if metrics.roi_90d and metrics.max_drawdown:
            rar = calculator.calculate_risk_adjusted_return(
                metrics.roi_90d, metrics.max_drawdown
            )
            recovery = calculator.calculate_recovery_factor(
                metrics.roi_90d, metrics.max_drawdown
            )
            consistency = calculator.calculate_consistency_score(
                metrics.roi_30d, metrics.roi_90d, metrics.roi_180d
            )

            print("📊 MÉTRICAS DERIVADAS:")
            print(f"  • Risk-Adjusted Return: {rar:.2f}")
            print(f"  • Recovery Factor: {recovery:.2f}")
            print(f"  • Consistency Score: {consistency:.2f}\n")

        # Estimación de slippage
        style = evaluation.get("candidate", {}).get("style", "mixed")
        slippage_min, slippage_max = calculator.estimate_slippage(style)
        print(f"⚠️  SLIPPAGE ESTIMADO ({style}):")
        print(f"  • Rango: {slippage_min}% - {slippage_max}%\n")

        print(f"{'='*70}\n")

    except Exception as e:
        print(f"❌ Error al analizar trader: {e}", file=sys.stderr)
        sys.exit(1)


def analyze_multiple_traders(
    filepaths: List[Path],
    risk_profile: str = "moderate",
    output_file: Path = None,
) -> None:
    """
    Analiza múltiples traders y genera un ranking.

    Args:
        filepaths: Lista de rutas a archivos de evaluación
        risk_profile: Perfil de riesgo a usar
        output_file: Archivo de salida para el reporte (opcional)
    """
    try:
        # Cargar todas las evaluaciones
        traders_metrics = []
        evaluations = []

        for filepath in filepaths:
            try:
                evaluation = load_evaluation(filepath)
                metrics = extract_metrics(evaluation)
                traders_metrics.append(metrics)
                evaluations.append(evaluation)
            except Exception as e:
                print(f"⚠️  Error al cargar {filepath}: {e}", file=sys.stderr)
                continue

        if not traders_metrics:
            print("❌ No se pudieron cargar traders válidos", file=sys.stderr)
            sys.exit(1)

        # Comparar traders
        calculator = MetricsCalculator()
        results = calculator.compare_traders(traders_metrics, risk_profile)

        # Mostrar ranking
        print(f"\n{'='*70}")
        print(f"RANKING DE TRADERS - Perfil: {risk_profile.upper()}")
        print(f"{'='*70}\n")

        print(f"Total de traders analizados: {len(results)}\n")

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['trader']}")
            print(f"   Score: {result['total_score']:.2f}/100 - {result['classification']}")
            print(f"   ROI 90d: {result['metrics']['roi_90d']}% | "
                  f"Max DD: {result['metrics']['max_drawdown']}% | "
                  f"Win Rate: {result['metrics']['win_rate']}%")
            print(f"   → {result['recommendation']}\n")

        # Calcular métricas del portafolio
        portfolio_metrics = calculator.calculate_portfolio_metrics(results)

        print(f"{'='*70}")
        print("MÉTRICAS DEL PORTAFOLIO (distribución igual)")
        print(f"{'='*70}\n")
        print(f"  • ROI 90d Promedio: {portfolio_metrics['portfolio_roi_90d']}%")
        print(f"  • Max DD Promedio: {portfolio_metrics['portfolio_max_dd']}%")
        print(f"  • Win Rate Promedio: {portfolio_metrics['portfolio_win_rate']}%")
        print(f"  • Leverage Promedio: {portfolio_metrics['portfolio_avg_leverage']}×")
        print(f"  • Número de Traders: {portfolio_metrics['num_traders']}\n")

        # Recomendaciones de asignación
        print(f"{'='*70}")
        print("RECOMENDACIONES DE ASIGNACIÓN")
        print(f"{'='*70}\n")

        approved = [r for r in results if r['total_score'] >= 70]
        if approved:
            print(f"Traders aprobados: {len(approved)}\n")
            for trader in approved[:5]:  # Top 5
                allocation = min(30, 100 / len(approved))
                print(f"  • {trader['trader']}: {allocation:.1f}% del portafolio")
                print(f"    (Score: {trader['total_score']:.2f})\n")
        else:
            print("⚠️  No hay traders que cumplan el criterio mínimo (score >= 70)\n")

        print(f"{'='*70}\n")

        # Guardar resultados si se especifica archivo de salida
        if output_file:
            output_data = {
                "analysis_date": datetime.utcnow().isoformat() + "Z",
                "risk_profile": risk_profile,
                "total_traders": len(results),
                "ranking": results,
                "portfolio_metrics": portfolio_metrics,
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            print(f"✅ Resultados guardados en: {output_file}\n")

    except Exception as e:
        print(f"❌ Error al analizar traders: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Analiza métricas de traders y genera rankings",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Analizar un solo trader
  %(prog)s evaluations/2025-01/trader_example.json

  # Analizar múltiples traders
  %(prog)s evaluations/2025-01/*.json

  # Especificar perfil de riesgo
  %(prog)s --profile aggressive evaluations/2025-01/*.json

  # Guardar resultados en archivo
  %(prog)s --output analysis.json evaluations/2025-01/*.json
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Archivo(s) JSON de evaluación",
    )

    parser.add_argument(
        "-p",
        "--profile",
        choices=["conservative", "moderate", "aggressive"],
        default="moderate",
        help="Perfil de riesgo (default: moderate)",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Archivo de salida para resultados JSON",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Muestra información detallada",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()

    # Analizar traders
    if len(args.files) == 1:
        analyze_single_trader(args.files[0], args.profile, args.verbose)
    else:
        analyze_multiple_traders(args.files, args.profile, args.output)


if __name__ == "__main__":
    main()