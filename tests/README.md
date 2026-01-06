# 🧪 Akira Traders - Test Suite

Suite completa de tests que valida el cumplimiento del código con la documentación y especificaciones del proyecto.

## 📋 Contenido

### **Compliance Tests** (`compliance/`)
Tests que validan que el código implementado cumple con la documentación:

- `test_documentation_compliance.py` - Verifica cumplimiento con ARCHITECTURE.md y methodology.md
  - ✅ Perfiles de riesgo definidos
  - ✅ Estructura del proyecto
  - ✅ Endpoints de API
  - ✅ Sistema de scoring
  - ✅ Calidad de documentación

### **Unit Tests** (`unit/`)
Tests unitarios para componentes individuales:

- `test_validation.py` - Validación de schemas y datos
  - ✅ Estructura de evaluaciones
  - ✅ Rangos de métricas
  - ✅ Perfiles de riesgo
  - ✅ Integridad de datos

- `test_scripts.py` - Tests de scripts Python
  - ✅ Existencia de scripts
  - ✅ Funcionalidad básica
  - ✅ Dependencias

### **Integration Tests** (`integration/`)
Tests de integración entre componentes:

- `test_backend_api.py` - Tests del servidor Flask
  - ✅ Endpoints de API
  - ✅ Manejo de errores
  - ✅ CORS
  - ✅ CRUD de evaluaciones

## 🚀 Uso

### Ejecutar todos los tests

```bash
python run_tests.py
```

### Ejecutar solo tests de cumplimiento

```bash
python run_tests.py --compliance
```

### Ejecutar tests con cobertura

```bash
python run_tests.py --coverage
```

### Ejecutar tests específicos

```bash
# Solo validación
python run_tests.py --validation

# Solo integración
python run_tests.py --integration

# Solo unitarios
python run_tests.py --unit
```

### Generar reporte XML

```bash
python run_tests.py --report
```

## 📊 Categorías de Tests

### 1. **Compliance** (Cumplimiento)
Valida que el código cumpla con las especificaciones documentadas:

```bash
pytest -m compliance -v
```

Tests incluidos:
- Perfiles de riesgo según methodology.md
- Estructura del proyecto según ARCHITECTURE.md
- Endpoints de API según especificación
- Sistema de scoring documentado

### 2. **Validation** (Validación)
Valida integridad y correctitud de datos:

```bash
pytest -m validation -v
```

Tests incluidos:
- Schemas JSON válidos
- Rangos de métricas correctos
- Tipos de datos apropiados
- Campos requeridos presentes

### 3. **Integration** (Integración)
Valida integración entre componentes:

```bash
pytest -m integration -v
```

Tests incluidos:
- Endpoints de API funcionales
- Comunicación backend-scripts
- Flujo de datos completo

### 4. **Unit** (Unitarios)
Tests de componentes individuales:

```bash
pytest -m unit -v
```

Tests incluidos:
- Funciones de cálculo
- Validadores
- Utilidades

## 🛠️ Configuración

### pytest.ini
Configuración principal de pytest:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
markers =
    compliance: Tests de cumplimiento
    validation: Tests de validación
    integration: Tests de integración
    unit: Tests unitarios
```

### conftest.py
Fixtures globales disponibles en todos los tests:

- `base_dir` - Directorio base del proyecto
- `scripts_dir` - Directorio de scripts
- `backend_dir` - Directorio del backend
- `docs_dir` - Directorio de documentación
- `evaluations_dir` - Directorio de evaluaciones

## 📈 Cobertura de Código

Para generar reporte de cobertura:

```bash
python run_tests.py --coverage
```

Esto generará:
- Reporte en consola
- Reporte HTML en `htmlcov/`

Abrir reporte HTML:

```bash
# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html

# Windows
start htmlcov/index.html
```

## 🔍 Tests Específicos

### Ejecutar un archivo de test específico

```bash
pytest tests/compliance/test_documentation_compliance.py -v
```

### Ejecutar una clase de tests específica

```bash
pytest tests/unit/test_validation.py::TestTraderEvaluationSchema -v
```

### Ejecutar un test individual

```bash
pytest tests/unit/test_validation.py::TestTraderEvaluationSchema::test_valid_evaluation_structure -v
```

## 📝 Agregar Nuevos Tests

### 1. Crear archivo de test

```python
# tests/unit/test_new_feature.py

import pytest

class TestNewFeature:
    """Tests para nueva funcionalidad"""

    def test_something(self):
        """Descripción del test"""
        assert True
```

### 2. Marcar con categoría

```python
@pytest.mark.unit
def test_unit_feature():
    assert True

@pytest.mark.integration
def test_integration_feature():
    assert True
```

### 3. Usar fixtures

```python
def test_with_fixture(base_dir):
    """Usa fixture global"""
    assert base_dir.exists()
```

## 🎯 Objetivos de Testing

### Cobertura Mínima
- **Compliance**: 100% (toda la documentación debe estar validada)
- **Scripts**: 80% (funciones críticas cubiertas)
- **Backend**: 70% (endpoints principales cubiertos)

### Tipos de Tests

1. **Smoke Tests**: Verifican que el sistema arranca
2. **Functional Tests**: Verifican funcionalidad específica
3. **Compliance Tests**: Verifican cumplimiento con specs
4. **Integration Tests**: Verifican integración entre componentes

## 🐛 Troubleshooting

### Error: ModuleNotFoundError

```bash
# Asegúrate de que el directorio de scripts esté en el path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/scripts"
```

### Error: No module named 'pytest'

```bash
# Instalar pytest
pip install pytest pytest-cov
```

### Tests muy lentos

```bash
# Omitir tests lentos
pytest -m "not slow"
```

### Ver output detallado

```bash
# Modo extra verbose con output completo
pytest -vv -s
```

## 📚 Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

## 🤝 Contribuir

Al agregar código nuevo:

1. ✅ Escribir tests para nueva funcionalidad
2. ✅ Asegurar que todos los tests pasen
3. ✅ Mantener cobertura > 70%
4. ✅ Documentar tests complejos

## 📄 Licencia

MIT License - Ver [LICENSE](../LICENSE) para detalles.
