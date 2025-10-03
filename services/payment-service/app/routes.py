from flask import Blueprint, request, jsonify, current_app
from app.models import Payment
from app.utils import token_required, get_db
from bson import ObjectId
from datetime import datetime
import uuid

payments_bp = Blueprint('payments', __name__)

@payments_bp.route('/', methods=['POST'])
@token_required
def create_payment(current_user):
    """Create a new payment"""
    try:
        data = request.get_json()

        # Validate input
        if not data or not data.get('order_id') or not data.get('amount'):
            return jsonify({'error': 'Order ID and amount are required'}), 400

        # Create payment document
        payment_data = Payment.create({
            'user_id': current_user['user_id'],
            'order_id': data['order_id'],
            'amount': float(data['amount']),
            'currency': data.get('currency', 'USD'),
            'payment_method': data.get('payment_method', 'card')
        })

        # Insert into database
        db = get_db()
        result = db.payments.insert_one(payment_data)

        # Simulate payment processing
        payment_data['_id'] = result.inserted_id
        payment_data['transaction_id'] = f"txn_{uuid.uuid4().hex[:16]}"
        payment_data['status'] = 'completed'  # In real app, this would be async

        # Update payment
        db.payments.update_one(
            {'_id': result.inserted_id},
            {'$set': {
                'status': 'completed',
                'transaction_id': payment_data['transaction_id'],
                'updated_at': datetime.utcnow()
            }}
        )

        return jsonify({
            'message': 'Payment processed successfully',
            'payment': Payment.to_dict(payment_data)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<payment_id>', methods=['GET'])
@token_required
def get_payment(current_user, payment_id):
    """Get a specific payment"""
    try:
        db = get_db()
        payment = db.payments.find_one({'_id': ObjectId(payment_id)})

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Check if user owns this payment or is admin
        if payment['user_id'] != current_user['user_id'] and not current_user.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify(Payment.to_dict(payment)), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/order/<order_id>', methods=['GET'])
@token_required
def get_payment_by_order(current_user, order_id):
    """Get payment by order ID"""
    try:
        db = get_db()
        payment = db.payments.find_one({'order_id': order_id})

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Check if user owns this payment or is admin
        if payment['user_id'] != current_user['user_id'] and not current_user.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify(Payment.to_dict(payment)), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/user', methods=['GET'])
@token_required
def get_user_payments(current_user):
    """Get all payments for current user"""
    try:
        db = get_db()
        payments = db.payments.find({'user_id': current_user['user_id']}).sort('created_at', -1)

        return jsonify([Payment.to_dict(p) for p in payments]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@payments_bp.route('/<payment_id>/refund', methods=['POST'])
@token_required
def refund_payment(current_user, payment_id):
    """Refund a payment"""
    try:
        db = get_db()
        payment = db.payments.find_one({'_id': ObjectId(payment_id)})

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Check permissions (only admin can refund)
        if not current_user.get('is_admin'):
            return jsonify({'error': 'Admin privileges required'}), 403

        if payment['status'] != 'completed':
            return jsonify({'error': 'Only completed payments can be refunded'}), 400

        # Update payment status
        db.payments.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': {
                'status': 'refunded',
                'updated_at': datetime.utcnow()
            }}
        )

        payment['status'] = 'refunded'
        payment['updated_at'] = datetime.utcnow()

        return jsonify({
            'message': 'Payment refunded successfully',
            'payment': Payment.to_dict(payment)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
