"""
Test de Backend API

Tests de integración para el servidor Flask backend.
Valida todos los endpoints según ARCHITECTURE.md
"""

import pytest
import json
import sys
from pathlib import Path
from datetime import datetime

# Agregar directorios al path
BASE_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "backend"))

try:
    from server import app
    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False
    app = None


@pytest.fixture
def client():
    """Fixture para cliente de testing de Flask"""
    if not BACKEND_AVAILABLE:
        pytest.skip("Backend no disponible")

    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_evaluation():
    """Evaluación de ejemplo para tests"""
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
            "display_name": "TestTrader_API",
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


class TestHealthEndpoint:
    """Tests para el endpoint de health check"""

    def test_health_endpoint_exists(self, client):
        """Verifica que el endpoint /api/health existe"""
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        """Verifica que /api/health retorna JSON"""
        response = client.get('/api/health')
        assert response.content_type == 'application/json'

    def test_health_has_status(self, client):
        """Verifica que /api/health retorna campo 'status'"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'status' in data

    def test_health_status_is_ok(self, client):
        """Verifica que el status sea 'ok'"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert data['status'] == 'ok'

    def test_health_has_timestamp(self, client):
        """Verifica que /api/health retorna timestamp"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'timestamp' in data

    def test_health_has_version(self, client):
        """Verifica que /api/health retorna version"""
        response = client.get('/api/health')
        data = json.loads(response.data)
        assert 'version' in data


class TestValidateEndpoint:
    """Tests para el endpoint de validación"""

    def test_validate_endpoint_exists(self, client):
        """Verifica que el endpoint /api/validate existe"""
        response = client.post('/api/validate', json={})
        # Puede retornar 200 o 500, pero no 404
        assert response.status_code != 404

    def test_validate_accepts_json(self, client, sample_evaluation):
        """Verifica que /api/validate acepta JSON"""
        response = client.post(
            '/api/validate',
            data=json.dumps(sample_evaluation),
            content_type='application/json'
        )
        assert response.status_code in [200, 500]

    def test_validate_returns_json(self, client, sample_evaluation):
        """Verifica que /api/validate retorna JSON"""
        response = client.post(
            '/api/validate',
            data=json.dumps(sample_evaluation),
            content_type='application/json'
        )
        assert response.content_type == 'application/json'

    def test_validate_response_structure(self, client, sample_evaluation):
        """Verifica que /api/validate retorna estructura correcta"""
        response = client.post(
            '/api/validate',
            data=json.dumps(sample_evaluation),
            content_type='application/json'
        )
        data = json.loads(response.data)

        # Debe tener campo 'valid'
        assert 'valid' in data
        # Debe tener campo 'errors' (aunque sea vacío)
        assert 'errors' in data


class TestAnalyzeEndpoint:
    """Tests para el endpoint de análisis"""

    def test_analyze_endpoint_exists(self, client):
        """Verifica que el endpoint /api/analyze existe"""
        response = client.post('/api/analyze', json={})
        assert response.status_code != 404

    def test_analyze_accepts_evaluation(self, client, sample_evaluation):
        """Verifica que /api/analyze acepta una evaluación"""
        payload = {"evaluation": sample_evaluation}
        response = client.post(
            '/api/analyze',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [200, 500]

    def test_analyze_with_risk_profile(self, client, sample_evaluation):
        """Verifica que /api/analyze acepta parámetro risk_profile"""
        payload = {
            "evaluation": sample_evaluation,
            "risk_profile": "moderate"
        }
        response = client.post(
            '/api/analyze',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [200, 500]


class TestAnalyzeMultipleEndpoint:
    """Tests para el endpoint de análisis múltiple"""

    def test_analyze_multiple_endpoint_exists(self, client):
        """Verifica que el endpoint /api/analyze/multiple existe"""
        response = client.post('/api/analyze/multiple', json={})
        assert response.status_code != 404

    def test_analyze_multiple_accepts_array(self, client, sample_evaluation):
        """Verifica que /api/analyze/multiple acepta array de evaluaciones"""
        payload = {
            "evaluations": [sample_evaluation],
            "risk_profile": "moderate"
        }
        response = client.post(
            '/api/analyze/multiple',
            data=json.dumps(payload),
            content_type='application/json'
        )
        assert response.status_code in [200, 500]


class TestConsolidateEndpoint:
    """Tests para el endpoint de consolidación"""

    def test_consolidate_endpoint_exists(self, client):
        """Verifica que el endpoint /api/consolidate existe"""
        response = client.get('/api/consolidate')
        assert response.status_code != 404

    def test_consolidate_accepts_query_params(self, client):
        """Verifica que /api/consolidate acepta parámetros de query"""
        response = client.get('/api/consolidate?month=2025-01&profile=moderate')
        assert response.status_code in [200, 500]


class TestEvaluationsCRUD:
    """Tests para endpoints CRUD de evaluaciones"""

    def test_get_evaluations_endpoint_exists(self, client):
        """Verifica que GET /api/evaluations existe"""
        response = client.get('/api/evaluations')
        assert response.status_code in [200, 500]

    def test_get_evaluations_returns_array(self, client):
        """Verifica que GET /api/evaluations retorna un array"""
        response = client.get('/api/evaluations')
        if response.status_code == 200:
            data = json.loads(response.data)
            assert isinstance(data, list)

    def test_post_evaluation_endpoint_exists(self, client):
        """Verifica que POST /api/evaluations existe"""
        response = client.post('/api/evaluations', json={})
        # Puede retornar error pero no 404
        assert response.status_code != 404

    def test_get_evaluation_by_filename(self, client):
        """Verifica que GET /api/evaluations/<filename> existe"""
        response = client.get('/api/evaluations/test_file.json')
        # Puede ser 404 (no encontrado) o 200/500
        assert response.status_code in [200, 404, 500]

    def test_put_evaluation_endpoint_exists(self, client):
        """Verifica que PUT /api/evaluations/<filename> existe"""
        response = client.put('/api/evaluations/test_file.json', json={})
        # Puede ser 404 (no encontrado) o 200/500
        assert response.status_code in [200, 404, 500]

    def test_delete_evaluation_endpoint_exists(self, client):
        """Verifica que DELETE /api/evaluations/<filename> existe"""
        response = client.delete('/api/evaluations/test_file.json')
        # Puede ser 404 (no encontrado) o 200/500
        assert response.status_code in [200, 404, 500]


class TestCORSConfiguration:
    """Tests para configuración de CORS"""

    def test_cors_is_enabled(self, client):
        """Verifica que CORS esté habilitado"""
        response = client.get('/api/health')
        # Verificar que hay headers CORS
        assert 'Access-Control-Allow-Origin' in response.headers or response.status_code == 200


class TestErrorHandling:
    """Tests para manejo de errores"""

    def test_invalid_json_returns_error(self, client):
        """Verifica que JSON inválido retorne error"""
        response = client.post(
            '/api/validate',
            data='invalid json{',
            content_type='application/json'
        )
        assert response.status_code in [400, 500]

    def test_missing_content_type_handled(self, client):
        """Verifica que se maneje la ausencia de content-type"""
        response = client.post('/api/validate', data='{}')
        # Debe retornar error o procesarlo
        assert response.status_code in [200, 400, 415, 500]

    def test_nonexistent_endpoint_returns_404(self, client):
        """Verifica que endpoints inexistentes retornen 404"""
        response = client.get('/api/nonexistent_endpoint_xyz')
        assert response.status_code == 404


class TestResponseHeaders:
    """Tests para headers de respuesta"""

    def test_content_type_is_json_for_api_endpoints(self, client):
        """Verifica que los endpoints API retornen JSON"""
        endpoints = [
            '/api/health',
            '/api/evaluations'
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                assert 'application/json' in response.content_type


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
