# 🚀 Guía de Inicio Rápido - Akira Traders

## ⚡ Inicio en 5 Minutos

### 1. Instalar Dependencias

```bash
# Frontend
cd frontend
npm install

# Backend (en otra terminal)
cd backend
pip install -r requirements.txt
```

### 2. Iniciar Servidores

```bash
# Terminal 1: Backend API
cd backend
python server.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 3. Abrir en el Navegador

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:3000

## 📁 Estructura del Proyecto

```
akira-traders/
├── frontend/                    # Aplicación React
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   ├── pages/              # Páginas de la aplicación
│   │   ├── services/           # Servicios API
│   │   ├── types/              # Tipos TypeScript
│   │   ├── utils/              # Utilidades
│   │   ├── styles/             # Estilos globales
│   │   ├── App.tsx             # Componente principal
│   │   └── main.tsx            # Entry point
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # API Python
│   ├── server.py               # Servidor Flask
│   └── requirements.txt
│
├── scripts/                     # Scripts Python
│   ├── validate.py             # Validación
│   ├── analyze_metrics.py      # Análisis
│   ├── consolidate.py          # Consolidación
│   └── utils/                  # Utilidades
│
└── evaluations/                 # Evaluaciones JSON
    └── YYYY-MM/                # Organizadas por mes
```

## 🎯 Funcionalidades Principales

### 1. Dashboard
- Vista general de traders
- Métricas agregadas
- Gráficos de performance

### 2. Lista de Traders
- Filtros por perfil de riesgo
- Búsqueda por nombre
- Ordenamiento por métricas

### 3. Detalle de Trader
- Información completa
- Gráficos detallados
- Historial de evaluaciones

### 4. Nueva Evaluación
- Formulario paso a paso
- Validación en tiempo real
- Cálculo automático de scores

### 5. Analytics
- Reportes consolidados
- Comparativas
- Exportación de datos

## 🔧 Scripts Disponibles

### Frontend

```bash
npm run dev              # Desarrollo
npm run build            # Build producción
npm run preview          # Preview build
npm run lint             # Linting
npm run format           # Formateo
npm run type-check       # Type checking
```

### Backend

```bash
python server.py         # Iniciar servidor
```

### Scripts Python (vía API)

```bash
# Validar evaluación
curl -X POST http://localhost:3000/api/validate \
  -H "Content-Type: application/json" \
  -d @evaluations/examples/trader_example_20250107.json

# Analizar trader
curl -X POST http://localhost:3000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"evaluation": {...}, "risk_profile": "moderate"}'

# Consolidar evaluaciones
curl http://localhost:3000/api/consolidate?month=2025-01
```

## 📊 Flujo de Trabajo

1. **Crear Evaluación**
   - Ir a "Nueva Evaluación"
   - Completar formulario
   - Validar datos
   - Guardar

2. **Analizar Trader**
   - El sistema calcula automáticamente:
     - Scores individuales
     - Score total
     - Clasificación
     - Recomendación

3. **Ver Dashboard**
   - Métricas agregadas
   - Rankings
   - Gráficos

4. **Exportar Reportes**
   - Consolidar por mes
   - Filtrar por perfil
   - Exportar JSON

## 🎨 Tecnologías Utilizadas

### Frontend
- **React 18** - UI Library
- **TypeScript** - Type Safety
- **Vite** - Build Tool
- **Tailwind CSS** - Styling
- **React Query** - Data Fetching
- **Zustand** - State Management
- **Recharts** - Gráficos
- **React Hook Form** - Formularios

### Backend
- **Python 3.11+** - Runtime
- **Flask** - Web Framework
- **Flask-CORS** - CORS Support

## 🔐 Seguridad

- Validación de datos en frontend y backend
- Sanitización de inputs
- CORS configurado
- Sin autenticación (desarrollo local)

## 📝 Próximos Pasos

1. ✅ Explorar el dashboard
2. ✅ Crear tu primera evaluación
3. ✅ Analizar métricas
4. ✅ Generar reportes
5. 🎨 Personalizar estilos
6. 🔧 Agregar nuevas funcionalidades

## 🐛 Troubleshooting

### Puerto ocupado
```bash
# Cambiar puerto en vite.config.ts o server.py
```

### Dependencias faltantes
```bash
# Reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Backend no responde
```bash
# Verificar que esté corriendo
curl http://localhost:3000/api/health
```

## 📚 Documentación Completa

- [README.md](./README.md) - Documentación principal
- [INSTALLATION.md](./INSTALLATION.md) - Guía de instalación
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura
- [COMPONENTS_GUIDE.md](./COMPONENTS_GUIDE.md) - Componentes

## 🤝 Soporte

¿Problemas? Consulta la documentación o revisa los logs:
- Frontend: Consola del navegador
- Backend: Terminal donde corre `server.py`