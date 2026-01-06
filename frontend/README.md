# 🎨 Akira Traders - Frontend Dashboard

> **Dashboard web profesional para evaluación y seguimiento de traders en Binance Copy Trading**

[![React](https://img.shields.io/badge/React-18.2+-61DAFB?logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?logo=typescript)](https://www.typescriptlang.org/)
[![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?logo=vite)](https://vitejs.dev/)
[![TailwindCSS](https://img.shields.io/badge/Tailwind-3.4+-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)

---

## 🎯 Características

### 🎨 Diseño Profesional
- **Estilo Binance-like**: Interfaz moderna y profesional inspirada en Binance
- **Dark/Light Mode**: Tema oscuro y claro con transiciones suaves
- **Responsive Design**: Optimizado para desktop, tablet y móvil
- **Animaciones Fluidas**: Transiciones y efectos visuales profesionales

### 🔐 Autenticación
- **Google OAuth 2.0**: Login seguro con cuenta de Google
- **Session Management**: Gestión de sesiones con tokens JWT
- **Protected Routes**: Rutas protegidas con autenticación
- **Auto-refresh**: Renovación automática de tokens

### 📊 Dashboard Interactivo
- **Vista de Traders**: Lista y cards de traders evaluados
- **Métricas en Tiempo Real**: Visualización de ROI, DD, Win Rate
- **Gráficos Avanzados**: Charts con Recharts/Chart.js
- **Filtros y Búsqueda**: Filtrado por perfil, score, métricas
- **Rankings**: Ordenamiento por múltiples criterios

### 🛠️ Gestión de Evaluaciones
- **CRUD Completo**: Crear, leer, actualizar, eliminar evaluaciones
- **Formularios Validados**: Validación con React Hook Form + Zod
- **Upload de Archivos**: Importar evaluaciones JSON
- **Export de Datos**: Exportar a JSON, CSV, PDF

---

## 📁 Estructura del Proyecto

```
frontend/
├── public/                      # Archivos estáticos
│   ├── favicon.ico
│   └── logo.svg
│
├── src/
│   ├── assets/                  # Recursos (imágenes, iconos)
│   │   ├── images/
│   │   └── icons/
│   │
│   ├── components/              # Componentes reutilizables
│   │   ├── common/              # Componentes comunes
│   │   │   ├── Button/
│   │   │   ├── Card/
│   │   │   ├── Input/
│   │   │   ├── Modal/
│   │   │   ├── Table/
│   │   │   └── Spinner/
│   │   │
│   │   ├── layout/              # Componentes de layout
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   ├── Footer/
│   │   │   └── MainLayout/
│   │   │
│   │   ├── traders/             # Componentes de traders
│   │   │   ├── TraderCard/
│   │   │   ├── TraderList/
│   │   │   ├── TraderDetail/
│   │   │   ├── TraderForm/
│   │   │   └── TraderMetrics/
│   │   │
│   │   ├── charts/              # Componentes de gráficos
│   │   │   ├── ROIChart/
│   │   │   ├── DrawdownChart/
│   │   │   └── PortfolioChart/
│   │   │
│   │   └── auth/                # Componentes de autenticación
│   │       ├── LoginButton/
│   │       ├── LogoutButton/
│   │       └── ProtectedRoute/
│   │
│   ├── pages/                   # Páginas de la aplicación
│   │   ├── Home/
│   │   ├── Dashboard/
│   │   ├── Traders/
│   │   ├── TraderDetail/
│   │   ├── NewEvaluation/
│   │   ├── Portfolio/
│   │   ├── Analytics/
│   │   ├── Settings/
│   │   └── Login/
│   │
│   ├── hooks/                   # Custom hooks
│   │   ├── useAuth.ts
│   │   ├── useTraders.ts
│   │   ├── useMetrics.ts
│   │   ├── useTheme.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── services/                # Servicios y API
│   │   ├── api/
│   │   │   ├── traders.ts
│   │   │   ├── evaluations.ts
│   │   │   └── analytics.ts
│   │   ├── auth/
│   │   │   ├── google.ts
│   │   │   └── jwt.ts
│   │   └── storage/
│   │       └── localStorage.ts
│   │
│   ├── store/                   # Estado global (Zustand/Redux)
│   │   ├── authStore.ts
│   │   ├── tradersStore.ts
│   │   ├── themeStore.ts
│   │   └── index.ts
│   │
│   ├── types/                   # TypeScript types
│   │   ├── trader.ts
│   │   ├── evaluation.ts
│   │   ├── metrics.ts
│   │   └── auth.ts
│   │
│   ├── utils/                   # Utilidades
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── calculations.ts
│   │   └── constants.ts
│   │
│   ├── styles/                  # Estilos globales
│   │   ├── globals.css
│   │   ├── themes.css
│   │   └── animations.css
│   │
│   ├── config/                  # Configuración
│   │   ├── env.ts
│   │   ├── routes.ts
│   │   └── api.ts
│   │
│   ├── App.tsx                  # Componente principal
│   ├── main.tsx                 # Entry point
│   └── vite-env.d.ts           # Tipos de Vite
│
├── .env.example                 # Variables de entorno ejemplo
├── .env.local                   # Variables de entorno local
├── .eslintrc.json              # Configuración ESLint
├── .prettierrc                 # Configuración Prettier
├── tsconfig.json               # Configuración TypeScript
├── vite.config.ts              # Configuración Vite
├── tailwind.config.js          # Configuración Tailwind
├── postcss.config.js           # Configuración PostCSS
├── package.json                # Dependencias
└── README.md                   # Este archivo
```

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Node.js 18+ y npm/yarn/pnpm
- Cuenta de Google Cloud Platform (para OAuth)
- Backend API corriendo (opcional para desarrollo)

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/akira-traders.git
cd akira-traders/frontend

# Instalar dependencias
npm install
# o
yarn install
# o
pnpm install

# Copiar variables de entorno
cp .env.example .env.local

# Configurar variables de entorno (ver sección siguiente)
vim .env.local

# Iniciar servidor de desarrollo
npm run dev
```

### Variables de Entorno

Crear archivo `.env.local`:

```env
# API Backend
VITE_API_URL=http://localhost:3000/api
VITE_API_TIMEOUT=30000

# Google OAuth
VITE_GOOGLE_CLIENT_ID=tu-client-id.apps.googleusercontent.com
VITE_GOOGLE_REDIRECT_URI=http://localhost:5173/auth/callback

# Configuración de la App
VITE_APP_NAME=Akira Traders
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development

# Features Flags
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DARK_MODE=true
```

---

## 📦 Dependencias Principales

### Core

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "typescript": "^5.3.0",
  "vite": "^5.0.0"
}
```

### UI y Estilos

```json
{
  "tailwindcss": "^3.4.0",
  "@headlessui/react": "^1.7.17",
  "@heroicons/react": "^2.1.0",
  "framer-motion": "^10.16.0",
  "clsx": "^2.0.0",
  "tailwind-merge": "^2.2.0"
}
```

### Estado y Datos

```json
{
  "zustand": "^4.4.7",
  "@tanstack/react-query": "^5.14.0",
  "axios": "^1.6.0",
  "zod": "^3.22.0"
}
```

### Formularios y Validación

```json
{
  "react-hook-form": "^7.49.0",
  "@hookform/resolvers": "^3.3.0"
}
```

### Gráficos

```json
{
  "recharts": "^2.10.0",
  "chart.js": "^4.4.0",
  "react-chartjs-2": "^5.2.0"
}
```

### Autenticación

```json
{
  "@react-oauth/google": "^0.12.0",
  "jwt-decode": "^4.0.0"
}
```

### Utilidades

```json
{
  "date-fns": "^3.0.0",
  "lodash-es": "^4.17.21",
  "react-hot-toast": "^2.4.1"
}
```

---

## 🎨 Sistema de Diseño

### Paleta de Colores (Binance-inspired)

```css
/* Colores Principales */
--primary: #F0B90B;        /* Amarillo Binance */
--primary-dark: #C99C0A;
--primary-light: #F3C94D;

/* Colores de Fondo */
--bg-primary: #0B0E11;     /* Fondo oscuro principal */
--bg-secondary: #1E2329;   /* Fondo oscuro secundario */
--bg-tertiary: #2B3139;    /* Fondo oscuro terciario */

/* Colores de Texto */
--text-primary: #EAECEF;   /* Texto principal */
--text-secondary: #848E9C; /* Texto secundario */
--text-tertiary: #5E6673;  /* Texto terciario */

/* Colores de Estado */
--success: #0ECB81;        /* Verde (ganancias) */
--danger: #F6465D;         /* Rojo (pérdidas) */
--warning: #F0B90B;        /* Amarillo (advertencia) */
--info: #3DCFFF;           /* Azul (información) */

/* Bordes */
--border: #2B3139;
--border-hover: #474D57;
```

### Tipografía

```css
/* Fuentes */
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;

/* Tamaños */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */
```

### Espaciado

```css
/* Sistema de espaciado (múltiplos de 4px) */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### Componentes Base

#### Button

```tsx
// Variantes: primary, secondary, danger, ghost
<Button variant="primary" size="md">
  Crear Evaluación
</Button>
```

#### Card

```tsx
<Card className="p-6">
  <Card.Header>
    <Card.Title>Trader Performance</Card.Title>
  </Card.Header>
  <Card.Body>
    {/* Contenido */}
  </Card.Body>
</Card>
```

#### Table

```tsx
<Table>
  <Table.Header>
    <Table.Row>
      <Table.Head>Trader</Table.Head>
      <Table.Head>ROI 90d</Table.Head>
      <Table.Head>Score</Table.Head>
    </Table.Row>
  </Table.Header>
  <Table.Body>
    {/* Filas */}
  </Table.Body>
</Table>
```

---

## 🔐 Autenticación con Google

### Configuración de Google Cloud

1. **Crear Proyecto en Google Cloud Console**
   - Ir a https://console.cloud.google.com
   - Crear nuevo proyecto "Akira Traders"

2. **Habilitar Google OAuth API**
   - APIs & Services → Library
   - Buscar "Google+ API" y habilitar

3. **Crear Credenciales OAuth 2.0**
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Web application
   - Authorized redirect URIs:
     - `http://localhost:5173/auth/callback` (desarrollo)
     - `https://tu-dominio.com/auth/callback` (producción)

4. **Copiar Client ID**
   - Copiar el Client ID generado
   - Agregar a `.env.local` como `VITE_GOOGLE_CLIENT_ID`

### Implementación en React

```tsx
// src/components/auth/GoogleLoginButton.tsx
import { GoogleLogin } from '@react-oauth/google';
import { useAuth } from '@/hooks/useAuth';

export function GoogleLoginButton() {
  const { loginWithGoogle } = useAuth();

  return (
    <GoogleLogin
      onSuccess={(credentialResponse) => {
        loginWithGoogle(credentialResponse.credential);
      }}
      onError={() => {
        console.error('Login Failed');
      }}
      theme="filled_black"
      size="large"
      text="signin_with"
      shape="rectangular"
    />
  );
}
```

### Hook de Autenticación

```tsx
// src/hooks/useAuth.ts
import { create } from 'zustand';
import { jwtDecode } from 'jwt-decode';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loginWithGoogle: (credential: string) => Promise<void>;
  logout: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  
  loginWithGoogle: async (credential) => {
    const decoded = jwtDecode(credential);
    // Enviar al backend para validación
    const response = await api.post('/auth/google', { credential });
    
    set({
      user: response.data.user,
      token: response.data.token,
      isAuthenticated: true,
    });
    
    localStorage.setItem('token', response.data.token);
  },
  
  logout: () => {
    set({ user: null, token: null, isAuthenticated: false });
    localStorage.removeItem('token');
  },
}));
```

---

## 📊 Páginas Principales

### 1. Dashboard

**Ruta**: `/dashboard`

**Características**:
- Resumen de portafolio
- Métricas agregadas (ROI, DD, Win Rate)
- Top 5 traders por score
- Gráfico de performance histórica
- Alertas y notificaciones

### 2. Traders

**Ruta**: `/traders`

**Características**:
- Lista de todos los traders evaluados
- Filtros por perfil, score, métricas
- Búsqueda por nombre
- Vista de cards o tabla
- Ordenamiento múltiple

### 3. Trader Detail

**Ruta**: `/traders/:id`

**Características**:
- Información completa del trader
- Métricas detalladas
- Gráficos de performance
- Historial de evaluaciones
- Acciones (editar, eliminar, copiar)

### 4. Nueva Evaluación

**Ruta**: `/evaluations/new`

**Características**:
- Formulario paso a paso
- Validación en tiempo real
- Preview de datos
- Cálculo automático de score
- Guardar como borrador

### 5. Portfolio

**Ruta**: `/portfolio`

**Características**:
- Vista consolidada del portafolio
- Distribución de asignaciones
- Métricas agregadas
- Rebalanceo sugerido
- Simulador de escenarios

### 6. Analytics

**Ruta**: `/analytics`

**Características**:
- Gráficos avanzados
- Comparativas históricas
- Análisis de correlación
- Exportar reportes
- Filtros temporales

---

## 🛠️ Scripts Disponibles

```bash
# Desarrollo
npm run dev              # Inicia servidor de desarrollo
npm run dev:host         # Inicia con acceso desde red local

# Build
npm run build            # Build de producción
npm run preview          # Preview del build

# Linting y Formateo
npm run lint             # Ejecuta ESLint
npm run lint:fix         # Corrige errores de ESLint
npm run format           # Formatea código con Prettier
npm run format:check     # Verifica formateo

# Testing
npm run test             # Ejecuta tests
npm run test:watch       # Tests en modo watch
npm run test:coverage    # Tests con coverage

# Type Checking
npm run type-check       # Verifica tipos de TypeScript

# Análisis
npm run analyze          # Analiza bundle size
```

---

## 🚢 Deployment

### Vercel (Recomendado)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Deploy a producción
vercel --prod
```

### Netlify

```bash
# Instalar Netlify CLI
npm i -g netlify-cli

# Deploy
netlify deploy

# Deploy a producción
netlify deploy --prod
```

### Docker

```dockerfile
# Dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```bash
# Build y run
docker build -t akira-traders-frontend .
docker run -p 80:80 akira-traders-frontend
```

---

## 📚 Recursos y Referencias

### Documentación
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [React Router](https://reactrouter.com/)

### Inspiración de Diseño
- [Binance](https://www.binance.com/)
- [Dribbble - Trading Dashboards](https://dribbble.com/search/trading-dashboard)
- [Behance - Crypto UI](https://www.behance.net/search/projects?search=crypto%20dashboard)

### Herramientas
- [Figma](https://www.figma.com/) - Diseño de UI
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [Redux DevTools](https://github.com/reduxjs/redux-devtools)

---

## 🤝 Contribuir

Ver [CONTRIBUTING.md](../CONTRIBUTING.md) para guías de contribución.

### Convenciones de Código

- **Componentes**: PascalCase (`TraderCard.tsx`)
- **Hooks**: camelCase con prefijo `use` (`useTraders.ts`)
- **Utilidades**: camelCase (`formatCurrency.ts`)
- **Constantes**: UPPER_SNAKE_CASE (`API_BASE_URL`)
- **Tipos**: PascalCase con sufijo `Type` o interfaz (`TraderType`, `ITrader`)

---

## 📄 Licencia

MIT License - Ver [LICENSE](../LICENSE) para detalles.

---

**Última actualización**: 2025-01-08  
**Versión**: 1.0.0  
**Autor**: Akira Traders Team