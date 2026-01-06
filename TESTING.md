# 🧪 Akira Traders - Documentación de Testing

## 📋 Resumen Ejecutivo

El **módulo de testing de Akira Traders** valida que el código implementado cumple con las especificaciones y documentación del proyecto. Incluye tests de cumplimiento, validación, integración y unitarios.

### 🎯 Objetivos

1. **Validar cumplimiento** con ARCHITECTURE.md y methodology.md
2. **Verificar integridad** de datos y schemas
3. **Garantizar funcionalidad** de scripts y APIs
4. **Mantener calidad** del código

---

## 📊 Estructura del Módulo de Testing

```
tests/
├── __init__.py                          # Paquete de tests
├── README.md                            # Documentación de tests
├── conftest.py                          # Configuración global de pytest
│
├── compliance/                          # Tests de cumplimiento
│   └── test_documentation_compliance.py # Valida contra documentación
│
├── unit/                                # Tests unitarios
│   ├── test_validation.py              # Validación de datos/schemas
│   └── test_scripts.py                 # Tests de scripts Python
│
├── integration/                         # Tests de integración
│   └── test_backend_api.py             # Tests de API REST
│
└── fixtures/                            # Datos de ejemplo
    └── sample_evaluations.json         # Evaluaciones de muestra

pytest.ini                               # Configuración de pytest
run_tests.py                             # Script ejecutor de tests
TESTING.md                               # Esta documentación
```

---

## 🚀 Ejecución Rápida

### Ejecutar todos los tests

```bash
python run_tests.py
```

### Ejecutar con cobertura

```bash
python run_tests.py --coverage
```

### Ejecutar tests específicos

```bash
python run_tests.py --compliance  # Solo cumplimiento
python run_tests.py --validation  # Solo validación
python run_tests.py --integration # Solo integración
python run_tests.py --unit        # Solo unitarios
```

---

## 📚 Categorías de Tests

### 1. **Compliance Tests** (Cumplimiento)

**Ubicación**: `tests/compliance/test_documentation_compliance.py`

**Objetivo**: Validar que el código cumple con las especificaciones documentadas.

**Clases de Tests**:

#### TestRiskProfileCompliance
Valida perfiles de riesgo según `docs/methodology.md`:

- ✅ Conservative (ROI 10-30%, DD ≤10%, WR ≥60%)
- ✅ Moderate (ROI 20-60%, DD ≤20%, WR ≥55%)
- ✅ Aggressive (ROI 40-200%, DD ≤35%, WR ≥50%)

```python
def test_methodology_file_exists(self):
    """Verifica que methodology.md existe"""

def test_risk_profiles_documented(self):
    """Verifica que los 3 perfiles estén documentados"""

def test_risk_profile_metrics_documented(self):
    """Verifica que todas las métricas clave estén documentadas"""
```

#### TestArchitectureCompliance
Valida estructura según `ARCHITECTURE.md`:

- ✅ Directorios requeridos (docs/, scripts/, backend/, frontend/)
- ✅ Scripts requeridos (validate.py, analyze_metrics.py, consolidate.py)
- ✅ Documentación completa

```python
def test_required_directories_exist(self):
    """Verifica que todos los directorios requeridos existan"""

def test_required_scripts_exist(self):
    """Verifica que todos los scripts requeridos existan"""
```

#### TestAPIEndpointCompliance
Valida endpoints del backend:

- ✅ `/api/health` - Health check
- ✅ `/api/validate` - Validación de evaluaciones
- ✅ `/api/analyze` - Análisis de métricas
- ✅ `/api/evaluations` - CRUD de evaluaciones

```python
def test_backend_has_health_endpoint(self):
    """Verifica que existe el endpoint de health check"""

def test_backend_has_crud_endpoints(self):
    """Verifica que existan los endpoints CRUD"""
```

#### TestScoringSystemCompliance
Valida sistema de scoring:

- ✅ Pesos por perfil (Conservative, Moderate, Aggressive)
- ✅ Rangos de scores (0-39: Pobre, 85-100: Excelente)
- ✅ Métricas ponderadas

#### TestDocumentationQuality
Valida calidad de documentación:

- ✅ README con secciones requeridas
- ✅ Diagramas en ARCHITECTURE.md
- ✅ Tablas de contenido

**Ejecutar**:
```bash
pytest tests/compliance/ -v
# o
python run_tests.py --compliance
```

---

### 2. **Validation Tests** (Validación)

**Ubicación**: `tests/unit/test_validation.py`

**Objetivo**: Validar integridad y correctitud de datos.

**Clases de Tests**:

#### TestTraderEvaluationSchema
Valida estructura de evaluaciones:

```python
def test_valid_evaluation_structure(self, valid_evaluation):
    """Verifica que una evaluación válida tenga todos los campos"""

def test_risk_profile_enum(self, valid_evaluation):
    """Verifica que el perfil de riesgo sea válido"""

def test_metrics_ranges(self, valid_evaluation):
    """Verifica que las métricas estén dentro de rangos válidos"""
```

**Validaciones**:
- ✅ Campos requeridos presentes
- ✅ Tipos de datos correctos
- ✅ Enums válidos (risk_profile, style, copy_mode)
- ✅ Rangos de métricas (0-100% para DD y WR)
- ✅ Arrays con 2 elementos para rangos

#### TestRiskProfileValidation
Valida límites por perfil:

```python
def test_moderate_profile_roi_range(self, moderate_profile_limits):
    """Verifica rango de ROI para perfil moderado"""

def test_conservative_is_more_restrictive_than_moderate(self):
    """Verifica que conservador sea más restrictivo"""
```

**Validaciones**:
- ✅ Conservative más restrictivo que Moderate
- ✅ Aggressive menos restrictivo que Moderate
- ✅ Límites coherentes entre perfiles

#### TestDataIntegrity
Valida integridad de datos existentes:

```python
def test_can_load_evaluation_files(self):
    """Verifica que archivos existentes sean JSON válidos"""

def test_timestamp_format_is_iso8601(self):
    """Verifica formato ISO 8601 en timestamps"""
```

**Ejecutar**:
```bash
pytest tests/unit/test_validation.py -v
# o
python run_tests.py --validation
```

---

### 3. **Backend API Tests** (Integración)

**Ubicación**: `tests/integration/test_backend_api.py`

**Objetivo**: Validar funcionalidad de endpoints REST.

**Clases de Tests**:

#### TestHealthEndpoint
```python
def test_health_endpoint_exists(self, client):
    """Verifica que /api/health existe y responde"""

def test_health_returns_json(self, client):
    """Verifica que retorna JSON válido"""
```

#### TestValidateEndpoint
```python
def test_validate_accepts_json(self, client, sample_evaluation):
    """Verifica que acepta evaluaciones JSON"""

def test_validate_response_structure(self, client):
    """Verifica estructura de respuesta"""
```

#### TestEvaluationsCRUD
```python
def test_get_evaluations_returns_array(self, client):
    """Verifica que GET retorna array de evaluaciones"""

def test_post_evaluation_endpoint_exists(self, client):
    """Verifica que POST funciona"""
```

**Ejecutar**:
```bash
pytest tests/integration/ -v
# o
python run_tests.py --integration
```

**Nota**: Requiere que el backend esté disponible.

---

### 4. **Scripts Tests** (Unitarios)

**Ubicación**: `tests/unit/test_scripts.py`

**Objetivo**: Validar scripts Python del proyecto.

**Clases de Tests**:

#### TestScriptsExistence
```python
@pytest.mark.parametrize("script_name", ["validate.py", "analyze_metrics.py", "consolidate.py"])
def test_script_exists(self, script_name):
    """Verifica que el script existe"""
```

#### TestValidateScript
```python
def test_validate_script_can_run(self):
    """Verifica que validate.py se pueda ejecutar"""
```

#### TestUtilsModule
```python
def test_utils_is_python_package(self):
    """Verifica que utils/ sea un paquete Python"""
```

**Ejecutar**:
```bash
pytest tests/unit/test_scripts.py -v
# o
python run_tests.py --unit
```

---

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

Fixtures globales disponibles:

```python
@pytest.fixture(scope="session")
def base_dir():
    """Directorio base del proyecto"""

@pytest.fixture(scope="session")
def scripts_dir():
    """Directorio de scripts"""
```

---

## 📊 Cobertura de Código

### Generar reporte de cobertura

```bash
python run_tests.py --coverage
```

### Ver reporte HTML

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Objetivos de cobertura

- **Compliance**: 100% (toda la documentación validada)
- **Scripts**: ≥80% (funciones críticas)
- **Backend**: ≥70% (endpoints principales)
- **Global**: ≥75%

---

## 🔍 Uso Avanzado

### Ejecutar test específico

```bash
pytest tests/compliance/test_documentation_compliance.py::TestRiskProfileCompliance::test_methodology_file_exists -v
```

### Ejecutar con markers

```bash
pytest -m compliance -v
pytest -m "unit and not slow" -v
```

### Modo verbose

```bash
pytest -vv -s  # Extra verbose con prints
```

### Generar reporte JUnit XML

```bash
python run_tests.py --report
```

El reporte se guarda en `test_reports/junit_report_<timestamp>.xml`

---

## 📈 Integración Continua (CI/CD)

### GitHub Actions (ejemplo)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py --coverage --report
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 🐛 Troubleshooting

### Error: ModuleNotFoundError

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/scripts:$(pwd)/backend"
```

### Error: No module named 'pytest'

```bash
pip install pytest pytest-cov
```

### Tests muy lentos

```bash
pytest -m "not slow" -v
```

### Ver solo failures

```bash
pytest --tb=short -x  # Stop en primer failure
pytest --lf  # Solo re-ejecutar failures anteriores
```

---

## 📝 Convenciones de Testing

### Nomenclatura

- **Archivos**: `test_*.py`
- **Clases**: `Test*`
- **Métodos**: `test_*`

### Estructura de un test

```python
class TestFeature:
    """Descripción de qué se testea"""

    @pytest.fixture
    def setup_data(self):
        """Fixture local"""
        return {"key": "value"}

    def test_something(self, setup_data):
        """Descripción clara del test"""
        # Arrange
        expected = "value"

        # Act
        result = setup_data["key"]

        # Assert
        assert result == expected
```

### Asserts

```python
# Preferir asserts con mensaje
assert condition, "Mensaje de error descriptivo"

# Comparaciones
assert actual == expected
assert value in collection
assert instance isinstance(obj, Class)
```

---

## 📚 Recursos

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

## ✅ Checklist para Pull Requests

Antes de crear un PR, verificar:

- [ ] Todos los tests pasan
- [ ] Cobertura ≥ objetivo (75%)
- [ ] Nuevas features tienen tests
- [ ] Tests de compliance actualizados si hay cambios en docs
- [ ] Sin warnings de pytest
- [ ] Reporte de cobertura revisado

---

## 🎯 Roadmap de Testing

### Fase Actual ✅
- [x] Tests de cumplimiento con documentación
- [x] Tests de validación de datos
- [x] Tests de integración de API
- [x] Tests unitarios de scripts

### Próximos Pasos 📅
- [ ] Tests end-to-end del flujo completo
- [ ] Tests de performance
- [ ] Tests de seguridad (validación de inputs)
- [ ] Mutation testing
- [ ] Property-based testing (Hypothesis)

---

**Última actualización**: 2025-01-09
**Versión**: 1.0.0
**Autor**: Akira Traders Team
