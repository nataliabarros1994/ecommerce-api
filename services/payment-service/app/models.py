from datetime import datetime
from bson import ObjectId

class Payment:
    """Payment model for MongoDB"""

    @staticmethod
    def create(data):
        """Create a payment document"""
        return {
            'user_id': data.get('user_id'),
            'order_id': data.get('order_id'),
            'amount': data.get('amount'),
            'currency': data.get('currency', 'USD'),
            'payment_method': data.get('payment_method', 'card'),
            'status': 'pending',
            'transaction_id': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

    @staticmethod
    def to_dict(payment):
        """Convert MongoDB document to dict"""
        if not payment:
            return None

        return {
            'id': str(payment['_id']),
            'user_id': payment.get('user_id'),
            'order_id': payment.get('order_id'),
            'amount': payment.get('amount'),
            'currency': payment.get('currency'),
            'payment_method': payment.get('payment_method'),
            'status': payment.get('status'),
            'transaction_id': payment.get('transaction_id'),
            'created_at': payment.get('created_at').isoformat() if payment.get('created_at') else None,
            'updated_at': payment.get('updated_at').isoformat() if payment.get('updated_at') else None
        }
