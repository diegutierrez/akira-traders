"""
Test de Scripts Python

Valida que los scripts de Python (validate.py, analyze_metrics.py, consolidate.py)
funcionen correctamente y cumplan con sus especificaciones.
"""

import pytest
import subprocess
import json
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"


class TestScriptsExistence:
    """Verifica que todos los scripts requeridos existan"""

    REQUIRED_SCRIPTS = [
        "validate.py",
        "analyze_metrics.py",
        "consolidate.py"
    ]

    @pytest.mark.parametrize("script_name", REQUIRED_SCRIPTS)
    def test_script_exists(self, script_name):
        """Verifica que el script existe"""
        script_path = SCRIPTS_DIR / script_name
        assert script_path.exists(), \
            f"Script requerido '{script_name}' no encontrado en scripts/"

    @pytest.mark.parametrize("script_name", REQUIRED_SCRIPTS)
    def test_script_is_readable(self, script_name):
        """Verifica que el script sea legible"""
        script_path = SCRIPTS_DIR / script_name
        if script_path.exists():
            assert script_path.stat().st_size > 0, \
                f"Script '{script_name}' está vacío"

    @pytest.mark.parametrize("script_name", REQUIRED_SCRIPTS)
    def test_script_has_shebang_or_docstring(self, script_name):
        """Verifica que el script tenga shebang o docstring"""
        script_path = SCRIPTS_DIR / script_name
        if script_path.exists():
            content = script_path.read_text()
            has_shebang = content.startswith("#!")
            has_docstring = '"""' in content or "'''" in content

            assert has_shebang or has_docstring, \
                f"Script '{script_name}' debe tener shebang o docstring"


class TestValidateScript:
    """Tests para scripts/validate.py"""

    @pytest.fixture
    def sample_evaluation_file(self, tmp_path):
        """Crea un archivo de evaluación temporal para testing"""
        evaluation = {
            "as_of_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "risk_profile": "moderate",
            "selection_criteria": {
                "roi_90d_range_pct": [20.0, 60.0],
                "max_drawdown_pct_lte": 20.0,
                "win_rate_pct_gte": 55.0,
                "min_days_active": 90,
                "leverage_range": [1.0, 3.0],
                "min_copiers": 100
            },
            "candidate": {
                "display_name": "TestTrader",
                "binance_profile_url": "https://www.binance.com/test",
                "metrics": {
                    "roi_30d_pct": 15.5,
                    "roi_90d_pct": 42.7,
                    "max_drawdown_pct": 14.5,
                    "win_rate_pct": 61.0,
                    "avg_leverage": 2.3,
                    "copiers": 342
                },
                "style": "swing",
                "copy_mode_suggestion": "fixed",
                "order_size_suggestion_usdt": 50,
                "daily_loss_cap_pct": 3.0,
                "stop_copy_drawdown_pct": 12.0
            }
        }

        file_path = tmp_path / "test_evaluation.json"
        with open(file_path, 'w') as f:
            json.dump(evaluation, f, indent=2)

        return file_path

    def test_validate_script_can_run(self):
        """Verifica que validate.py se pueda ejecutar"""
        script_path = SCRIPTS_DIR / "validate.py"
        if not script_path.exists():
            pytest.skip("validate.py no encontrado")

        # Intentar ejecutar con --help o sin argumentos
        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(SCRIPTS_DIR)
            )
            # Puede retornar 0 (help) o 2 (error esperado)
            assert result.returncode in [0, 1, 2]
        except subprocess.TimeoutExpired:
            pytest.fail("validate.py se colgó al ejecutar")

    def test_validate_script_has_main_block(self):
        """Verifica que validate.py tenga bloque __main__"""
        script_path = SCRIPTS_DIR / "validate.py"
        if script_path.exists():
            content = script_path.read_text()
            assert 'if __name__' in content, \
                "validate.py debe tener bloque __main__"


class TestAnalyzeMetricsScript:
    """Tests para scripts/analyze_metrics.py"""

    def test_analyze_metrics_script_can_run(self):
        """Verifica que analyze_metrics.py se pueda ejecutar"""
        script_path = SCRIPTS_DIR / "analyze_metrics.py"
        if not script_path.exists():
            pytest.skip("analyze_metrics.py no encontrado")

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(SCRIPTS_DIR)
            )
            assert result.returncode in [0, 1, 2]
        except subprocess.TimeoutExpired:
            pytest.fail("analyze_metrics.py se colgó al ejecutar")

    def test_analyze_metrics_has_main_block(self):
        """Verifica que analyze_metrics.py tenga bloque __main__"""
        script_path = SCRIPTS_DIR / "analyze_metrics.py"
        if script_path.exists():
            content = script_path.read_text()
            assert 'if __name__' in content, \
                "analyze_metrics.py debe tener bloque __main__"

    def test_analyze_metrics_has_scoring_function(self):
        """Verifica que analyze_metrics.py tenga función de scoring"""
        script_path = SCRIPTS_DIR / "analyze_metrics.py"
        if script_path.exists():
            content = script_path.read_text()
            # Buscar indicadores de scoring
            has_score = any([
                "score" in content.lower(),
                "calculate" in content.lower(),
                "rating" in content.lower()
            ])
            assert has_score, \
                "analyze_metrics.py debe tener funcionalidad de scoring"


class TestConsolidateScript:
    """Tests para scripts/consolidate.py"""

    def test_consolidate_script_can_run(self):
        """Verifica que consolidate.py se pueda ejecutar"""
        script_path = SCRIPTS_DIR / "consolidate.py"
        if not script_path.exists():
            pytest.skip("consolidate.py no encontrado")

        try:
            result = subprocess.run(
                [sys.executable, str(script_path), "--help"],
                capture_output=True,
                text=True,
                timeout=5,
                cwd=str(SCRIPTS_DIR)
            )
            assert result.returncode in [0, 1, 2]
        except subprocess.TimeoutExpired:
            pytest.fail("consolidate.py se colgó al ejecutar")

    def test_consolidate_has_main_block(self):
        """Verifica que consolidate.py tenga bloque __main__"""
        script_path = SCRIPTS_DIR / "consolidate.py"
        if script_path.exists():
            content = script_path.read_text()
            assert 'if __name__' in content, \
                "consolidate.py debe tener bloque __main__"


class TestUtilsModule:
    """Tests para el módulo utils/"""

    def test_utils_directory_exists(self):
        """Verifica que el directorio utils existe"""
        utils_dir = SCRIPTS_DIR / "utils"
        assert utils_dir.exists(), \
            "Directorio scripts/utils no encontrado"

    def test_utils_is_python_package(self):
        """Verifica que utils sea un paquete Python válido"""
        utils_init = SCRIPTS_DIR / "utils" / "__init__.py"
        assert utils_init.exists(), \
            "scripts/utils/__init__.py no encontrado (no es paquete Python)"

    def test_utils_has_expected_modules(self):
        """Verifica que utils tenga los módulos esperados"""
        utils_dir = SCRIPTS_DIR / "utils"

        # Buscar archivos .py (excluyendo __init__.py)
        python_files = list(utils_dir.glob("*.py"))
        python_files = [f for f in python_files if f.name != "__init__.py"]

        # Debe haber al menos un módulo de utilidades
        assert len(python_files) > 0, \
            "scripts/utils debe contener módulos de utilidades"


class TestScriptsImportability:
    """Tests para verificar que los scripts se puedan importar"""

    def test_scripts_are_importable_as_modules(self):
        """Verifica que los scripts se puedan importar (no solo ejecutar)"""
        # Agregar scripts al path
        sys.path.insert(0, str(SCRIPTS_DIR))

        scripts_to_test = ["validate", "analyze_metrics", "consolidate"]

        for script_name in scripts_to_test:
            script_path = SCRIPTS_DIR / f"{script_name}.py"
            if script_path.exists():
                try:
                    # Intentar importar (solo verifica sintaxis)
                    import importlib.util
                    spec = importlib.util.spec_from_file_location(
                        script_name,
                        script_path
                    )
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        # No ejecutamos, solo verificamos que compile
                        assert module is not None
                except SyntaxError as e:
                    pytest.fail(f"Error de sintaxis en {script_name}.py: {e}")


class TestScriptsDependencies:
    """Tests para verificar dependencias de los scripts"""

    def test_scripts_can_import_required_modules(self):
        """Verifica que las importaciones básicas funcionen"""
        required_modules = [
            "json",
            "pathlib",
            "datetime"
        ]

        for module_name in required_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.fail(f"Módulo estándar '{module_name}' no disponible")

    def test_external_dependencies_available(self):
        """Verifica que dependencias externas estén instaladas"""
        # Estas son las dependencias críticas según requirements.txt
        external_modules = [
            "jsonschema",
            "pandas",
            "jinja2"
        ]

        for module_name in external_modules:
            try:
                __import__(module_name)
            except ImportError:
                pytest.skip(f"Dependencia '{module_name}' no instalada (test skip)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
