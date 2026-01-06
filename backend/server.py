#!/usr/bin/env python3
"""
Servidor API simple para ejecutar scripts de Python desde el frontend.

Este servidor proporciona endpoints REST para:
- Validar evaluaciones de traders
- Analizar métricas
- Consolidar reportes
- Gestionar evaluaciones (CRUD)
- Autenticación con Google OAuth
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import subprocess
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

from auth import verify_google_token, generate_jwt, require_auth

app = Flask(__name__)
CORS(app)  # Permitir CORS para desarrollo

# Directorios del proyecto
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / 'scripts'
EVALUATIONS_DIR = BASE_DIR / 'evaluations'
TEMP_DIR = EVALUATIONS_DIR / 'temp'
LEADERBOARD_DIR = BASE_DIR / 'data' / 'leaderboard'

# Crear directorios si no existen
TEMP_DIR.mkdir(parents=True, exist_ok=True)
LEADERBOARD_DIR.mkdir(parents=True, exist_ok=True)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    })


# ============================================
# AUTENTICACIÓN
# ============================================

@app.route('/api/auth/google', methods=['POST'])
def google_auth():
    """
    Autentica con token de Google y retorna JWT.

    Body: { "token": "google_id_token" }
    Returns: { "token": "jwt_token", "user": { email, name, picture } }
    """
    try:
        data = request.json
        google_token = data.get('token')

        if not google_token:
            return jsonify({'error': 'Token requerido'}), 400

        user_info = verify_google_token(google_token)

        if not user_info:
            return jsonify({'error': 'Autenticación fallida - Email no autorizado'}), 401

        # Generar JWT
        jwt_token = generate_jwt(user_info)

        return jsonify({
            'token': jwt_token,
            'user': {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }
        })
    except Exception as e:
        print(f"Error en autenticación: {e}")
        return jsonify({'error': 'Error de autenticación'}), 500


@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_auth():
    """
    Verifica que el token JWT es válido.
    Requiere header Authorization: Bearer <token>
    """
    return jsonify({
        'valid': True,
        'user': request.user
    })


# ============================================
# VALIDACIÓN Y ANÁLISIS
# ============================================

@app.route('/api/validate', methods=['POST'])
def validate():
    """
    Valida una evaluación de trader usando validate.py
    
    Body: TraderEvaluation JSON
    Returns: ValidationResult
    """
    try:
        data = request.json
        
        # Guardar temporalmente
        temp_file = TEMP_DIR / f'temp_validation_{datetime.now().timestamp()}.json'
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Ejecutar script de validación
        result = subprocess.run(
            ['python', str(SCRIPTS_DIR / 'validate.py'), str(temp_file)],
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR)
        )
        
        # Limpiar archivo temporal
        temp_file.unlink()
        
        # Parsear resultado
        valid = result.returncode == 0
        
        return jsonify({
            'valid': valid,
            'errors': [] if valid else [{'message': result.stderr, 'severity': 'error'}],
            'warnings': [],
            'output': result.stdout
        })
        
    except Exception as e:
        return jsonify({
            'valid': False,
            'errors': [{'message': str(e), 'severity': 'error'}],
            'warnings': []
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Analiza métricas de un trader usando analyze_metrics.py
    
    Body: { evaluation: TraderEvaluation, risk_profile?: string }
    Returns: TraderAnalysis
    """
    try:
        data = request.json
        evaluation = data.get('evaluation')
        risk_profile = data.get('risk_profile', evaluation.get('risk_profile', 'moderate'))
        
        # Guardar temporalmente
        temp_file = TEMP_DIR / f'temp_analysis_{datetime.now().timestamp()}.json'
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(evaluation, f, indent=2, ensure_ascii=False)
        
        # Ejecutar script de análisis
        result = subprocess.run(
            ['python', str(SCRIPTS_DIR / 'analyze_metrics.py'), 
             '--profile', risk_profile, str(temp_file)],
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR)
        )
        
        # Limpiar archivo temporal
        temp_file.unlink()
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        # Parsear salida (el script imprime a stdout)
        return jsonify({
            'success': True,
            'output': result.stdout,
            'raw_output': result.stdout
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze/multiple', methods=['POST'])
def analyze_multiple():
    """
    Analiza múltiples traders y genera ranking
    
    Body: { evaluations: TraderEvaluation[], risk_profile?: string }
    Returns: { ranking: TraderAnalysis[], portfolio_metrics: PortfolioMetrics }
    """
    try:
        data = request.json
        evaluations = data.get('evaluations', [])
        risk_profile = data.get('risk_profile', 'moderate')
        
        # Guardar evaluaciones temporalmente
        temp_files = []
        for i, evaluation in enumerate(evaluations):
            temp_file = TEMP_DIR / f'temp_multi_{i}_{datetime.now().timestamp()}.json'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(evaluation, f, indent=2, ensure_ascii=False)
            temp_files.append(str(temp_file))
        
        # Ejecutar script de análisis múltiple
        result = subprocess.run(
            ['python', str(SCRIPTS_DIR / 'analyze_metrics.py'), 
             '--profile', risk_profile] + temp_files,
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR)
        )
        
        # Limpiar archivos temporales
        for temp_file in temp_files:
            Path(temp_file).unlink()
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        return jsonify({
            'success': True,
            'output': result.stdout
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/consolidate', methods=['GET'])
def consolidate():
    """
    Consolida evaluaciones usando consolidate.py
    
    Query params: month?, profile?
    Returns: ConsolidatedReport
    """
    try:
        month = request.args.get('month')
        profile = request.args.get('profile')
        
        cmd = ['python', str(SCRIPTS_DIR / 'consolidate.py')]
        
        if month:
            cmd.extend(['--month', month])
        if profile:
            cmd.extend(['--profile', profile])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR)
        )
        
        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
        
        return jsonify({
            'success': True,
            'output': result.stdout
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluations', methods=['GET'])
def get_evaluations():
    """
    Obtiene todas las evaluaciones almacenadas
    
    Returns: TraderEvaluation[]
    """
    try:
        evaluations = []
        
        # Buscar todos los archivos JSON (excepto temp)
        for json_file in EVALUATIONS_DIR.rglob('*.json'):
            if 'temp' not in str(json_file) and 'examples' not in str(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        data['_source_file'] = json_file.name
                        evaluations.append(data)
                except Exception as e:
                    print(f"Error loading {json_file}: {e}")
        
        return jsonify(evaluations)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/evaluations/<filename>', methods=['GET'])
def get_evaluation(filename):
    """
    Obtiene una evaluación específica
    
    Returns: TraderEvaluation
    """
    try:
        # Buscar el archivo
        for json_file in EVALUATIONS_DIR.rglob(filename):
            if 'temp' not in str(json_file):
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_source_file'] = json_file.name
                    return jsonify(data)
        
        return jsonify({
            'error': 'Evaluation not found'
        }), 404
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/api/evaluations', methods=['POST'])
@require_auth
def save_evaluation():
    """
    Guarda una nueva evaluación (requiere autenticación)

    Body: TraderEvaluation
    Returns: { success: boolean, message: string, filename: string }
    """
    try:
        data = request.json
        
        # Generar nombre de archivo
        trader_name = data['candidate']['display_name'].replace(' ', '_').replace('/', '_')
        date = data['as_of_utc'][:10].replace('-', '')
        filename = f"trader_{trader_name}_{date}.json"
        
        # Determinar directorio (por mes)
        month = data['as_of_utc'][:7]  # YYYY-MM
        eval_dir = EVALUATIONS_DIR / month
        eval_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = eval_dir / filename
        
        # Guardar evaluación
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'Evaluación guardada: {filename}',
            'filename': filename
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluations/<filename>', methods=['PUT'])
@require_auth
def update_evaluation(filename):
    """
    Actualiza una evaluación existente (requiere autenticación)
    
    Body: TraderEvaluation
    Returns: { success: boolean, message: string }
    """
    try:
        data = request.json
        
        # Buscar el archivo
        for json_file in EVALUATIONS_DIR.rglob(filename):
            if 'temp' not in str(json_file):
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                return jsonify({
                    'success': True,
                    'message': f'Evaluación actualizada: {filename}'
                })
        
        return jsonify({
            'success': False,
            'error': 'Evaluation not found'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/evaluations/<filename>', methods=['DELETE'])
@require_auth
def delete_evaluation(filename):
    """
    Elimina una evaluación (requiere autenticación)
    
    Returns: { success: boolean, message: string }
    """
    try:
        # Buscar el archivo
        for json_file in EVALUATIONS_DIR.rglob(filename):
            if 'temp' not in str(json_file):
                json_file.unlink()
                
                return jsonify({
                    'success': True,
                    'message': f'Evaluación eliminada: {filename}'
                })
        
        return jsonify({
            'success': False,
            'error': 'Evaluation not found'
        }), 404
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ========================================
# LEADERBOARD ENDPOINTS
# ========================================

@app.route('/api/leaderboard/fetch', methods=['POST'])
def fetch_leaderboard():
    """
    Ejecuta colección de leaderboard de Binance

    Body: { period: string, limit: number, use_mock?: boolean }
    Returns: { success: boolean, data: object, stats: object }
    """
    try:
        data = request.json
        period = data.get('period', 'WEEKLY')
        limit = data.get('limit', 100)
        use_mock = data.get('use_mock', True)

        # Ejecutar collector
        cmd = [
            'python',
            str(SCRIPTS_DIR / 'leaderboard_collector.py'),
            '--period', period,
            '--limit', str(limit)
        ]

        if not use_mock:
            cmd.append('--real-api')

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR)
        )

        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500

        # Leer el snapshot más reciente
        snapshots = sorted(
            LEADERBOARD_DIR.glob(f'leaderboard_{period}_*.json'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if snapshots:
            with open(snapshots[0], 'r', encoding='utf-8') as f:
                snapshot_data = json.load(f)

            return jsonify({
                'success': True,
                'data': snapshot_data.get('data', {}),
                'metadata': snapshot_data.get('metadata', {}),
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No snapshot was created'
            }), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leaderboard/snapshots', methods=['GET'])
def list_snapshots():
    """
    Lista snapshots guardados del leaderboard

    Query params: period? (DAILY, WEEKLY, MONTHLY, ALL)
    Returns: { snapshots: SnapshotInfo[] }
    """
    try:
        period = request.args.get('period')

        pattern = f'leaderboard_{period}_*.json' if period else 'leaderboard_*.json'
        snapshot_files = sorted(
            LEADERBOARD_DIR.glob(pattern),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        snapshots = []
        for snapshot_path in snapshot_files:
            try:
                with open(snapshot_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metadata = data.get('metadata', {})
                    traders_count = len(data.get('data', {}).get('data', []))

                    snapshots.append({
                        'filename': snapshot_path.name,
                        'path': str(snapshot_path),
                        'collected_at': metadata.get('collected_at'),
                        'period': metadata.get('period'),
                        'traders_count': traders_count,
                        'size_kb': snapshot_path.stat().st_size / 1024
                    })
            except Exception as e:
                print(f"Error reading {snapshot_path.name}: {e}")

        return jsonify({
            'success': True,
            'snapshots': snapshots,
            'count': len(snapshots)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leaderboard/snapshots/<filename>', methods=['GET'])
def get_snapshot(filename):
    """
    Obtiene un snapshot específico

    Returns: SnapshotData
    """
    try:
        snapshot_path = LEADERBOARD_DIR / filename

        if not snapshot_path.exists():
            return jsonify({
                'success': False,
                'error': 'Snapshot not found'
            }), 404

        with open(snapshot_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return jsonify({
            'success': True,
            'snapshot': data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leaderboard/analyze', methods=['POST'])
def analyze_leaderboard():
    """
    Analiza leaderboard con sistema de scoring completo

    Body: {
        snapshot_filename?: string,  // Si no se proporciona, usa el más reciente
        profile: 'conservative' | 'moderate' | 'aggressive',
        top_n?: number,  // Limitar resultados (default: todos)
        export?: boolean  // Guardar análisis en JSON
    }
    Returns: { success: boolean, analysis: Analysis }
    """
    try:
        data = request.json
        snapshot_filename = data.get('snapshot_filename')
        risk_profile = data.get('profile', 'moderate')
        top_n = data.get('top_n')
        should_export = data.get('export', False)

        # Construir comando
        cmd = [
            'python',
            str(SCRIPTS_DIR / 'leaderboard_analyzer.py'),
            '--profile', risk_profile,
            '--data-dir', str(LEADERBOARD_DIR)
        ]

        if snapshot_filename:
            cmd.extend(['--snapshot', snapshot_filename])

        if top_n:
            cmd.extend(['--top', str(top_n)])

        # Si se requiere export, crear archivo temporal
        output_file = None
        if should_export or top_n:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = LEADERBOARD_DIR / f'analysis_{risk_profile}_{timestamp}.json'
            cmd.extend(['--output', str(output_file)])

        # Ejecutar analyzer
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(SCRIPTS_DIR)
        )

        if result.returncode != 0:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500

        # Si se exportó, leer el archivo
        if output_file and output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                analysis = json.load(f)

            return jsonify({
                'success': True,
                'analysis': analysis,
                'output_file': output_file.name if should_export else None
            })
        else:
            # Parsear output del CLI
            return jsonify({
                'success': True,
                'output': result.stdout,
                'message': 'Analysis completed - use export=true to get full JSON'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/leaderboard/candidates', methods=['POST'])
def filter_candidates():
    """
    Filtra traders del leaderboard por perfil de riesgo

    Body: {
        snapshot_filename?: string,  // Si no se proporciona, usa el más reciente
        risk_profile: 'conservative' | 'moderate' | 'aggressive',
        min_roi?: number,
        max_drawdown?: number,
        min_win_rate?: number
    }
    Returns: { candidates: Trader[], count: number }
    """
    try:
        data = request.json
        snapshot_filename = data.get('snapshot_filename')
        risk_profile = data.get('risk_profile', 'moderate')

        # Determinar snapshot a usar
        if snapshot_filename:
            snapshot_path = LEADERBOARD_DIR / snapshot_filename
        else:
            # Usar el más reciente
            snapshots = sorted(
                LEADERBOARD_DIR.glob('leaderboard_*.json'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            if not snapshots:
                return jsonify({
                    'success': False,
                    'error': 'No snapshots found'
                }), 404
            snapshot_path = snapshots[0]

        # Leer snapshot
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            snapshot = json.load(f)

        traders = snapshot.get('data', {}).get('data', [])

        # Definir límites por perfil (de docs/methodology.md)
        profile_limits = {
            'conservative': {
                'min_roi': 10.0,
                'max_roi': 30.0,
                'max_drawdown': 10.0,
                'min_win_rate': 60.0,
                'max_leverage': 2.0
            },
            'moderate': {
                'min_roi': 20.0,
                'max_roi': 60.0,
                'max_drawdown': 20.0,
                'min_win_rate': 55.0,
                'max_leverage': 3.0
            },
            'aggressive': {
                'min_roi': 40.0,
                'max_roi': 200.0,
                'max_drawdown': 35.0,
                'min_win_rate': 50.0,
                'max_leverage': 5.0
            }
        }

        limits = profile_limits.get(risk_profile, profile_limits['moderate'])

        # Overrides opcionales
        if 'min_roi' in data:
            limits['min_roi'] = data['min_roi']
        if 'max_drawdown' in data:
            limits['max_drawdown'] = data['max_drawdown']
        if 'min_win_rate' in data:
            limits['min_win_rate'] = data['min_win_rate']

        # Filtrar candidatos
        candidates = []
        for trader in traders:
            roi = trader.get('roi', 0)
            win_rate = trader.get('winRate', 0)
            leverage = trader.get('avgLeverage', 0)

            # Aplicar filtros
            if (limits['min_roi'] <= roi <= limits['max_roi'] and
                win_rate >= limits['min_win_rate'] and
                leverage <= limits['max_leverage']):

                candidates.append({
                    **trader,
                    'matched_profile': risk_profile,
                    'scores': {
                        'roi_score': min(100, (roi / limits['max_roi']) * 100),
                        'win_rate_score': (win_rate / 100) * 100,
                        'leverage_score': max(0, 100 - (leverage / limits['max_leverage']) * 100)
                    }
                })

        # Ordenar por ROI descendente
        candidates.sort(key=lambda x: x['roi'], reverse=True)

        return jsonify({
            'success': True,
            'candidates': candidates,
            'count': len(candidates),
            'profile': risk_profile,
            'limits_used': limits,
            'snapshot_used': snapshot_path.name
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("🚀 Akira Traders API Server")
    print(f"📁 Scripts directory: {SCRIPTS_DIR}")
    print(f"📁 Evaluations directory: {EVALUATIONS_DIR}")
    print(f"📁 Leaderboard directory: {LEADERBOARD_DIR}")
    print("🌐 Server running on http://localhost:3000")
    print("📡 API endpoints available at http://localhost:3000/api")
    print("\nPress Ctrl+C to stop the server\n")

    app.run(debug=True, port=3000, host='0.0.0.0')