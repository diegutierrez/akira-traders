# 🔧 Scripts de Akira Traders

Scripts Python para validación, análisis y consolidación de evaluaciones de traders.

## 📋 Contenido

- [`validate.py`](validate.py) - Validación de evaluaciones
- [`analyze_metrics.py`](analyze_metrics.py) - Análisis de métricas y scoring
- [`consolidate.py`](consolidate.py) - Consolidación de múltiples evaluaciones
- [`utils/`](utils/) - Módulos de utilidades compartidas

## 🚀 Instalación

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r ../requirements.txt
```

## 📖 Uso

### 1. Validar Evaluación

Valida un archivo JSON contra el schema y reglas de negocio:

```bash
# Validar un archivo
python validate.py ../evaluations/examples/trader_example_20250107.json

# Validar múltiples archivos
python validate.py ../evaluations/2025-01/*.json

# Modo verbose
python validate.py --verbose ../evaluations/examples/trader_example_20250107.json
```

**Salida esperada:**
```
======================================================================
Validación de: trader_example_20250107.json
======================================================================

✅ Validación EXITOSA

✨ No se encontraron problemas

======================================================================
```

### 2. Analizar Métricas

Analiza métricas de traders y calcula scores:

```bash
# Analizar un trader
python analyze_metrics.py ../evaluations/examples/trader_example_20250107.json

# Analizar múltiples traders con ranking
python analyze_metrics.py ../evaluations/2025-01/*.json

# Especificar perfil de riesgo
python analyze_metrics.py --profile aggressive ../evaluations/2025-01/*.json

# Guardar resultados en JSON
python analyze_metrics.py --output analysis.json ../evaluations/2025-01/*.json
```

**Salida esperada:**
```
======================================================================
ANÁLISIS DE TRADER: CryptoMaster123
======================================================================

📊 Perfil de Riesgo: MODERATE
📅 Fecha de Evaluación: 2025-01-07T00:00:00Z

📈 MÉTRICAS PRINCIPALES:
  • ROI 90d: 42.7%
  • Max Drawdown: 14.5%
  • Win Rate: 61.0%
  • Leverage Promedio: 2.3×
  • Copiadores: 342

🎯 SCORES CALCULADOS:
  • Drawdown Score: 71.00/100
  • Win Rate Score: 52.50/100
  • ROI Score: 42.70/100
  • Consistency Score: 89.23/100
  • RAR Score: 58.90/100

⭐ SCORE TOTAL: 62.87/100
📋 Clasificación: Aceptable
💡 Recomendación: Revisión detallada requerida
```

### 3. Consolidar Evaluaciones

Consolida múltiples evaluaciones en un reporte unificado:

```bash
# Consolidar por mes
python consolidate.py --month 2025-01

# Filtrar por perfil de riesgo
python consolidate.py --month 2025-01 --profile moderate

# Especificar directorio y salida
python consolidate.py --directory ../evaluations/2025-01 --output consolidated.json
```

**Salida esperada:**
```
======================================================================
REPORTE CONSOLIDADO DE EVALUACIONES
======================================================================

📊 Total de Traders: 5
📅 Fecha de Generación: 2025-01-07 12:00:00 UTC

======================================================================
ESTADÍSTICAS GENERALES
======================================================================

ROI 90 días:
  • Promedio: 45.3%
  • Rango: 28.5% - 67.2%
  • Mediana: 42.7%

Max Drawdown:
  • Promedio: 16.2%
  • Rango: 10.3% - 19.8%
  • Mediana: 14.5%
```

## 🧩 Módulos de Utilidades

### SchemaValidator

Validador de schemas JSON:

```python
from utils.schema_validator import SchemaValidator

validator = SchemaValidator()
errors = validator.get_validation_errors(data)
is_valid = validator.is_valid(data)
```

### MetricsCalculator

Calculadora de métricas derivadas:

```python
from utils.metrics_calculator import MetricsCalculator, TraderMetrics

calculator = MetricsCalculator()

# Calcular RAR
rar = calculator.calculate_risk_adjusted_return(roi=42.7, max_drawdown=14.5)

# Calcular score total
metrics = TraderMetrics(
    display_name="Trader1",
    roi_90d=42.7,
    max_drawdown=14.5,
    win_rate=61.0,
    avg_leverage=2.3
)
scores = calculator.calculate_trader_score(metrics, "moderate")
```

## 📊 Ejemplos de Flujo Completo

### Flujo 1: Validar y Analizar

```bash
# 1. Validar evaluación
python validate.py ../evaluations/examples/trader_example_20250107.json

# 2. Si es válida, analizar métricas
python analyze_metrics.py ../evaluations/examples/trader_example_20250107.json
```

### Flujo 2: Análisis Mensual

```bash
# 1. Validar todas las evaluaciones del mes
python validate.py ../evaluations/2025-01/*.json

# 2. Generar ranking
python analyze_metrics.py --output ranking.json ../evaluations/2025-01/*.json

# 3. Consolidar reporte
python consolidate.py --month 2025-01 --output consolidated.json
```

## 🔍 Troubleshooting

### Error: ModuleNotFoundError

```bash
# Asegúrate de estar en el directorio scripts/
cd scripts/

# O agrega el directorio al PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: FileNotFoundError

```bash
# Verifica que el archivo existe
ls -la ../evaluations/examples/

# Usa rutas absolutas si es necesario
python validate.py /ruta/completa/al/archivo.json
```

### Error: json.JSONDecodeError

```bash
# Valida que el JSON sea correcto
python -m json.tool archivo.json

# O usa un validador online
cat archivo.json | jq .
```

## 📚 Documentación Adicional

- [Metodología de Selección](../docs/methodology.md)
- [Limitaciones y Riesgos](../docs/limitations.md)
- [Arquitectura del Sistema](../ARCHITECTURE.md)

## 🤝 Contribuir

Para contribuir mejoras a los scripts:

1. Sigue las convenciones de código (PEP 8)
2. Agrega docstrings a funciones y clases
3. Incluye type hints cuando sea posible
4. Escribe código simple y legible
5. Agrega comentarios para lógica compleja

## 📄 Licencia

MIT License - Ver [LICENSE](../LICENSE) para detalles.