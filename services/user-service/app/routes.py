from flask import Blueprint, request, jsonify
from app.models import db, UserProfile
from app.utils import token_required

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    """Get user profile"""
    try:
        profile = UserProfile.query.filter_by(user_id=current_user['user_id']).first()

        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        return jsonify(profile.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['POST', 'PUT'])
@token_required
def create_or_update_profile(current_user):
    """Create or update user profile"""
    try:
        data = request.get_json()

        profile = UserProfile.query.filter_by(user_id=current_user['user_id']).first()

        if profile:
            # Update existing profile
            for key, value in data.items():
                if hasattr(profile, key) and key != 'id' and key != 'user_id':
                    setattr(profile, key, value)
        else:
            # Create new profile
            profile = UserProfile(user_id=current_user['user_id'], **data)
            db.session.add(profile)

        db.session.commit()

        return jsonify({
            'message': 'Profile updated successfully',
            'profile': profile.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['DELETE'])
@token_required
def delete_profile(current_user):
    """Delete user profile"""
    try:
        profile = UserProfile.query.filter_by(user_id=current_user['user_id']).first()

        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        db.session.delete(profile)
        db.session.commit()

        return jsonify({'message': 'Profile deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
@token_required
def get_user_profile(current_user, user_id):
    """Get any user's profile (for admin or public info)"""
    try:
        profile = UserProfile.query.filter_by(user_id=user_id).first()

        if not profile:
            return jsonify({'error': 'Profile not found'}), 404

        return jsonify(profile.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
