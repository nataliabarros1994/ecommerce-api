from flask import Blueprint, request, jsonify
from app.models import db, User, RefreshToken
from app.utils import create_tokens, decode_token, token_required
from datetime import datetime, timedelta
import jwt

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()

        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 409

        # Create new user
        user = User(email=data['email'])
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Generate tokens
        tokens = create_tokens(user)

        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'tokens': tokens
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return tokens"""
    try:
        data = request.get_json()

        # Validate input
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400

        # Find user
        user = User.query.filter_by(email=data['email']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401

        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403

        # Generate tokens
        tokens = create_tokens(user)

        return jsonify({
            'message': 'Login successful',
            'user': user.to_dict(),
            'tokens': tokens
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """Refresh access token using refresh token"""
    try:
        data = request.get_json()
        refresh_token = data.get('refresh_token')

        if not refresh_token:
            return jsonify({'error': 'Refresh token is required'}), 400

        # Verify refresh token in database
        token_record = RefreshToken.query.filter_by(token=refresh_token).first()

        if not token_record or token_record.is_revoked:
            return jsonify({'error': 'Invalid refresh token'}), 401

        if token_record.expires_at < datetime.utcnow():
            return jsonify({'error': 'Refresh token expired'}), 401

        # Decode token to get user info
        try:
            payload = decode_token(refresh_token)
            user = User.query.get(payload['user_id'])

            if not user or not user.is_active:
                return jsonify({'error': 'User not found or inactive'}), 401

            # Generate new tokens
            tokens = create_tokens(user)

            # Revoke old refresh token
            token_record.is_revoked = True
            db.session.commit()

            return jsonify({
                'message': 'Token refreshed successfully',
                'tokens': tokens
            }), 200

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Refresh token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid refresh token'}), 401

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/verify', methods=['POST'])
def verify():
    """Verify access token"""
    try:
        data = request.get_json()
        token = data.get('token')

        if not token:
            return jsonify({'error': 'Token is required'}), 400

        payload = decode_token(token)

        return jsonify({
            'valid': True,
            'user_id': payload['user_id'],
            'email': payload['email'],
            'is_admin': payload.get('is_admin', False)
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout(current_user):
    """Revoke all refresh tokens for user"""
    try:
        RefreshToken.query.filter_by(user_id=current_user['user_id']).update({'is_revoked': True})
        db.session.commit()

        return jsonify({'message': 'Logged out successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """Get current user information"""
    try:
        user = User.query.get(current_user['user_id'])

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
