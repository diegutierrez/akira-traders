# 📊 Akira Traders - Sistema de Evaluación de Copy Trading

> **Framework profesional para selección, evaluación y seguimiento de traders en Binance Copy Trading**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 🎯 Objetivo

Sistema de evaluación, documentación y seguimiento de traders de **Binance Copy Trading**, diseñado para inversores que buscan:

- ✅ **Control de Riesgo**: Límites claros y medibles
- ✅ **Trazabilidad**: Decisiones documentadas y auditables
- ✅ **Reproducibilidad**: Proceso estandarizado y repetible
- ✅ **Profesionalismo**: Enfoque de ingeniería aplicado al trading

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Perfiles de Riesgo](#-perfiles-de-riesgo)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Guía de Uso](#-guía-de-uso)
- [Documentación](#-documentación)
- [Ejemplos](#-ejemplos)
- [Roadmap](#-roadmap)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## ✨ Características

### 🏗️ Arquitectura Profesional

- **Schema-First**: Validación estricta mediante JSON Schema
- **Git as Source of Truth**: Versionado completo de evaluaciones
- **Multi-Format Output**: Reportes en Markdown, HTML y PDF
- **Separation of Concerns**: Datos, lógica y presentación separados

### 📊 Evaluación Cuantitativa

- **Métricas Estandarizadas**: ROI, Max DD, Win Rate, Leverage
- **Sistema de Scoring**: Puntuación ponderada 0-100
- **Risk-Adjusted Returns**: Métricas ajustadas por riesgo
- **Análisis Comparativo**: Ranking de múltiples traders

### 🛡️ Control de Riesgo

- **Perfiles Predefinidos**: Conservative, Moderate, Aggressive
- **Límites Automáticos**: Stop-loss y daily caps por trader
- **Diversificación**: Máximo 30% por trader
- **Monitoreo Continuo**: Revisiones programadas

### 📝 Documentación Completa

- **Templates Estandarizados**: Markdown y Jinja2
- **Evaluaciones Individuales**: Análisis detallado por trader
- **Reportes Consolidados**: Vista agregada del portafolio
- **Trazabilidad Total**: Historial completo en Git

### 🤖 Automatización

- **Validación Automática**: Pre-commit hooks y CI/CD
- **Generación de Reportes**: Scripts Python para MD/HTML/PDF
- **Análisis de Métricas**: Cálculo automático de scores
- **Consolidación**: Agregación de múltiples evaluaciones

---

## 🎚️ Perfiles de Riesgo

### Conservative (Conservador)

**Objetivo**: Preservación de capital con crecimiento moderado

| Métrica | Valor |
|---------|-------|
| ROI 90d | 10% - 30% |
| Max Drawdown | ≤ 10% |
| Win Rate | ≥ 60% |
| Leverage | 1× - 2× |
| Stop Copy | -5% a -8% |

**Ideal para**: Capital crítico, baja tolerancia al riesgo

---

### Moderate (Moderado) ⭐ **Recomendado**

**Objetivo**: Balance entre crecimiento y control de riesgo

| Métrica | Valor |
|---------|-------|
| ROI 90d | 20% - 60% |
| Max Drawdown | ≤ 20% |
| Win Rate | ≥ 55% |
| Leverage | 1× - 3× |
| Stop Copy | -10% a -12% |

**Ideal para**: Mayoría de inversores, balance riesgo/retorno

---

### Aggressive (Agresivo)

**Objetivo**: Maximización de retornos con riesgo elevado

| Métrica | Valor |
|---------|-------|
| ROI 90d | 40% - 100%+ |
| Max Drawdown | ≤ 35% |
| Win Rate | ≥ 50% |
| Leverage | 2× - 5× |
| Stop Copy | -15% a -20% |

**Ideal para**: Capital especulativo, alta tolerancia al riesgo

---

## 📁 Estructura del Proyecto

```
akira-traders/
├── README.md                          # Este archivo
├── ARCHITECTURE.md                    # Arquitectura técnica
├── CONTRIBUTING.md                    # Guía de contribución
├── LICENSE                            # Licencia MIT
├── .gitignore                         # Exclusiones Git
├── requirements.txt                   # Dependencias Python
├── pyproject.toml                     # Configuración Python
│
├── docs/                              # Documentación
│   ├── methodology.md                 # Metodología de selección
│   ├── limitations.md                 # Limitaciones y riesgos
│   ├── workflow.md                    # Flujo de trabajo
│   └── glossary.md                    # Glosario de términos
│
├── schemas/                           # JSON Schemas
│   ├── trader-evaluation.schema.json  # Schema principal
│   └── risk-profile.schema.json       # Schema de perfiles
│
├── templates/                         # Plantillas
│   ├── markdown/
│   │   ├── trader-evaluation.md       # Template evaluación
│   │   ├── executive-summary.md       # Template ejecutivo
│   │   └── technical-annex.md         # Template técnico
│   └── jinja2/
│       ├── executive-report.j2        # Reporte ejecutivo
│       ├── technical-report.j2        # Reporte técnico
│       └── consolidated-report.j2     # Reporte consolidado
│
├── evaluations/                       # Evaluaciones de traders
│   ├── 2025-01/                       # Por mes
│   │   ├── trader_example_20250107.json
│   │   └── trader_example_20250107.md
│   └── archive/                       # Históricas
│
├── reports/                           # Reportes generados
│   ├── executive/                     # Ejecutivos
│   ├── technical/                     # Técnicos
│   └── consolidated/                  # Consolidados
│
└── scripts/                           # Scripts Python
    ├── validate.py                    # Validación
    ├── generate_report.py             # Generación reportes
    ├── analyze_metrics.py             # Análisis métricas
    ├── consolidate.py                 # Consolidación
    └── utils/                         # Utilidades
```

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.11 o superior
- Git
- Cuenta de Binance con Copy Trading habilitado

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/akira-traders.git
cd akira-traders

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar pre-commit hooks
pre-commit install

# Verificar instalación
python scripts/validate.py --version
```

### Dependencias Principales

```
jsonschema>=4.20.0      # Validación de schemas
jinja2>=3.1.2           # Templates
pandas>=2.1.4           # Análisis de datos
markdown>=3.5.1         # Generación MD
weasyprint>=60.1        # Generación PDF
pyyaml>=6.0.1          # Configuración
```

---

## 📖 Guía de Uso

### 1️⃣ Búsqueda y Filtrado

#### Opción A: Leaderboard Collector (Automatizado) ✨ NUEVO

Usa el script de colección automática para obtener datos del Binance Leaderboard:

```bash
# Activar entorno virtual
source venv/bin/activate

# Colectar ranking semanal (top 15 traders)
python scripts/leaderboard_collector.py --period WEEKLY --limit 15

# Colectar ranking diario (top 100)
python scripts/leaderboard_collector.py --period DAILY --limit 100

# Listar snapshots guardados
python scripts/leaderboard_collector.py --list
```

Los datos se guardan en `data/leaderboard/` con metadata y timestamps.

**Nota**: Por defecto usa datos mock realistas. Ver [BINANCE_API_LIMITATIONS.md](docs/BINANCE_API_LIMITATIONS.md) para detalles.

#### Opción B: Búsqueda Manual

Accede a [Binance Copy Trading](https://www.binance.com/es/copy-trading) y filtra por:

- **Tipo**: Futures USD-M
- **Riesgo**: Bajo / Medio (según perfil)
- **Duración**: > 90 días
- **ROI 90d**: Según perfil (ej: 20-60% para Moderate)
- **Max DD**: Según perfil (ej: < 20% para Moderate)

### 2️⃣ Captura de Métricas

Para cada trader candidato, captura:

```
✅ Nombre del trader
✅ URL del perfil
✅ ROI 30d / 90d / 180d
✅ Max Drawdown
✅ Win Rate
✅ Leverage promedio
✅ Número de copiadores
✅ Activos operados
✅ Estilo de trading
```

**Tip**: Toma screenshots como evidencia

### 3️⃣ Crear Evaluación

Usa el template de evaluación:

```bash
# Copiar template
cp templates/markdown/trader-evaluation.md \
   evaluations/2025-01/trader_nombre_20250108.md

# Editar con tus datos
vim evaluations/2025-01/trader_nombre_20250108.md
```

Completa todas las secciones:
- ✅ Resumen Ejecutivo
- ✅ Métricas Técnicas
- ✅ Riesgos Conocidos
- ✅ Recomendaciones

### 4️⃣ Generar JSON

Convierte el Markdown a JSON estandarizado:

```bash
python scripts/convert_md_to_json.py \
  evaluations/2025-01/trader_nombre_20250108.md
```

O crea el JSON manualmente siguiendo el schema.

### 5️⃣ Validar

Valida el JSON contra el schema:

```bash
python scripts/validate.py \
  evaluations/2025-01/trader_nombre_20250108.json
```

**Output esperado**:
```
✅ Schema validation: PASSED
✅ Metrics consistency: PASSED
✅ Risk profile alignment: PASSED
```

### 6️⃣ Generar Reportes

#### Reporte Individual

```bash
python scripts/generate_report.py \
  --input evaluations/2025-01/trader_nombre_20250108.json \
  --output reports/executive/trader_nombre_20250108.pdf \
  --type executive
```

#### Reporte Consolidado

```bash
python scripts/consolidate.py \
  --month 2025-01 \
  --output reports/consolidated/2025-01.pdf
```

### 7️⃣ Commit y Versionado

```bash
# Agregar archivos
git add evaluations/2025-01/trader_nombre_20250108.*

# Commit con mensaje descriptivo
git commit -m "feat(evaluation): Add TraderNombre evaluation (moderate profile)"

# Push
git push origin main
```

### 8️⃣ Activar Copia en Binance

1. Login en Binance
2. Ir a Copy Trading
3. Buscar el trader
4. Configurar parámetros:
   - **Modo**: Fixed Amount
   - **Monto**: Según recomendación (ej: 50 USDT)
   - **Stop Copy**: Según perfil (ej: -12%)
5. Activar copia

### 9️⃣ Monitoreo Continuo

**Revisión Diaria** (5 min):
- Verificar DD actual vs límite
- Revisar pérdidas del día
- Confirmar que no hay alertas

**Revisión Semanal** (30 min):
- Actualizar métricas en JSON
- Regenerar reportes
- Evaluar performance vs benchmark
- Ajustar asignaciones si necesario

**Revisión Mensual** (2 horas):
- Re-evaluación completa de traders
- Decisión de continuidad
- Búsqueda de nuevos candidatos
- Actualización de documentación

---

## 📚 Documentación

### Documentos Principales

| Documento | Descripción |
|-----------|-------------|
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Arquitectura técnica del sistema |
| [`docs/methodology.md`](docs/methodology.md) | Metodología de selección y scoring |
| [`docs/limitations.md`](docs/limitations.md) | Limitaciones y riesgos conocidos |
| [`docs/workflow.md`](docs/workflow.md) | Flujo de trabajo detallado |
| [`docs/BINANCE_API_LIMITATIONS.md`](docs/BINANCE_API_LIMITATIONS.md) | Limitaciones del API de Binance y soluciones ✨ NUEVO |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Guía de contribución |

### Schemas

- [`schemas/trader-evaluation.schema.json`](schemas/trader-evaluation.schema.json): Schema principal de evaluación
- [`schemas/risk-profile.schema.json`](schemas/risk-profile.schema.json): Schema de perfiles de riesgo

### Templates

- [`templates/markdown/trader-evaluation.md`](templates/markdown/trader-evaluation.md): Template de evaluación individual
- [`templates/jinja2/executive-report.j2`](templates/jinja2/executive-report.j2): Template de reporte ejecutivo
- [`templates/jinja2/technical-report.j2`](templates/jinja2/technical-report.j2): Template de reporte técnico

---

## 💡 Ejemplos

### Ejemplo 1: Evaluación Completa

Ver [`evaluations/examples/trader_example_20250107.json`](evaluations/examples/trader_example_20250107.json)

```json
{
  "as_of_utc": "2025-01-07T00:00:00Z",
  "risk_profile": "moderate",
  "candidate": {
    "display_name": "CryptoMaster123",
    "metrics": {
      "roi_90d_pct": 42.7,
      "max_drawdown_pct": 14.5,
      "win_rate_pct": 61.0,
      "avg_leverage": 2.3
    },
    "style": "swing",
    "copy_mode_suggestion": "fixed",
    "order_size_suggestion_usdt": 50
  }
}
```

### Ejemplo 2: Reporte Ejecutivo

Ver [`reports/examples/executive-summary-2025-01.pdf`](reports/examples/executive-summary-2025-01.pdf)

**Contenido**:
- Resumen de 5 traders seleccionados
- Métricas agregadas del portafolio
- Distribución de riesgo
- Recomendaciones de asignación

### Ejemplo 3: Workflow Completo

Ver [`docs/examples/complete-workflow.md`](docs/examples/complete-workflow.md)

Ejemplo paso a paso de evaluación, desde búsqueda hasta activación.

---

## 🗺️ Roadmap

### ✅ Fase 1: Fundación (Completada)

- [x] Estructura de directorios
- [x] Documentación base
- [x] Schemas JSON
- [x] Templates Markdown

### 🔄 Fase 2: Automatización (En Progreso)

- [ ] Scripts de validación
- [ ] Generador de reportes
- [ ] Analizador de métricas
- [ ] Pre-commit hooks
- [ ] CI/CD pipeline

### 📅 Fase 3: Mejoras (Planificado)

- [ ] Dashboard web interactivo
- [ ] Alertas automáticas (email/Telegram)
- [ ] Backtesting de estrategias
- [ ] API wrapper para Binance (si disponible)
- [ ] Machine Learning para scoring

### 🔮 Fase 4: Avanzado (Futuro)

- [ ] Multi-exchange support
- [ ] Portfolio optimization
- [ ] Risk simulation (Monte Carlo)
- [ ] Social trading analytics
- [ ] Mobile app

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor lee [`CONTRIBUTING.md`](CONTRIBUTING.md) para detalles sobre:

- Código de conducta
- Proceso de pull requests
- Estándares de código
- Guía de estilo

### Formas de Contribuir

1. 🐛 **Reportar Bugs**: Abre un issue con detalles
2. 💡 **Sugerir Features**: Propón mejoras
3. 📝 **Mejorar Docs**: Corrige o expande documentación
4. 🔧 **Código**: Implementa features o fixes
5. 🧪 **Testing**: Agrega tests
6. 📊 **Evaluaciones**: Comparte evaluaciones de traders

### Quick Start para Contribuidores

```bash
# Fork el repo
# Clonar tu fork
git clone https://github.com/tu-usuario/akira-traders.git

# Crear branch
git checkout -b feature/mi-feature

# Hacer cambios
# ...

# Commit
git commit -m "feat: Add mi feature"

# Push
git push origin feature/mi-feature

# Crear Pull Request en GitHub
```

---

## ⚠️ Disclaimer

**IMPORTANTE**: Este sistema es una herramienta de evaluación y documentación. **NO** constituye asesoramiento financiero.

### Advertencias

- ❌ **No garantiza ganancias**
- ❌ **El trading conlleva riesgo de pérdida total**
- ❌ **Performance pasada no garantiza resultados futuros**
- ❌ **Invierte solo lo que puedas permitirte perder**

### Responsabilidades

- ✅ **Usuario**: Responsable de sus decisiones de inversión
- ✅ **Sistema**: Proporciona framework y metodología
- ✅ **Educación**: Entender completamente los riesgos

Ver [`docs/limitations.md`](docs/limitations.md) para detalles completos.

---

## 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

```
MIT License

Copyright (c) 2025 Akira Traders

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 📞 Contacto

- **GitHub**: [github.com/tu-usuario/akira-traders](https://github.com/tu-usuario/akira-traders)
- **Issues**: [github.com/tu-usuario/akira-traders/issues](https://github.com/tu-usuario/akira-traders/issues)
- **Discussions**: [github.com/tu-usuario/akira-traders/discussions](https://github.com/tu-usuario/akira-traders/discussions)

---

## 🙏 Agradecimientos

- **Binance**: Por la plataforma de Copy Trading
- **Comunidad Cripto**: Por compartir conocimiento
- **Contribuidores**: Por mejorar este proyecto

---

## 📊 Estadísticas del Proyecto

![GitHub stars](https://img.shields.io/github/stars/tu-usuario/akira-traders?style=social)
![GitHub forks](https://img.shields.io/github/forks/tu-usuario/akira-traders?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/tu-usuario/akira-traders?style=social)

---

<div align="center">

**⭐ Si este proyecto te resulta útil, considera darle una estrella en GitHub ⭐**

**Hecho con ❤️ por la comunidad de Akira Traders**

</div>