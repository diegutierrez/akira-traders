#!/usr/bin/env python3
"""
Akira Traders - Test Runner

Script principal para ejecutar todos los tests del proyecto y generar reportes.

Uso:
    python run_tests.py              # Ejecutar todos los tests
    python run_tests.py --compliance # Solo tests de cumplimiento
    python run_tests.py --validation # Solo tests de validación
    python run_tests.py --coverage   # Con cobertura de código
    python run_tests.py --report     # Generar reporte detallado
"""

import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import json


class TestRunner:
    """Ejecutor de tests con generación de reportes"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.tests_dir = self.base_dir / "tests"
        self.reports_dir = self.base_dir / "test_reports"
        self.reports_dir.mkdir(exist_ok=True)

    def run_tests(self, args):
        """Ejecuta los tests según los argumentos proporcionados"""

        pytest_args = ["pytest"]

        # Agregar verbose
        pytest_args.append("-v")

        # Filtrar por tipo de test
        if args.compliance:
            pytest_args.extend(["-m", "compliance"])
            print("🔍 Ejecutando tests de CUMPLIMIENTO...")
        elif args.validation:
            pytest_args.extend(["-m", "validation"])
            print("✅ Ejecutando tests de VALIDACIÓN...")
        elif args.integration:
            pytest_args.extend(["-m", "integration"])
            print("🔗 Ejecutando tests de INTEGRACIÓN...")
        elif args.unit:
            pytest_args.extend(["-m", "unit"])
            print("🧪 Ejecutando tests UNITARIOS...")
        else:
            print("🚀 Ejecutando TODOS los tests...")

        # Agregar cobertura si se solicita
        if args.coverage:
            pytest_args.extend([
                "--cov=scripts",
                "--cov=backend",
                "--cov-report=html",
                "--cov-report=term"
            ])
            print("📊 Generando reporte de cobertura...")

        # Agregar reporte JUnit si se solicita
        if args.report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            junit_file = self.reports_dir / f"junit_report_{timestamp}.xml"
            pytest_args.extend([
                f"--junit-xml={junit_file}"
            ])
            print(f"📄 Reporte JUnit: {junit_file}")

        # Agregar directorio de tests
        pytest_args.append(str(self.tests_dir))

        # Ejecutar pytest
        print(f"\n{'='*70}")
        print(f"Comando: {' '.join(pytest_args)}")
        print(f"{'='*70}\n")

        result = subprocess.run(pytest_args)

        return result.returncode

    def generate_summary(self):
        """Genera un resumen de los tests ejecutados"""

        print("\n" + "="*70)
        print("📊 RESUMEN DE TESTS")
        print("="*70 + "\n")

        # Información del proyecto
        print("Proyecto: Akira Traders - Sistema de Evaluación de Traders")
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # Categorías de tests
        categories = {
            "Cumplimiento": "tests/compliance/",
            "Validación": "tests/unit/test_validation.py",
            "Backend API": "tests/integration/test_backend_api.py",
            "Scripts": "tests/unit/test_scripts.py"
        }

        print("Categorías de tests:")
        for category, path in categories.items():
            full_path = self.base_dir / path
            if full_path.exists():
                print(f"  ✅ {category}: {path}")
            else:
                print(f"  ❌ {category}: {path} (no encontrado)")

        print("\n" + "="*70)
        print()

    def check_dependencies(self):
        """Verifica que las dependencias necesarias estén instaladas"""

        print("🔍 Verificando dependencias...\n")

        required_packages = {
            "pytest": "Framework de testing",
            "jsonschema": "Validación de schemas",
            "pandas": "Análisis de datos",
            "jinja2": "Templates",
            "flask": "Backend API"
        }

        missing = []
        installed = []

        for package, description in required_packages.items():
            try:
                __import__(package)
                installed.append(f"  ✅ {package:15s} - {description}")
            except ImportError:
                missing.append(f"  ❌ {package:15s} - {description}")

        if installed:
            print("Dependencias instaladas:")
            for item in installed:
                print(item)

        if missing:
            print("\nDependencias faltantes:")
            for item in missing:
                print(item)
            print("\nInstalar con: pip install -r requirements.txt")
            return False

        print("\n✅ Todas las dependencias están instaladas\n")
        return True


def main():
    """Función principal"""

    parser = argparse.ArgumentParser(
        description="Ejecutor de tests para Akira Traders",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Filtros de tests
    parser.add_argument(
        "--compliance",
        action="store_true",
        help="Solo tests de cumplimiento con documentación"
    )
    parser.add_argument(
        "--validation",
        action="store_true",
        help="Solo tests de validación de datos"
    )
    parser.add_argument(
        "--integration",
        action="store_true",
        help="Solo tests de integración (API, scripts)"
    )
    parser.add_argument(
        "--unit",
        action="store_true",
        help="Solo tests unitarios"
    )

    # Opciones de reporte
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generar reporte de cobertura de código"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Generar reporte JUnit XML"
    )

    # Otras opciones
    parser.add_argument(
        "--check-deps",
        action="store_true",
        help="Solo verificar dependencias (no ejecutar tests)"
    )

    args = parser.parse_args()

    runner = TestRunner()

    # Si solo se pide verificar dependencias
    if args.check_deps:
        return 0 if runner.check_dependencies() else 1

    # Mostrar banner
    print("\n" + "="*70)
    print("🧪 AKIRA TRADERS - TEST SUITE")
    print("="*70 + "\n")

    # Verificar dependencias
    if not runner.check_dependencies():
        print("\n⚠️  Algunas dependencias faltan. Los tests pueden fallar.")
        print("Continuar de todos modos? (y/N): ", end="")
        response = input().lower()
        if response != 'y':
            print("Abortado.")
            return 1

    # Generar resumen
    runner.generate_summary()

    # Ejecutar tests
    returncode = runner.run_tests(args)

    # Mensaje final
    print("\n" + "="*70)
    if returncode == 0:
        print("✅ TODOS LOS TESTS PASARON")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
    print("="*70 + "\n")

    # Mensaje sobre cobertura
    if args.coverage:
        print("📊 Reporte de cobertura generado en: htmlcov/index.html")
        print("   Abrir con: open htmlcov/index.html (macOS) o xdg-open htmlcov/index.html (Linux)\n")

    return returncode


if __name__ == "__main__":
    sys.exit(main())
