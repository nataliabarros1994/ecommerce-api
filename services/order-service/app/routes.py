from flask import Blueprint, request, jsonify
from app.models import db, Order, OrderItem, OrderStatus
from app.utils import token_required
from decimal import Decimal

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['GET'])
@token_required
def get_orders(current_user):
    """Get all orders for the current user"""
    try:
        orders = Order.query.filter_by(user_id=current_user['user_id']).order_by(Order.created_at.desc()).all()
        return jsonify([order.to_dict() for order in orders]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['GET'])
@token_required
def get_order(current_user, order_id):
    """Get a specific order"""
    try:
        order = Order.query.get(order_id)

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Check if user owns this order or is admin
        if order.user_id != current_user['user_id'] and not current_user.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify(order.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/', methods=['POST'])
@token_required
def create_order(current_user):
    """Create a new order"""
    try:
        data = request.get_json()

        # Validate input
        if not data or not data.get('items'):
            return jsonify({'error': 'Items are required'}), 400

        # Create order
        order = Order(
            user_id=current_user['user_id'],
            shipping_address=data.get('shipping_address', ''),
            total_amount=0
        )

        total_amount = Decimal('0.00')

        # Add order items
        for item_data in data['items']:
            if not all(k in item_data for k in ['product_id', 'quantity', 'price']):
                return jsonify({'error': 'Invalid item data'}), 400

            price = Decimal(str(item_data['price']))
            quantity = int(item_data['quantity'])
            subtotal = price * quantity

            order_item = OrderItem(
                product_id=item_data['product_id'],
                product_name=item_data.get('product_name', ''),
                quantity=quantity,
                price=price,
                subtotal=subtotal
            )
            order.items.append(order_item)
            total_amount += subtotal

        order.total_amount = total_amount

        db.session.add(order)
        db.session.commit()

        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>/status', methods=['PUT'])
@token_required
def update_order_status(current_user, order_id):
    """Update order status"""
    try:
        data = request.get_json()
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'Status is required'}), 400

        # Validate status
        valid_statuses = [s.value for s in OrderStatus]
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

        order = Order.query.get(order_id)

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Check permissions
        if order.user_id != current_user['user_id'] and not current_user.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403

        order.status = new_status
        db.session.commit()

        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/<int:order_id>', methods=['DELETE'])
@token_required
def cancel_order(current_user, order_id):
    """Cancel an order"""
    try:
        order = Order.query.get(order_id)

        if not order:
            return jsonify({'error': 'Order not found'}), 404

        # Check permissions
        if order.user_id != current_user['user_id'] and not current_user.get('is_admin'):
            return jsonify({'error': 'Unauthorized'}), 403

        # Only pending or confirmed orders can be cancelled
        if order.status not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
            return jsonify({'error': 'Order cannot be cancelled'}), 400

        order.status = OrderStatus.CANCELLED.value
        db.session.commit()

        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
