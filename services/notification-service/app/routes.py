from flask import Blueprint, request, jsonify, current_app
from app.utils import token_required, send_email
import logging

notifications_bp = Blueprint('notifications', __name__)
logger = logging.getLogger(__name__)

@notifications_bp.route('/email', methods=['POST'])
@token_required
def send_email_notification(current_user):
    """Send an email notification"""
    try:
        data = request.get_json()

        # Validate input
        if not data or not data.get('to') or not data.get('subject') or not data.get('body'):
            return jsonify({'error': 'To, subject, and body are required'}), 400

        # Send email
        result = send_email(
            to=data['to'],
            subject=data['subject'],
            body=data['body']
        )

        if result:
            return jsonify({'message': 'Email sent successfully'}), 200
        else:
            return jsonify({'error': 'Failed to send email'}), 500

    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/order-confirmation', methods=['POST'])
def send_order_confirmation():
    """Send order confirmation email (internal service call)"""
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('order_id'):
            return jsonify({'error': 'Email and order_id are required'}), 400

        # Create email content
        subject = f"Order Confirmation - #{data['order_id']}"
        body = f"""
        Dear Customer,

        Thank you for your order!

        Order ID: {data['order_id']}
        Total: ${data.get('total', 0):.2f}

        We will send you another email when your order ships.

        Best regards,
        GlowShop Team
        """

        result = send_email(
            to=data['email'],
            subject=subject,
            body=body
        )

        if result:
            return jsonify({'message': 'Order confirmation sent'}), 200
        else:
            return jsonify({'error': 'Failed to send confirmation'}), 500

    except Exception as e:
        logger.error(f"Error sending order confirmation: {str(e)}")
        return jsonify({'error': str(e)}), 500

@notifications_bp.route('/payment-receipt', methods=['POST'])
def send_payment_receipt():
    """Send payment receipt email (internal service call)"""
    try:
        data = request.get_json()

        if not data or not data.get('email') or not data.get('transaction_id'):
            return jsonify({'error': 'Email and transaction_id are required'}), 400

        # Create email content
        subject = f"Payment Receipt - {data['transaction_id']}"
        body = f"""
        Dear Customer,

        Your payment has been processed successfully.

        Transaction ID: {data['transaction_id']}
        Amount: ${data.get('amount', 0):.2f}
        Payment Method: {data.get('payment_method', 'Card')}

        Thank you for your business!

        Best regards,
        GlowShop Team
        """

        result = send_email(
            to=data['email'],
            subject=subject,
            body=body
        )

        if result:
            return jsonify({'message': 'Payment receipt sent'}), 200
        else:
            return jsonify({'error': 'Failed to send receipt'}), 500

    except Exception as e:
        logger.error(f"Error sending payment receipt: {str(e)}")
        return jsonify({'error': str(e)}), 500
