# 📦 Guía de Instalación - Akira Traders Frontend

## 🚀 Instalación Rápida

### 1. Instalar Dependencias de Node.js

```bash
cd frontend
npm install
```

### 2. Configurar Variables de Entorno

```bash
cp .env.example .env.local
```

Edita `.env.local` con tus configuraciones:

```env
VITE_API_URL=http://localhost:3000/api
VITE_SCRIPTS_PATH=../scripts
```

### 3. Iniciar Servidor de Desarrollo

```bash
npm run dev
```

El frontend estará disponible en: http://localhost:5173

## 🐍 Backend API (Python)

Para que el frontend pueda ejecutar los scripts de Python, necesitas un servidor backend simple.

### Opción 1: Usar el servidor incluido

Crea un archivo `backend/server.py` en la raíz del proyecto:

```python
#!/usr/bin/env python3
"""
Servidor API simple para ejecutar scripts de Python desde el frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import subprocess
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

SCRIPTS_DIR = Path(__file__).parent.parent / 'scripts'
EVALUATIONS_DIR = Path(__file__).parent.parent / 'evaluations'

@app.route('/api/validate', methods=['POST'])
def validate():
    """Valida una evaluación"""
    data = request.json
    
    # Guardar temporalmente
    temp_file = EVALUATIONS_DIR / 'temp' / 'temp_evaluation.json'
    temp_file.parent.mkdir(exist_ok=True)
    
    with open(temp_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Ejecutar script de validación
    result = subprocess.run(
        ['python', str(SCRIPTS_DIR / 'validate.py'), str(temp_file)],
        capture_output=True,
        text=True
    )
    
    # Parsear resultado
    valid = result.returncode == 0
    
    return jsonify({
        'valid': valid,
        'output': result.stdout,
        'errors': result.stderr if not valid else None
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analiza métricas de un trader"""
    data = request.json
    evaluation = data.get('evaluation')
    risk_profile = data.get('risk_profile', 'moderate')
    
    # Guardar temporalmente
    temp_file = EVALUATIONS_DIR / 'temp' / 'temp_evaluation.json'
    temp_file.parent.mkdir(exist_ok=True)
    
    with open(temp_file, 'w') as f:
        json.dump(evaluation, f, indent=2)
    
    # Ejecutar script de análisis
    result = subprocess.run(
        ['python', str(SCRIPTS_DIR / 'analyze_metrics.py'), 
         '--profile', risk_profile, str(temp_file)],
        capture_output=True,
        text=True
    )
    
    return jsonify({
        'success': result.returncode == 0,
        'output': result.stdout,
        'error': result.stderr if result.returncode != 0 else None
    })

@app.route('/api/consolidate', methods=['GET'])
def consolidate():
    """Consolida evaluaciones"""
    month = request.args.get('month')
    profile = request.args.get('profile')
    
    cmd = ['python', str(SCRIPTS_DIR / 'consolidate.py')]
    
    if month:
        cmd.extend(['--month', month])
    if profile:
        cmd.extend(['--profile', profile])
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    return jsonify({
        'success': result.returncode == 0,
        'output': result.stdout,
        'error': result.stderr if result.returncode != 0 else None
    })

@app.route('/api/evaluations', methods=['GET'])
def get_evaluations():
    """Obtiene todas las evaluaciones"""
    evaluations = []
    
    for json_file in EVALUATIONS_DIR.rglob('*.json'):
        if 'temp' not in str(json_file):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    data['_source_file'] = json_file.name
                    evaluations.append(data)
            except Exception as e:
                print(f"Error loading {json_file}: {e}")
    
    return jsonify(evaluations)

@app.route('/api/evaluations', methods=['POST'])
def save_evaluation():
    """Guarda una nueva evaluación"""
    data = request.json
    
    # Generar nombre de archivo
    trader_name = data['candidate']['display_name'].replace(' ', '_')
    date = data['as_of_utc'][:10].replace('-', '')
    filename = f"trader_{trader_name}_{date}.json"
    
    # Determinar directorio (por mes)
    month = data['as_of_utc'][:7]  # YYYY-MM
    eval_dir = EVALUATIONS_DIR / month
    eval_dir.mkdir(exist_ok=True)
    
    filepath = eval_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return jsonify({
        'success': True,
        'message': f'Evaluación guardada: {filename}',
        'filename': filename
    })

if __name__ == '__main__':
    app.run(debug=True, port=3000)
```

### Instalar dependencias del backend:

```bash
pip install flask flask-cors
```

### Iniciar el servidor backend:

```bash
python backend/server.py
```

El backend estará disponible en: http://localhost:3000

## 📝 Scripts Disponibles

```bash
# Desarrollo
npm run dev              # Inicia servidor de desarrollo

# Build
npm run build            # Build de producción
npm run preview          # Preview del build

# Linting
npm run lint             # Ejecuta ESLint
npm run lint:fix         # Corrige errores de ESLint

# Formateo
npm run format           # Formatea código con Prettier
npm run format:check     # Verifica formateo

# Type Checking
npm run type-check       # Verifica tipos de TypeScript

# Scripts de Python (requieren backend corriendo)
npm run validate         # Ejecuta validación
npm run analyze          # Ejecuta análisis
npm run consolidate      # Ejecuta consolidación
```

## 🔧 Solución de Problemas

### Error: Cannot find module

```bash
# Eliminar node_modules y reinstalar
rm -rf node_modules package-lock.json
npm install
```

### Error: Port 5173 already in use

```bash
# Cambiar puerto en vite.config.ts
server: {
  port: 5174, // Cambiar a otro puerto
}
```

### Error: Backend no responde

```bash
# Verificar que el backend esté corriendo
curl http://localhost:3000/api/evaluations

# Si no responde, reiniciar el servidor backend
python backend/server.py
```

## 📚 Próximos Pasos

1. ✅ Instalar dependencias
2. ✅ Configurar variables de entorno
3. ✅ Iniciar backend API
4. ✅ Iniciar frontend
5. 🎨 Explorar el dashboard
6. 📊 Crear tu primera evaluación

## 🤝 Soporte

Si encuentras problemas, consulta:
- [README.md](./README.md) - Documentación principal
- [ARCHITECTURE.md](./ARCHITECTURE.md) - Arquitectura del sistema
- [COMPONENTS_GUIDE.md](./COMPONENTS_GUIDE.md) - Guía de componentes