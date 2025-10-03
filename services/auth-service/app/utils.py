import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from app.models import db, RefreshToken

SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')
ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 3600))
REFRESH_TOKEN_EXPIRES = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 2592000))

def create_access_token(user):
    """Create JWT access token"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'is_admin': user.is_admin,
        'exp': datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def create_refresh_token(user):
    """Create JWT refresh token and store in database"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_EXPIRES),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    # Store in database
    refresh_token = RefreshToken(
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(seconds=REFRESH_TOKEN_EXPIRES)
    )
    db.session.add(refresh_token)
    db.session.commit()

    return token

def create_tokens(user):
    """Create both access and refresh tokens"""
    return {
        'access_token': create_access_token(user),
        'refresh_token': create_refresh_token(user),
        'token_type': 'Bearer',
        'expires_in': ACCESS_TOKEN_EXPIRES
    }

def decode_token(token):
    """Decode and verify JWT token"""
    return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Get token from header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            payload = decode_token(token)

            # Verify it's an access token
            if payload.get('type') != 'access':
                return jsonify({'error': 'Invalid token type'}), 401

            current_user = payload

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        return f(current_user, *args, **kwargs)

    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    @token_required
    def decorated(current_user, *args, **kwargs):
        if not current_user.get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403

        return f(current_user, *args, **kwargs)

    return decorated
