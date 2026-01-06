"""
Configuración global de pytest para Akira Traders

Este archivo contiene fixtures y configuraciones que están disponibles
para todos los tests del proyecto.
"""

import pytest
import sys
from pathlib import Path

# Agregar directorios al path para imports
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "scripts"))
sys.path.insert(0, str(BASE_DIR / "backend"))


def pytest_configure(config):
    """Configuración ejecutada antes de los tests"""
    config.addinivalue_line(
        "markers", "compliance: Tests de cumplimiento con documentación"
    )
    config.addinivalue_line(
        "markers", "validation: Tests de validación de datos"
    )
    config.addinivalue_line(
        "markers", "integration: Tests de integración"
    )
    config.addinivalue_line(
        "markers", "unit: Tests unitarios"
    )


def pytest_collection_modifyitems(config, items):
    """Modificar items de test antes de ejecutarlos"""
    for item in items:
        # Marcar tests según su ubicación
        if "compliance" in str(item.fspath):
            item.add_marker(pytest.mark.compliance)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)


@pytest.fixture(scope="session")
def base_dir():
    """Fixture que retorna el directorio base del proyecto"""
    return BASE_DIR


@pytest.fixture(scope="session")
def scripts_dir():
    """Fixture que retorna el directorio de scripts"""
    return BASE_DIR / "scripts"


@pytest.fixture(scope="session")
def backend_dir():
    """Fixture que retorna el directorio del backend"""
    return BASE_DIR / "backend"


@pytest.fixture(scope="session")
def docs_dir():
    """Fixture que retorna el directorio de documentación"""
    return BASE_DIR / "docs"


@pytest.fixture(scope="session")
def evaluations_dir():
    """Fixture que retorna el directorio de evaluaciones"""
    return BASE_DIR / "evaluations"
