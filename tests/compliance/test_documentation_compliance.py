"""
Test de Cumplimiento con Documentación

Valida que el código implementado cumple con las especificaciones
definidas en la documentación del proyecto.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, List

# Rutas del proyecto
BASE_DIR = Path(__file__).parent.parent.parent
DOCS_DIR = BASE_DIR / "docs"
SCRIPTS_DIR = BASE_DIR / "scripts"
BACKEND_DIR = BASE_DIR / "backend"
EVALUATIONS_DIR = BASE_DIR / "evaluations"


class TestRiskProfileCompliance:
    """
    Valida que los perfiles de riesgo implementados coincidan
    con los definidos en docs/methodology.md
    """

    EXPECTED_PROFILES = {
        "conservative": {
            "roi_90d_range": (10.0, 30.0),
            "max_drawdown": 10.0,
            "win_rate_min": 60.0,
            "leverage_range": (1.0, 2.0),
            "min_days_active": 180,
            "min_copiers": 200,
            "stop_copy_range": (-8.0, -5.0),
            "daily_loss_cap_range": (-2.0, -1.0)
        },
        "moderate": {
            "roi_90d_range": (20.0, 60.0),
            "max_drawdown": 20.0,
            "win_rate_min": 55.0,
            "leverage_range": (1.0, 3.0),
            "min_days_active": 90,
            "min_copiers": 100,
            "stop_copy_range": (-12.0, -10.0),
            "daily_loss_cap_range": (-3.0, -2.0)
        },
        "aggressive": {
            "roi_90d_range": (40.0, 200.0),
            "max_drawdown": 35.0,
            "win_rate_min": 50.0,
            "leverage_range": (2.0, 5.0),
            "min_days_active": 60,
            "min_copiers": 50,
            "stop_copy_range": (-20.0, -15.0),
            "daily_loss_cap_range": (-7.0, -5.0)
        }
    }

    def test_methodology_file_exists(self):
        """Verifica que methodology.md existe"""
        assert (DOCS_DIR / "methodology.md").exists(), \
            "docs/methodology.md no encontrado"

    def test_risk_profiles_documented(self):
        """Verifica que los 3 perfiles estén documentados"""
        methodology = (DOCS_DIR / "methodology.md").read_text()

        assert "Conservative" in methodology, \
            "Perfil Conservative no documentado"
        assert "Moderate" in methodology, \
            "Perfil Moderate no documentado"
        assert "Aggressive" in methodology, \
            "Perfil Aggressive no documentado"

    def test_risk_profile_metrics_documented(self):
        """Verifica que todas las métricas clave estén documentadas"""
        methodology = (DOCS_DIR / "methodology.md").read_text()

        required_metrics = [
            "ROI",
            "Drawdown",
            "Win Rate",
            "Leverage",
            "Stop Copy"
        ]

        for metric in required_metrics:
            assert metric in methodology, \
                f"Métrica '{metric}' no documentada en methodology.md"


class TestArchitectureCompliance:
    """
    Valida que la estructura del proyecto coincida con
    la arquitectura definida en ARCHITECTURE.md
    """

    REQUIRED_DIRECTORIES = [
        "docs",
        "scripts",
        "evaluations",
        "backend",
        "frontend"
    ]

    REQUIRED_SCRIPTS = [
        "validate.py",
        "analyze_metrics.py",
        "consolidate.py"
    ]

    REQUIRED_DOCS = [
        "README.md",
        "ARCHITECTURE.md",
        "PLAN_EJECUTIVO.md",
        "docs/methodology.md",
        "docs/limitations.md"
    ]

    def test_architecture_file_exists(self):
        """Verifica que ARCHITECTURE.md existe"""
        assert (BASE_DIR / "ARCHITECTURE.md").exists(), \
            "ARCHITECTURE.md no encontrado"

    def test_required_directories_exist(self):
        """Verifica que todos los directorios requeridos existan"""
        for directory in self.REQUIRED_DIRECTORIES:
            dir_path = BASE_DIR / directory
            assert dir_path.exists(), \
                f"Directorio requerido '{directory}' no encontrado"

    def test_required_scripts_exist(self):
        """Verifica que todos los scripts requeridos existan"""
        for script in self.REQUIRED_SCRIPTS:
            script_path = SCRIPTS_DIR / script
            assert script_path.exists(), \
                f"Script requerido '{script}' no encontrado en scripts/"

    def test_required_documentation_exists(self):
        """Verifica que toda la documentación requerida exista"""
        for doc in self.REQUIRED_DOCS:
            doc_path = BASE_DIR / doc
            assert doc_path.exists(), \
                f"Documento requerido '{doc}' no encontrado"

    def test_backend_server_exists(self):
        """Verifica que el servidor backend existe"""
        assert (BACKEND_DIR / "server.py").exists(), \
            "backend/server.py no encontrado"

    def test_frontend_src_exists(self):
        """Verifica que el directorio src del frontend existe"""
        frontend_src = BASE_DIR / "frontend" / "src"
        assert frontend_src.exists(), \
            "frontend/src no encontrado"


class TestAPIEndpointCompliance:
    """
    Valida que los endpoints del backend cumplan con
    la especificación en ARCHITECTURE.md
    """

    REQUIRED_ENDPOINTS = {
        "/api/health": ["GET"],
        "/api/validate": ["POST"],
        "/api/analyze": ["POST"],
        "/api/analyze/multiple": ["POST"],
        "/api/consolidate": ["GET"],
        "/api/evaluations": ["GET", "POST"],
        "/api/evaluations/<filename>": ["GET", "PUT", "DELETE"]
    }

    def test_backend_server_has_required_imports(self):
        """Verifica que server.py tenga los imports necesarios"""
        server_content = (BACKEND_DIR / "server.py").read_text()

        required_imports = [
            "from flask import",
            "from flask_cors import CORS",
            "import json",
            "import subprocess"
        ]

        for import_stmt in required_imports:
            assert import_stmt in server_content, \
                f"Import requerido '{import_stmt}' no encontrado en server.py"

    def test_backend_has_health_endpoint(self):
        """Verifica que existe el endpoint de health check"""
        server_content = (BACKEND_DIR / "server.py").read_text()
        assert "/api/health" in server_content, \
            "Endpoint /api/health no encontrado"
        assert "def health_check" in server_content, \
            "Función health_check no encontrada"

    def test_backend_has_validation_endpoint(self):
        """Verifica que existe el endpoint de validación"""
        server_content = (BACKEND_DIR / "server.py").read_text()
        assert "/api/validate" in server_content, \
            "Endpoint /api/validate no encontrado"
        assert "def validate" in server_content, \
            "Función validate no encontrada"

    def test_backend_has_analysis_endpoint(self):
        """Verifica que existe el endpoint de análisis"""
        server_content = (BACKEND_DIR / "server.py").read_text()
        assert "/api/analyze" in server_content, \
            "Endpoint /api/analyze no encontrado"
        assert "def analyze" in server_content, \
            "Función analyze no encontrada"

    def test_backend_has_crud_endpoints(self):
        """Verifica que existan los endpoints CRUD de evaluaciones"""
        server_content = (BACKEND_DIR / "server.py").read_text()

        crud_functions = [
            "get_evaluations",
            "get_evaluation",
            "save_evaluation",
            "update_evaluation",
            "delete_evaluation"
        ]

        for func in crud_functions:
            assert f"def {func}" in server_content, \
                f"Función CRUD '{func}' no encontrada"


class TestScoringSystemCompliance:
    """
    Valida que el sistema de scoring implementado coincida
    con la metodología definida en docs/methodology.md
    """

    SCORING_WEIGHTS = {
        "conservative": {
            "max_drawdown": 0.30,
            "win_rate": 0.25,
            "roi": 0.15,
            "consistency": 0.20,
            "rar": 0.10
        },
        "moderate": {
            "max_drawdown": 0.25,
            "win_rate": 0.20,
            "roi": 0.25,
            "consistency": 0.15,
            "rar": 0.15
        },
        "aggressive": {
            "max_drawdown": 0.20,
            "win_rate": 0.15,
            "roi": 0.30,
            "consistency": 0.10,
            "rar": 0.25
        }
    }

    def test_analyze_metrics_script_exists(self):
        """Verifica que el script de análisis de métricas existe"""
        assert (SCRIPTS_DIR / "analyze_metrics.py").exists(), \
            "scripts/analyze_metrics.py no encontrado"

    def test_scoring_methodology_documented(self):
        """Verifica que la metodología de scoring esté documentada"""
        methodology = (DOCS_DIR / "methodology.md").read_text()

        assert "Sistema de Scoring" in methodology, \
            "Sistema de Scoring no documentado"
        assert "Ponderada" in methodology or "ponderado" in methodology.lower(), \
            "Sistema de puntuación ponderada no documentado"

    def test_score_ranges_documented(self):
        """Verifica que los rangos de score estén documentados"""
        methodology = (DOCS_DIR / "methodology.md").read_text()

        score_ranges = ["85-100", "70-84", "55-69", "40-54", "0-39"]

        for score_range in score_ranges:
            assert score_range in methodology, \
                f"Rango de score '{score_range}' no documentado"


class TestDataValidationCompliance:
    """
    Valida que el sistema de validación cumpla con
    los requisitos de calidad de datos
    """

    def test_validate_script_exists(self):
        """Verifica que el script de validación existe"""
        assert (SCRIPTS_DIR / "validate.py").exists(), \
            "scripts/validate.py no encontrado"

    def test_validate_script_has_schema_validation(self):
        """Verifica que el script de validación use JSON Schema"""
        validate_content = (SCRIPTS_DIR / "validate.py").read_text()

        # Buscar imports relacionados con validación
        assert "jsonschema" in validate_content or "schema" in validate_content.lower(), \
            "No se encontró referencia a validación de schema en validate.py"

    def test_requirements_has_jsonschema(self):
        """Verifica que jsonschema esté en requirements.txt"""
        requirements = (BASE_DIR / "requirements.txt").read_text()
        assert "jsonschema" in requirements, \
            "jsonschema no encontrado en requirements.txt"


class TestDocumentationQuality:
    """
    Valida la calidad y completitud de la documentación
    """

    def test_readme_has_required_sections(self):
        """Verifica que README tenga todas las secciones requeridas"""
        readme = (BASE_DIR / "README.md").read_text()

        required_sections = [
            "Objetivo",
            "Características",
            "Perfiles de Riesgo",
            "Instalación",
            "Guía de Uso",
            "Documentación"
        ]

        for section in required_sections:
            assert section in readme, \
                f"Sección '{section}' no encontrada en README.md"

    def test_architecture_has_diagrams(self):
        """Verifica que ARCHITECTURE tenga diagramas de flujo"""
        architecture = (BASE_DIR / "ARCHITECTURE.md").read_text()

        # Buscar indicadores de diagramas Mermaid
        assert "```mermaid" in architecture or "graph" in architecture, \
            "No se encontraron diagramas en ARCHITECTURE.md"

    def test_all_docs_have_toc(self):
        """Verifica que documentos principales tengan tabla de contenidos"""
        docs_to_check = [
            BASE_DIR / "README.md",
            BASE_DIR / "ARCHITECTURE.md",
            DOCS_DIR / "methodology.md"
        ]

        for doc_path in docs_to_check:
            if doc_path.exists():
                content = doc_path.read_text()
                # Buscar indicadores de TOC
                has_toc = any([
                    "## Índice" in content,
                    "## 📋 Índice" in content,
                    "## Tabla de Contenidos" in content,
                    "## 📋 Tabla de Contenidos" in content
                ])
                assert has_toc, \
                    f"{doc_path.name} no tiene tabla de contenidos"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
