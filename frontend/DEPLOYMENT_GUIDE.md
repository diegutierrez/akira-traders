# 🚀 Guía de Deployment - Akira Traders Frontend

## 📋 Índice

1. [Preparación para Producción](#preparación-para-producción)
2. [Deployment en Vercel](#deployment-en-vercel)
3. [Deployment en Netlify](#deployment-en-netlify)
4. [Deployment con Docker](#deployment-con-docker)
5. [CI/CD con GitHub Actions](#cicd-con-github-actions)
6. [Optimizaciones](#optimizaciones)
7. [Monitoreo](#monitoreo)

---

## 🔧 Preparación para Producción

### 1. Variables de Entorno

Crear archivo `.env.production`:

```env
# API Backend (Producción)
VITE_API_URL=https://api.akira-traders.com/api
VITE_API_TIMEOUT=30000

# Google OAuth (Producción)
VITE_GOOGLE_CLIENT_ID=tu-client-id-produccion.apps.googleusercontent.com
VITE_GOOGLE_REDIRECT_URI=https://akira-traders.com/auth/callback

# Configuración de la App
VITE_APP_NAME=Akira Traders
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=production

# Features
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_DARK_MODE=true

# Analytics (opcional)
VITE_GA_TRACKING_ID=G-XXXXXXXXXX
VITE_SENTRY_DSN=https://xxx@sentry.io/xxx
```

### 2. Build de Producción

```bash
# Instalar dependencias
npm ci

# Ejecutar linter
npm run lint

# Ejecutar tests
npm run test

# Build optimizado
npm run build

# Preview del build
npm run preview
```

### 3. Optimizaciones Pre-Deploy

#### package.json

```json
{
  "scripts": {
    "build": "tsc && vite build",
    "build:analyze": "vite build --mode analyze",
    "preview": "vite preview --port 4173"
  }
}
```

#### vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ],
  build: {
    target: 'es2015',
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom', 'react-router-dom'],
          'ui-vendor': ['@headlessui/react', 'framer-motion'],
          'chart-vendor': ['recharts', 'chart.js'],
          'utils-vendor': ['axios', 'date-fns', 'lodash-es'],
        },
      },
    },
    chunkSizeWarningLimit: 1000,
  },
});
```

---

## ☁️ Deployment en Vercel

### Opción 1: Deploy desde CLI

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy a preview
vercel

# Deploy a producción
vercel --prod
```

### Opción 2: Deploy desde GitHub

1. **Conectar Repositorio**
   ```
   1. Ir a https://vercel.com
   2. Click en "New Project"
   3. Importar repositorio de GitHub
   4. Seleccionar "akira-traders"
   ```

2. **Configurar Proyecto**
   ```
   Framework Preset: Vite
   Root Directory: frontend/
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm ci
   ```

3. **Variables de Entorno**
   ```
   Settings → Environment Variables
   
   Agregar todas las variables de .env.production:
   - VITE_API_URL
   - VITE_GOOGLE_CLIENT_ID
   - VITE_GOOGLE_REDIRECT_URI
   - etc.
   ```

4. **Deploy**
   ```
   Click en "Deploy"
   Esperar a que termine el build
   ```

### Configuración de Dominio

```bash
# Agregar dominio personalizado
vercel domains add akira-traders.com

# Configurar DNS
# Agregar registro A:
# @ → 76.76.21.21

# Agregar registro CNAME:
# www → cname.vercel-dns.com
```

### vercel.json

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

---

## 🌐 Deployment en Netlify

### Opción 1: Deploy desde CLI

```bash
# Instalar Netlify CLI
npm i -g netlify-cli

# Login
netlify login

# Inicializar sitio
netlify init

# Deploy a preview
netlify deploy

# Deploy a producción
netlify deploy --prod
```

### Opción 2: Deploy desde GitHub

1. **Conectar Repositorio**
   ```
   1. Ir a https://app.netlify.com
   2. Click en "New site from Git"
   3. Conectar con GitHub
   4. Seleccionar repositorio
   ```

2. **Configurar Build**
   ```
   Base directory: frontend/
   Build command: npm run build
   Publish directory: frontend/dist
   ```

3. **Variables de Entorno**
   ```
   Site settings → Build & deploy → Environment
   
   Agregar variables:
   - VITE_API_URL
   - VITE_GOOGLE_CLIENT_ID
   - etc.
   ```

### netlify.toml

```toml
[build]
  base = "frontend/"
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.js"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"

[[headers]]
  for = "/*.css"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

---

## 🐳 Deployment con Docker

### Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci

# Copiar código fuente
COPY . .

# Build de producción
RUN npm run build

# Production stage
FROM nginx:alpine

# Copiar build
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf

```nginx
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/javascript application/json;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Cache static assets
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (opcional)
    location /api/ {
        proxy_pass http://backend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    networks:
      - app-network

  backend:
    image: akira-traders-backend:latest
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
    restart: unless-stopped
    networks:
      - app-network

networks:
  app-network:
    driver: bridge
```

### Comandos Docker

```bash
# Build imagen
docker build -t akira-traders-frontend:latest .

# Run contenedor
docker run -d -p 80:80 --name akira-frontend akira-traders-frontend:latest

# Ver logs
docker logs -f akira-frontend

# Detener contenedor
docker stop akira-frontend

# Docker Compose
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

## 🔄 CI/CD con GitHub Actions

### .github/workflows/deploy.yml

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
    paths:
      - 'frontend/**'
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Run linter
        working-directory: ./frontend
        run: npm run lint
      
      - name: Run tests
        working-directory: ./frontend
        run: npm run test
      
      - name: Type check
        working-directory: ./frontend
        run: npm run type-check

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./frontend
        run: npm ci
      
      - name: Build
        working-directory: ./frontend
        run: npm run build
        env:
          VITE_API_URL: ${{ secrets.VITE_API_URL }}
          VITE_GOOGLE_CLIENT_ID: ${{ secrets.VITE_GOOGLE_CLIENT_ID }}
          VITE_GOOGLE_REDIRECT_URI: ${{ secrets.VITE_GOOGLE_REDIRECT_URI }}
      
      - name: Upload build artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist
          path: frontend/dist

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Download build artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist
          path: frontend/dist
      
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
          vercel-args: '--prod'
```

### Secrets de GitHub

```
Settings → Secrets and variables → Actions

Agregar secrets:
- VERCEL_TOKEN
- VERCEL_ORG_ID
- VERCEL_PROJECT_ID
- VITE_API_URL
- VITE_GOOGLE_CLIENT_ID
- VITE_GOOGLE_REDIRECT_URI
```

---

## ⚡ Optimizaciones

### 1. Code Splitting

```typescript
// Lazy loading de rutas
const DashboardPage = lazy(() => import('@/pages/Dashboard'));
const TradersPage = lazy(() => import('@/pages/Traders'));

// Uso con Suspense
<Suspense fallback={<LoadingScreen />}>
  <Routes>
    <Route path="/dashboard" element={<DashboardPage />} />
    <Route path="/traders" element={<TradersPage />} />
  </Routes>
</Suspense>
```

### 2. Image Optimization

```typescript
// Usar formatos modernos
<picture>
  <source srcSet="/logo.webp" type="image/webp" />
  <source srcSet="/logo.avif" type="image/avif" />
  <img src="/logo.png" alt="Logo" />
</picture>

// Lazy loading de imágenes
<img
  src="/trader.jpg"
  loading="lazy"
  decoding="async"
  alt="Trader"
/>
```

### 3. Preload Critical Resources

```html
<!-- index.html -->
<head>
  <!-- Preload fonts -->
  <link
    rel="preload"
    href="/fonts/inter.woff2"
    as="font"
    type="font/woff2"
    crossorigin
  />
  
  <!-- Preconnect to API -->
  <link rel="preconnect" href="https://api.akira-traders.com" />
  <link rel="dns-prefetch" href="https://api.akira-traders.com" />
</head>
```

### 4. Service Worker (PWA)

```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'Akira Traders',
        short_name: 'Akira',
        description: 'Sistema de evaluación de traders',
        theme_color: '#F0B90B',
        background_color: '#0B0E11',
        display: 'standalone',
        icons: [
          {
            src: '/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: '/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
});
```

---

## 📊 Monitoreo

### 1. Google Analytics

```typescript
// src/utils/analytics.ts
export const initGA = () => {
  const trackingId = import.meta.env.VITE_GA_TRACKING_ID;
  
  if (!trackingId) return;
  
  const script = document.createElement('script');
  script.src = `https://www.googletagmanager.com/gtag/js?id=${trackingId}`;
  script.async = true;
  document.head.appendChild(script);
  
  window.dataLayer = window.dataLayer || [];
  function gtag(...args: any[]) {
    window.dataLayer.push(args);
  }
  gtag('js', new Date());
  gtag('config', trackingId);
};

export const trackPageView = (path: string) => {
  if (window.gtag) {
    window.gtag('config', import.meta.env.VITE_GA_TRACKING_ID, {
      page_path: path,
    });
  }
};
```

### 2. Sentry (Error Tracking)

```typescript
// src/main.tsx
import * as Sentry from '@sentry/react';

if (import.meta.env.PROD) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    environment: import.meta.env.VITE_APP_ENV,
    tracesSampleRate: 1.0,
  });
}
```

### 3. Performance Monitoring

```typescript
// src/utils/performance.ts
export const reportWebVitals = (onPerfEntry?: (metric: any) => void) => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};
```

---

## 📚 Checklist de Deployment

### Pre-Deploy

- [ ] Tests pasando
- [ ] Linter sin errores
- [ ] Build exitoso localmente
- [ ] Variables de entorno configuradas
- [ ] Google OAuth configurado para producción
- [ ] API backend funcionando

### Deploy

- [ ] Build de producción generado
- [ ] Assets optimizados
- [ ] Source maps deshabilitados
- [ ] Console.logs removidos
- [ ] Dominio configurado
- [ ] SSL/HTTPS habilitado

### Post-Deploy

- [ ] Sitio accesible
- [ ] Login con Google funcionando
- [ ] API conectada correctamente
- [ ] Responsive en móvil
- [ ] Performance aceptable (Lighthouse > 90)
- [ ] Analytics configurado
- [ ] Error tracking activo

---

## 📚 Referencias

- [Vite Production Build](https://vitejs.dev/guide/build.html)
- [Vercel Documentation](https://vercel.com/docs)
- [Netlify Documentation](https://docs.netlify.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Última actualización**: 2025-01-08  
**Versión**: 1.0.0  
**Autor**: Akira Traders Team