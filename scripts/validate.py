#!/usr/bin/env python3
"""
Script de validación de evaluaciones de traders.

Este script valida archivos JSON de evaluaciones contra el schema definido,
verifica la consistencia de métricas y la alineación con perfiles de riesgo.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime


# Perfiles de riesgo predefinidos
RISK_PROFILES = {
    "conservative": {
        "roi_90d_range": (10, 30),
        "max_drawdown_max": 10,
        "win_rate_min": 60,
        "leverage_range": (1, 2),
        "min_days_active": 180,
        "min_copiers": 200,
    },
    "moderate": {
        "roi_90d_range": (20, 60),
        "max_drawdown_max": 20,
        "win_rate_min": 55,
        "leverage_range": (1, 3),
        "min_days_active": 90,
        "min_copiers": 100,
    },
    "aggressive": {
        "roi_90d_range": (40, 100),
        "max_drawdown_max": 35,
        "win_rate_min": 50,
        "leverage_range": (2, 5),
        "min_days_active": 60,
        "min_copiers": 50,
    },
}


class ValidationError(Exception):
    """Excepción personalizada para errores de validación."""
    pass


class TraderValidator:
    """Validador de evaluaciones de traders."""

    def __init__(self, verbose: bool = False):
        """
        Inicializa el validador.

        Args:
            verbose: Si es True, muestra información detallada
        """
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_file(self, filepath: Path) -> bool:
        """
        Valida un archivo JSON de evaluación.

        Args:
            filepath: Ruta al archivo JSON

        Returns:
            True si la validación es exitosa, False en caso contrario
        """
        self.errors = []
        self.warnings = []

        try:
            # Leer archivo JSON
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Validaciones
            self._validate_structure(data)
            self._validate_risk_profile(data)
            self._validate_metrics(data)
            self._validate_consistency(data)

            return len(self.errors) == 0

        except json.JSONDecodeError as e:
            self.errors.append(f"Error al parsear JSON: {e}")
            return False
        except FileNotFoundError:
            self.errors.append(f"Archivo no encontrado: {filepath}")
            return False
        except Exception as e:
            self.errors.append(f"Error inesperado: {e}")
            return False

    def _validate_structure(self, data: Dict[str, Any]) -> None:
        """Valida la estructura básica del JSON."""
        required_fields = ["as_of_utc", "risk_profile", "candidate"]

        for field in required_fields:
            if field not in data:
                self.errors.append(f"Campo requerido faltante: {field}")

        # Validar formato de fecha
        if "as_of_utc" in data:
            try:
                datetime.fromisoformat(data["as_of_utc"].replace("Z", "+00:00"))
            except ValueError:
                self.errors.append(
                    f"Formato de fecha inválido: {data['as_of_utc']}"
                )

        # Validar perfil de riesgo
        if "risk_profile" in data:
            if data["risk_profile"] not in RISK_PROFILES:
                self.errors.append(
                    f"Perfil de riesgo inválido: {data['risk_profile']}"
                )

        # Validar estructura del candidato
        if "candidate" in data:
            self._validate_candidate_structure(data["candidate"])

    def _validate_candidate_structure(self, candidate: Dict[str, Any]) -> None:
        """Valida la estructura del candidato."""
        required_fields = [
            "display_name",
            "metrics",
            "style",
            "copy_mode_suggestion",
            "order_size_suggestion_usdt",
        ]

        for field in required_fields:
            if field not in candidate:
                self.errors.append(
                    f"Campo requerido faltante en candidate: {field}"
                )

        # Validar métricas
        if "metrics" in candidate:
            required_metrics = [
                "roi_90d_pct",
                "max_drawdown_pct",
                "win_rate_pct",
                "avg_leverage",
            ]
            for metric in required_metrics:
                if metric not in candidate["metrics"]:
                    self.errors.append(
                        f"Métrica requerida faltante: {metric}"
                    )

    def _validate_risk_profile(self, data: Dict[str, Any]) -> None:
        """Valida la alineación con el perfil de riesgo."""
        if "risk_profile" not in data or "candidate" not in data:
            return

        profile_name = data["risk_profile"]
        profile = RISK_PROFILES.get(profile_name)
        if not profile:
            return

        metrics = data["candidate"].get("metrics", {})

        # Validar ROI 90d
        roi_90d = metrics.get("roi_90d_pct")
        if roi_90d is not None:
            min_roi, max_roi = profile["roi_90d_range"]
            if roi_90d < min_roi:
                self.warnings.append(
                    f"ROI 90d ({roi_90d}%) está por debajo del rango "
                    f"esperado para perfil {profile_name} ({min_roi}-{max_roi}%)"
                )
            elif roi_90d > max_roi:
                self.warnings.append(
                    f"ROI 90d ({roi_90d}%) excede el rango esperado "
                    f"para perfil {profile_name} ({min_roi}-{max_roi}%)"
                )

        # Validar Max Drawdown
        max_dd = metrics.get("max_drawdown_pct")
        if max_dd is not None:
            if max_dd > profile["max_drawdown_max"]:
                self.errors.append(
                    f"Max Drawdown ({max_dd}%) excede el límite "
                    f"para perfil {profile_name} ({profile['max_drawdown_max']}%)"
                )

        # Validar Win Rate
        win_rate = metrics.get("win_rate_pct")
        if win_rate is not None:
            if win_rate < profile["win_rate_min"]:
                self.errors.append(
                    f"Win Rate ({win_rate}%) está por debajo del mínimo "
                    f"para perfil {profile_name} ({profile['win_rate_min']}%)"
                )

        # Validar Leverage
        avg_leverage = metrics.get("avg_leverage")
        if avg_leverage is not None:
            min_lev, max_lev = profile["leverage_range"]
            if avg_leverage < min_lev or avg_leverage > max_lev:
                self.warnings.append(
                    f"Leverage promedio ({avg_leverage}×) está fuera del rango "
                    f"esperado para perfil {profile_name} ({min_lev}-{max_lev}×)"
                )

    def _validate_metrics(self, data: Dict[str, Any]) -> None:
        """Valida los rangos de las métricas."""
        if "candidate" not in data:
            return

        metrics = data["candidate"].get("metrics", {})

        # Validar rangos
        validations = [
            ("max_drawdown_pct", 0, 100, "Max Drawdown"),
            ("win_rate_pct", 0, 100, "Win Rate"),
            ("avg_leverage", 1, 10, "Leverage Promedio"),
        ]

        for metric_name, min_val, max_val, display_name in validations:
            value = metrics.get(metric_name)
            if value is not None:
                if value < min_val or value > max_val:
                    self.errors.append(
                        f"{display_name} ({value}) está fuera del rango "
                        f"válido ({min_val}-{max_val})"
                    )

        # Validar que ROI 30d <= ROI 90d (si ambos están presentes)
        roi_30d = metrics.get("roi_30d_pct")
        roi_90d = metrics.get("roi_90d_pct")
        if roi_30d is not None and roi_90d is not None:
            if abs(roi_30d - roi_90d) > roi_90d * 0.5:
                self.warnings.append(
                    f"Gran diferencia entre ROI 30d ({roi_30d}%) y "
                    f"ROI 90d ({roi_90d}%). Verificar consistencia."
                )

    def _validate_consistency(self, data: Dict[str, Any]) -> None:
        """Valida la consistencia interna de los datos."""
        if "candidate" not in data:
            return

        candidate = data["candidate"]

        # Validar que order_size_suggestion sea razonable
        order_size = candidate.get("order_size_suggestion_usdt")
        if order_size is not None:
            if order_size < 10:
                self.warnings.append(
                    f"Order size ({order_size} USDT) es muy bajo. "
                    "Mínimo recomendado: 10 USDT"
                )
            elif order_size > 1000:
                self.warnings.append(
                    f"Order size ({order_size} USDT) es muy alto. "
                    "Verificar si es intencional."
                )

        # Validar estilo de trading
        valid_styles = ["scalping", "swing", "trend-following", "arbitrage", "mixed"]
        style = candidate.get("style")
        if style and style not in valid_styles:
            self.warnings.append(
                f"Estilo de trading '{style}' no está en la lista estándar: "
                f"{', '.join(valid_styles)}"
            )

    def print_results(self, filepath: Path, success: bool) -> None:
        """Imprime los resultados de la validación."""
        print(f"\n{'='*70}")
        print(f"Validación de: {filepath.name}")
        print(f"{'='*70}\n")

        if success:
            print("✅ Validación EXITOSA")
        else:
            print("❌ Validación FALLIDA")

        if self.errors:
            print(f"\n🔴 Errores ({len(self.errors)}):")
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")

        if self.warnings:
            print(f"\n⚠️  Advertencias ({len(self.warnings)}):")
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")

        if not self.errors and not self.warnings:
            print("\n✨ No se encontraron problemas")

        print(f"\n{'='*70}\n")


def validate_multiple_files(filepaths: List[Path], verbose: bool = False) -> Tuple[int, int]:
    """
    Valida múltiples archivos.

    Args:
        filepaths: Lista de rutas a archivos JSON
        verbose: Si es True, muestra información detallada

    Returns:
        Tupla con (archivos exitosos, archivos fallidos)
    """
    validator = TraderValidator(verbose=verbose)
    successful = 0
    failed = 0

    for filepath in filepaths:
        success = validator.validate_file(filepath)
        validator.print_results(filepath, success)

        if success:
            successful += 1
        else:
            failed += 1

    return successful, failed


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Valida evaluaciones de traders contra el schema y reglas de negocio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  %(prog)s evaluations/2025-01/trader_example.json
  %(prog)s evaluations/2025-01/*.json
  %(prog)s --verbose evaluations/2025-01/trader_example.json
        """,
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
        help="Archivo(s) JSON a validar",
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

    # Validar archivos
    successful, failed = validate_multiple_files(args.files, args.verbose)

    # Resumen final
    total = successful + failed
    print(f"{'='*70}")
    print(f"RESUMEN FINAL")
    print(f"{'='*70}")
    print(f"Total de archivos: {total}")
    print(f"✅ Exitosos: {successful}")
    print(f"❌ Fallidos: {failed}")
    print(f"{'='*70}\n")

    # Código de salida
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()