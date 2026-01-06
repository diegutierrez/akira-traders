#!/usr/bin/env python3
"""
Script de consolidación de evaluaciones de traders.

Este script consolida múltiples evaluaciones en un reporte unificado,
generando vistas agregadas y comparativas del portafolio.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from collections import defaultdict

from utils.metrics_calculator import MetricsCalculator, TraderMetrics


def load_evaluations_from_directory(
    directory: Path,
    pattern: str = "*.json",
) -> List[Dict[str, Any]]:
    """
    Carga todas las evaluaciones de un directorio.

    Args:
        directory: Directorio con archivos de evaluación
        pattern: Patrón de archivos a buscar

    Returns:
        Lista de evaluaciones cargadas
    """
    evaluations = []
    
    if not directory.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {directory}")

    for filepath in directory.glob(pattern):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["_source_file"] = filepath.name
                evaluations.append(data)
        except Exception as e:
            print(f"⚠️  Error al cargar {filepath.name}: {e}", file=sys.stderr)
            continue

    return evaluations


def group_by_risk_profile(
    evaluations: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Agrupa evaluaciones por perfil de riesgo.

    Args:
        evaluations: Lista de evaluaciones

    Returns:
        Diccionario con evaluaciones agrupadas por perfil
    """
    grouped = defaultdict(list)
    
    for evaluation in evaluations:
        profile = evaluation.get("risk_profile", "unknown")
        grouped[profile].append(evaluation)
    
    return dict(grouped)


def generate_summary_statistics(
    evaluations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Genera estadísticas resumidas de las evaluaciones.

    Args:
        evaluations: Lista de evaluaciones

    Returns:
        Diccionario con estadísticas
    """
    if not evaluations:
        return {}

    # Extraer métricas
    rois = []
    drawdowns = []
    win_rates = []
    leverages = []
    copiers = []

    for evaluation in evaluations:
        metrics = evaluation.get("candidate", {}).get("metrics", {})
        
        if metrics.get("roi_90d_pct") is not None:
            rois.append(metrics["roi_90d_pct"])
        if metrics.get("max_drawdown_pct") is not None:
            drawdowns.append(metrics["max_drawdown_pct"])
        if metrics.get("win_rate_pct") is not None:
            win_rates.append(metrics["win_rate_pct"])
        if metrics.get("avg_leverage") is not None:
            leverages.append(metrics["avg_leverage"])
        if metrics.get("copiers") is not None:
            copiers.append(metrics["copiers"])

    def calc_stats(values: List[float]) -> Dict[str, float]:
        """Calcula estadísticas básicas."""
        if not values:
            return {"min": 0, "max": 0, "avg": 0, "median": 0}
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        return {
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "avg": round(sum(values) / n, 2),
            "median": round(sorted_values[n // 2], 2),
        }

    return {
        "total_traders": len(evaluations),
        "roi_90d": calc_stats(rois),
        "max_drawdown": calc_stats(drawdowns),
        "win_rate": calc_stats(win_rates),
        "avg_leverage": calc_stats(leverages),
        "copiers": calc_stats(copiers),
    }


def generate_consolidated_report(
    evaluations: List[Dict[str, Any]],
    output_file: Path,
    risk_profile: str = None,
) -> None:
    """
    Genera un reporte consolidado de evaluaciones.

    Args:
        evaluations: Lista de evaluaciones
        output_file: Archivo de salida
        risk_profile: Filtrar por perfil de riesgo (opcional)
    """
    # Filtrar por perfil si se especifica
    if risk_profile:
        evaluations = [
            e for e in evaluations
            if e.get("risk_profile") == risk_profile
        ]

    if not evaluations:
        print("❌ No hay evaluaciones para consolidar", file=sys.stderr)
        sys.exit(1)

    # Agrupar por perfil
    grouped = group_by_risk_profile(evaluations)

    # Generar estadísticas
    overall_stats = generate_summary_statistics(evaluations)

    # Calcular scores y rankings
    calculator = MetricsCalculator()
    all_traders = []

    for evaluation in evaluations:
        candidate = evaluation.get("candidate", {})
        metrics_data = candidate.get("metrics", {})
        
        metrics = TraderMetrics(
            display_name=candidate.get("display_name", "Unknown"),
            roi_30d=metrics_data.get("roi_30d_pct"),
            roi_90d=metrics_data.get("roi_90d_pct"),
            roi_180d=metrics_data.get("roi_180d_pct"),
            max_drawdown=metrics_data.get("max_drawdown_pct"),
            win_rate=metrics_data.get("win_rate_pct"),
            avg_leverage=metrics_data.get("avg_leverage"),
            copiers=metrics_data.get("copiers"),
        )

        profile = evaluation.get("risk_profile", "moderate")
        scores = calculator.calculate_trader_score(metrics, profile)
        classification, recommendation = calculator.classify_score(
            scores["total_score"]
        )

        all_traders.append({
            "trader": metrics.display_name,
            "risk_profile": profile,
            "total_score": scores["total_score"],
            "classification": classification,
            "recommendation": recommendation,
            "metrics": {
                "roi_90d": metrics.roi_90d,
                "max_drawdown": metrics.max_drawdown,
                "win_rate": metrics.win_rate,
                "avg_leverage": metrics.avg_leverage,
                "copiers": metrics.copiers,
            },
            "source_file": evaluation.get("_source_file"),
        })

    # Ordenar por score
    all_traders.sort(key=lambda x: x["total_score"], reverse=True)

    # Generar reporte consolidado
    report = {
        "report_metadata": {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_evaluations": len(evaluations),
            "risk_profiles": list(grouped.keys()),
            "filter_applied": risk_profile,
        },
        "summary_statistics": overall_stats,
        "traders_ranking": all_traders,
        "by_risk_profile": {},
    }

    # Estadísticas por perfil
    for profile, profile_evals in grouped.items():
        profile_stats = generate_summary_statistics(profile_evals)
        report["by_risk_profile"][profile] = {
            "count": len(profile_evals),
            "statistics": profile_stats,
        }

    # Guardar reporte
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"✅ Reporte consolidado generado: {output_file}")


def print_consolidated_summary(evaluations: List[Dict[str, Any]]) -> None:
    """
    Imprime un resumen consolidado en consola.

    Args:
        evaluations: Lista de evaluaciones
    """
    if not evaluations:
        print("❌ No hay evaluaciones para mostrar", file=sys.stderr)
        return

    # Agrupar por perfil
    grouped = group_by_risk_profile(evaluations)
    
    # Estadísticas generales
    overall_stats = generate_summary_statistics(evaluations)

    print(f"\n{'='*70}")
    print("REPORTE CONSOLIDADO DE EVALUACIONES")
    print(f"{'='*70}\n")

    print(f"📊 Total de Traders: {overall_stats['total_traders']}")
    print(f"📅 Fecha de Generación: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n")

    print(f"{'='*70}")
    print("ESTADÍSTICAS GENERALES")
    print(f"{'='*70}\n")

    print("ROI 90 días:")
    print(f"  • Promedio: {overall_stats['roi_90d']['avg']}%")
    print(f"  • Rango: {overall_stats['roi_90d']['min']}% - {overall_stats['roi_90d']['max']}%")
    print(f"  • Mediana: {overall_stats['roi_90d']['median']}%\n")

    print("Max Drawdown:")
    print(f"  • Promedio: {overall_stats['max_drawdown']['avg']}%")
    print(f"  • Rango: {overall_stats['max_drawdown']['min']}% - {overall_stats['max_drawdown']['max']}%")
    print(f"  • Mediana: {overall_stats['max_drawdown']['median']}%\n")

    print("Win Rate:")
    print(f"  • Promedio: {overall_stats['win_rate']['avg']}%")
    print(f"  • Rango: {overall_stats['win_rate']['min']}% - {overall_stats['win_rate']['max']}%")
    print(f"  • Mediana: {overall_stats['win_rate']['median']}%\n")

    print(f"{'='*70}")
    print("DISTRIBUCIÓN POR PERFIL DE RIESGO")
    print(f"{'='*70}\n")

    for profile, profile_evals in grouped.items():
        print(f"📌 {profile.upper()}: {len(profile_evals)} traders")

    print(f"\n{'='*70}\n")


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Consolida múltiples evaluaciones de traders",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  # Consolidar todas las evaluaciones de un mes
  %(prog)s --month 2025-01

  # Consolidar con filtro de perfil
  %(prog)s --month 2025-01 --profile moderate

  # Especificar directorio personalizado
  %(prog)s --directory evaluations/2025-01 --output report.json
        """,
    )

    parser.add_argument(
        "--month",
        type=str,
        help="Mes a consolidar (formato: YYYY-MM)",
    )

    parser.add_argument(
        "--directory",
        type=Path,
        help="Directorio con evaluaciones",
    )

    parser.add_argument(
        "-p",
        "--profile",
        choices=["conservative", "moderate", "aggressive"],
        help="Filtrar por perfil de riesgo",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Archivo de salida JSON",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()

    # Determinar directorio
    if args.directory:
        directory = args.directory
    elif args.month:
        directory = Path("evaluations") / args.month
    else:
        print("❌ Debe especificar --month o --directory", file=sys.stderr)
        sys.exit(1)

    # Cargar evaluaciones
    try:
        evaluations = load_evaluations_from_directory(directory)
        
        if not evaluations:
            print(f"❌ No se encontraron evaluaciones en {directory}", file=sys.stderr)
            sys.exit(1)

        print(f"✅ Cargadas {len(evaluations)} evaluaciones desde {directory}\n")

        # Mostrar resumen en consola
        print_consolidated_summary(evaluations)

        # Generar archivo de salida si se especifica
        if args.output:
            generate_consolidated_report(evaluations, args.output, args.profile)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()