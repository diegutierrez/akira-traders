# Akira Traders - Instrucciones de Proyecto

## Guias de Calidad (Referencia: diegutierrez/.github)

### Branching Strategy
```
main        <- produccion, solo recibe merges de test
test        <- ambiente de QA, recibe merges de development
development <- rama de integracion, los PRs van aca
```
Prefijos de branch: `feat/`, `fix/`, `refactor/`, `hotfix/`, `chore/`

### Formato de Commits
Conventional commits:
```
tipo(scope): descripcion breve
```
Tipos: `feat` | `fix` | `refactor` | `docs` | `style` | `test` | `chore`

### PR Template
- Descripcion del cambio y por que es necesario
- Tipo de cambio (feat/fix/refactor/docs/chore)
- Checklist: compila sin errores, no secrets en codigo, configs con defaults, logs sin datos sensibles, conventional commits

### Principios de Codigo
- **SOLID**: single responsibility, open/closed, dependency inversion
- **Errores**: no swallow exceptions, propagar con contexto, fail fast
- **Resiliencia**: retry con backoff exponencial, circuit breaker, fallback, timeouts en I/O
- **Seguridad**: no hardcodear credenciales (env vars), no loguear datos sensibles, validar inputs, menor privilegio
- **Observabilidad**: logs estructurados, niveles correctos (ERROR/WARN/INFO/DEBUG), contexto en cada log
- **Config**: toda config externalizable via env vars, defaults sensatos para dev local

### JavaScript / TypeScript
- Configuracion via env vars con defaults: `const PORT = process.env.PORT || 8080`
- Validar JSON antes de procesar (try/catch)
- async/await sobre callbacks
- Constantes agrupadas al inicio del archivo
- console.log (normal), console.warn (inesperado manejado), console.error (errores)
- Graceful shutdown (SIGINT handler)
- node_modules/ siempre en .gitignore

## Stack del Proyecto
- **Frontend**: React + TypeScript + Vite + TailwindCSS, desplegado en Vercel
- **Backend**: Supabase Edge Functions (Deno)
- **AI**: Gemini 2.5 Flash-Lite (coin reports)
- **Data**: Hyperliquid DEX API
- **MCP**: Supabase + GitHub (configurado en .mcp.json, gitignored)
