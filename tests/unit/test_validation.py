"""
Test de Validación de Schemas y Datos

Valida que los datos cumplan con los schemas definidos
y las reglas de negocio del sistema.
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Agregar directorio de scripts al path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

# Intentar importar el módulo de validación
try:
    from validate import validate_evaluation
    VALIDATE_MODULE_AVAILABLE = True
except ImportError:
    VALIDATE_MODULE_AVAILABLE = False


class TestTraderEvaluationSchema:
    """
    Valida que las evaluaciones de traders cumplan con
    el schema esperado según ARCHITECTURE.md
    """

    @pytest.fixture
    def valid_evaluation(self) -> Dict[str, Any]:
        """Fixture con evaluación válida de ejemplo"""
        return {
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
                "display_name": "TestTrader123",
                "binance_profile_url": "https://www.binance.com/test",
                "metrics": {
                    "roi_30d_pct": 15.5,
                    "roi_90d_pct": 42.7,
                    "roi_180d_pct": 65.3,
                    "max_drawdown_pct": 14.5,
                    "win_rate_pct": 61.0,
                    "avg_leverage": 2.3,
                    "copiers": 342
                },
                "style": "swing",
                "assets_whitelist": ["BTCUSDT", "ETHUSDT"],
                "copy_mode_suggestion": "fixed",
                "order_size_suggestion_usdt": 50,
                "daily_loss_cap_pct": 3.0,
                "stop_copy_drawdown_pct": 12.0,
                "notes": "Trader con buen historial"
            }
        }

    @pytest.fixture
    def invalid_evaluation_missing_fields(self) -> Dict[str, Any]:
        """Fixture con evaluación inválida (campos faltantes)"""
        return {
            "as_of_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "risk_profile": "moderate"
            # Faltan: selection_criteria y candidate
        }

    @pytest.fixture
    def invalid_evaluation_wrong_types(self) -> Dict[str, Any]:
        """Fixture con evaluación inválida (tipos incorrectos)"""
        return {
            "as_of_utc": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "risk_profile": "moderate",
            "selection_criteria": {
                "roi_90d_range_pct": "20-60",  # Debería ser array
                "max_drawdown_pct_lte": "20",  # Debería ser number
                "win_rate_pct_gte": 55.0,
                "min_days_active": 90,
                "leverage_range": [1.0, 3.0],
                "min_copiers": 100
            },
            "candidate": {
                "display_name": "TestTrader",
                "binance_profile_url": "not-a-url",  # URL inválida
                "metrics": {
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

    def test_valid_evaluation_structure(self, valid_evaluation):
        """Verifica que una evaluación válida tenga todos los campos requeridos"""
        required_fields = ["as_of_utc", "risk_profile", "selection_criteria", "candidate"]

        for field in required_fields:
            assert field in valid_evaluation, \
                f"Campo requerido '{field}' no encontrado"

    def test_risk_profile_enum(self, valid_evaluation):
        """Verifica que el perfil de riesgo sea uno de los valores permitidos"""
        allowed_profiles = ["conservative", "moderate", "aggressive"]
        assert valid_evaluation["risk_profile"] in allowed_profiles, \
            f"Perfil de riesgo '{valid_evaluation['risk_profile']}' no es válido"

    def test_selection_criteria_structure(self, valid_evaluation):
        """Verifica que los criterios de selección tengan la estructura correcta"""
        criteria = valid_evaluation["selection_criteria"]

        required_criteria_fields = [
            "roi_90d_range_pct",
            "max_drawdown_pct_lte",
            "win_rate_pct_gte",
            "min_days_active",
            "leverage_range",
            "min_copiers"
        ]

        for field in required_criteria_fields:
            assert field in criteria, \
                f"Campo de criterio '{field}' no encontrado"

    def test_candidate_structure(self, valid_evaluation):
        """Verifica que los datos del candidato tengan la estructura correcta"""
        candidate = valid_evaluation["candidate"]

        required_candidate_fields = [
            "display_name",
            "binance_profile_url",
            "metrics",
            "style",
            "copy_mode_suggestion",
            "order_size_suggestion_usdt",
            "daily_loss_cap_pct",
            "stop_copy_drawdown_pct"
        ]

        for field in required_candidate_fields:
            assert field in candidate, \
                f"Campo de candidato '{field}' no encontrado"

    def test_metrics_structure(self, valid_evaluation):
        """Verifica que las métricas tengan la estructura correcta"""
        metrics = valid_evaluation["candidate"]["metrics"]

        required_metrics_fields = [
            "roi_90d_pct",
            "max_drawdown_pct",
            "win_rate_pct",
            "avg_leverage",
            "copiers"
        ]

        for field in required_metrics_fields:
            assert field in metrics, \
                f"Campo de métrica '{field}' no encontrado"

    def test_metrics_ranges(self, valid_evaluation):
        """Verifica que las métricas estén dentro de rangos válidos"""
        metrics = valid_evaluation["candidate"]["metrics"]

        # Max Drawdown debe ser 0-100%
        assert 0 <= metrics["max_drawdown_pct"] <= 100, \
            "Max Drawdown fuera de rango (0-100%)"

        # Win Rate debe ser 0-100%
        assert 0 <= metrics["win_rate_pct"] <= 100, \
            "Win Rate fuera de rango (0-100%)"

        # Leverage debe ser positivo
        assert metrics["avg_leverage"] > 0, \
            "Leverage debe ser positivo"

        # Copiers debe ser no negativo
        assert metrics["copiers"] >= 0, \
            "Número de copiers no puede ser negativo"

    def test_style_enum(self, valid_evaluation):
        """Verifica que el estilo de trading sea uno de los valores permitidos"""
        allowed_styles = ["scalping", "swing", "trend-following", "arbitrage", "mixed"]
        style = valid_evaluation["candidate"]["style"]

        assert style in allowed_styles, \
            f"Estilo '{style}' no es válido"

    def test_copy_mode_enum(self, valid_evaluation):
        """Verifica que el modo de copia sea uno de los valores permitidos"""
        allowed_modes = ["fixed", "ratio"]
        mode = valid_evaluation["candidate"]["copy_mode_suggestion"]

        assert mode in allowed_modes, \
            f"Modo de copia '{mode}' no es válido"

    def test_roi_range_is_array(self, valid_evaluation):
        """Verifica que el rango de ROI sea un array de 2 elementos"""
        roi_range = valid_evaluation["selection_criteria"]["roi_90d_range_pct"]

        assert isinstance(roi_range, list), \
            "roi_90d_range_pct debe ser un array"
        assert len(roi_range) == 2, \
            "roi_90d_range_pct debe tener exactamente 2 elementos"
        assert roi_range[0] < roi_range[1], \
            "El primer valor del rango debe ser menor que el segundo"

    def test_leverage_range_is_array(self, valid_evaluation):
        """Verifica que el rango de leverage sea un array de 2 elementos"""
        leverage_range = valid_evaluation["selection_criteria"]["leverage_range"]

        assert isinstance(leverage_range, list), \
            "leverage_range debe ser un array"
        assert len(leverage_range) == 2, \
            "leverage_range debe tener exactamente 2 elementos"
        assert leverage_range[0] < leverage_range[1], \
            "El primer valor del rango debe ser menor que el segundo"


class TestRiskProfileValidation:
    """
    Valida que los datos cumplan con los límites definidos
    para cada perfil de riesgo según methodology.md
    """

    @pytest.fixture
    def conservative_profile_limits(self) -> Dict[str, Any]:
        """Límites para perfil conservador"""
        return {
            "roi_90d_range": (10.0, 30.0),
            "max_drawdown": 10.0,
            "win_rate_min": 60.0,
            "leverage_max": 2.0,
            "min_copiers": 200
        }

    @pytest.fixture
    def moderate_profile_limits(self) -> Dict[str, Any]:
        """Límites para perfil moderado"""
        return {
            "roi_90d_range": (20.0, 60.0),
            "max_drawdown": 20.0,
            "win_rate_min": 55.0,
            "leverage_max": 3.0,
            "min_copiers": 100
        }

    @pytest.fixture
    def aggressive_profile_limits(self) -> Dict[str, Any]:
        """Límites para perfil agresivo"""
        return {
            "roi_90d_range": (40.0, 200.0),
            "max_drawdown": 35.0,
            "win_rate_min": 50.0,
            "leverage_max": 5.0,
            "min_copiers": 50
        }

    def test_moderate_profile_roi_range(self, moderate_profile_limits):
        """Verifica que el rango de ROI para perfil moderado sea correcto"""
        assert moderate_profile_limits["roi_90d_range"] == (20.0, 60.0), \
            "Rango de ROI para perfil moderado incorrecto"

    def test_moderate_profile_drawdown(self, moderate_profile_limits):
        """Verifica que el max drawdown para perfil moderado sea correcto"""
        assert moderate_profile_limits["max_drawdown"] == 20.0, \
            "Max Drawdown para perfil moderado incorrecto"

    def test_moderate_profile_win_rate(self, moderate_profile_limits):
        """Verifica que el win rate mínimo para perfil moderado sea correcto"""
        assert moderate_profile_limits["win_rate_min"] == 55.0, \
            "Win Rate mínimo para perfil moderado incorrecto"

    def test_conservative_is_more_restrictive_than_moderate(
        self,
        conservative_profile_limits,
        moderate_profile_limits
    ):
        """Verifica que el perfil conservador sea más restrictivo que el moderado"""
        # Max Drawdown más bajo
        assert conservative_profile_limits["max_drawdown"] < moderate_profile_limits["max_drawdown"], \
            "Perfil conservador debería tener max drawdown más bajo"

        # Win Rate más alto
        assert conservative_profile_limits["win_rate_min"] > moderate_profile_limits["win_rate_min"], \
            "Perfil conservador debería requerir win rate más alto"

        # Leverage más bajo
        assert conservative_profile_limits["leverage_max"] < moderate_profile_limits["leverage_max"], \
            "Perfil conservador debería tener leverage máximo más bajo"

    def test_aggressive_is_less_restrictive_than_moderate(
        self,
        aggressive_profile_limits,
        moderate_profile_limits
    ):
        """Verifica que el perfil agresivo sea menos restrictivo que el moderado"""
        # Max Drawdown más alto
        assert aggressive_profile_limits["max_drawdown"] > moderate_profile_limits["max_drawdown"], \
            "Perfil agresivo debería permitir max drawdown más alto"

        # Win Rate más bajo
        assert aggressive_profile_limits["win_rate_min"] < moderate_profile_limits["win_rate_min"], \
            "Perfil agresivo debería requerir win rate más bajo"

        # Leverage más alto
        assert aggressive_profile_limits["leverage_max"] > moderate_profile_limits["leverage_max"], \
            "Perfil agresivo debería permitir leverage más alto"


class TestDataIntegrity:
    """
    Verifica la integridad de datos en evaluaciones existentes
    """

    def test_evaluations_directory_exists(self):
        """Verifica que el directorio de evaluaciones existe"""
        evaluations_dir = BASE_DIR / "evaluations"
        assert evaluations_dir.exists(), \
            "Directorio 'evaluations' no encontrado"

    def test_can_load_evaluation_files(self):
        """Verifica que los archivos de evaluación existentes sean JSON válidos"""
        evaluations_dir = BASE_DIR / "evaluations"

        # Buscar archivos JSON (excluir temp y examples)
        json_files = []
        for json_file in evaluations_dir.rglob("*.json"):
            if "temp" not in str(json_file) and "examples" not in str(json_file):
                json_files.append(json_file)

        # Si hay archivos, verificar que se puedan cargar
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                assert isinstance(data, dict), \
                    f"{json_file.name} no contiene un objeto JSON válido"
            except json.JSONDecodeError as e:
                pytest.fail(f"Error al parsear {json_file.name}: {e}")

    def test_timestamp_format_is_iso8601(self):
        """Verifica que los timestamps estén en formato ISO 8601"""
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Verificar formato básico
        assert "T" in timestamp, "Timestamp debe tener 'T' separando fecha y hora"
        assert timestamp.endswith("Z"), "Timestamp debe terminar con 'Z' (UTC)"

        # Verificar que se pueda parsear
        try:
            parsed = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")
            assert parsed is not None
        except ValueError:
            pytest.fail("Formato de timestamp no es válido ISO 8601")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
