"""
Módulo de autenticación con Google OAuth 2.0
"""
from functools import wraps
from flask import request, jsonify
import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
import os
from datetime import datetime, timedelta

GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
ALLOWED_EMAIL = os.environ.get('ALLOWED_EMAIL')
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-change-in-production')


def verify_google_token(token: str) -> dict | None:
    """
    Verifica el token de Google y retorna la info del usuario.
    Retorna None si el token es inválido o el email no está autorizado.
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # Verificar que el email esté autorizado
        if ALLOWED_EMAIL and idinfo.get('email') != ALLOWED_EMAIL:
            print(f"Email no autorizado: {idinfo.get('email')}")
            return None

        return idinfo
    except Exception as e:
        print(f"Error verificando token de Google: {e}")
        return None


def generate_jwt(user_info: dict) -> str:
    """
    Genera un JWT con la información del usuario.
    """
    payload = {
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture'),
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')


def verify_jwt(token: str) -> dict | None:
    """
    Verifica un JWT y retorna el payload.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])

        # Verificar email autorizado
        if ALLOWED_EMAIL and payload.get('email') != ALLOWED_EMAIL:
            return None

        return payload
    except jwt.ExpiredSignatureError:
        print("Token expirado")
        return None
    except jwt.InvalidTokenError as e:
        print(f"Token inválido: {e}")
        return None


def require_auth(f):
    """
    Decorator para proteger endpoints.
    Requiere header Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({'error': 'No autorizado - Token requerido'}), 401

        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No autorizado - Formato inválido'}), 401

        token = auth_header.split(' ')[1]
        payload = verify_jwt(token)

        if not payload:
            return jsonify({'error': 'No autorizado - Token inválido'}), 401

        # Agregar info del usuario al request
        request.user = payload
        return f(*args, **kwargs)

    return decorated
