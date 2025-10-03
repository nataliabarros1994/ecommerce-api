from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import mongo_client
from app.models import Product, Category
from app.utils import token_required, admin_required
from config import Config

products_bp = Blueprint('products', __name__)

def get_db():
    """Get database instance"""
    return mongo_client[Config.MONGO_DB]

@products_bp.route('', methods=['GET'])
def get_products():
    """
    List products with pagination and filters
    Query params:
        - page: Page number (default: 1)
        - per_page: Items per page (default: 20, max: 100)
        - category: Filter by category
        - search: Search in name and description
        - min_price: Minimum price
        - max_price: Maximum price
        - sort: Sort field (price, name, created_at)
        - order: Sort order (asc, desc)
    """
    try:
        db = get_db()

        # Pagination
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(
            int(request.args.get('per_page', Config.DEFAULT_PAGE_SIZE)),
            Config.MAX_PAGE_SIZE
        )
        skip = (page - 1) * per_page

        # Filters
        filters = {'is_active': True}

        if category := request.args.get('category'):
            filters['category'] = category

        if search := request.args.get('search'):
            filters['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'description': {'$regex': search, '$options': 'i'}}
            ]

        if min_price := request.args.get('min_price'):
            filters['price'] = {'$gte': float(min_price)}

        if max_price := request.args.get('max_price'):
            if 'price' in filters:
                filters['price']['$lte'] = float(max_price)
            else:
                filters['price'] = {'$lte': float(max_price)}

        # Sorting
        sort_field = request.args.get('sort', 'created_at')
        sort_order = -1 if request.args.get('order', 'desc') == 'desc' else 1

        # Query
        products = list(
            db.products.find(filters)
            .sort(sort_field, sort_order)
            .skip(skip)
            .limit(per_page)
        )

        total = db.products.count_documents(filters)

        return jsonify({
            'products': [Product.to_dict(p) for p in products],
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    try:
        db = get_db()
        product = db.products.find_one({'_id': ObjectId(product_id)})

        if not product or not product.get('is_active'):
            return jsonify({'error': 'Product not found'}), 404

        return jsonify(Product.to_dict(product)), 200

    except Exception as e:
        return jsonify({'error': 'Product not found'}), 404

@products_bp.route('', methods=['POST'])
@admin_required
def create_product(current_user):
    """Create new product (admin only)"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400

        db = get_db()
        product = Product.create(db, data)

        return jsonify({
            'message': 'Product created successfully',
            'product': product
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/<product_id>', methods=['PUT'])
@admin_required
def update_product(current_user, product_id):
    """Update product (admin only)"""
    try:
        data = request.get_json()

        db = get_db()

        # Check if product exists
        if not db.products.find_one({'_id': ObjectId(product_id)}):
            return jsonify({'error': 'Product not found'}), 404

        if Product.update(db, product_id, data):
            updated_product = db.products.find_one({'_id': ObjectId(product_id)})
            return jsonify({
                'message': 'Product updated successfully',
                'product': Product.to_dict(updated_product)
            }), 200
        else:
            return jsonify({'error': 'No changes made'}), 400

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/<product_id>', methods=['DELETE'])
@admin_required
def delete_product(current_user, product_id):
    """Delete product (soft delete, admin only)"""
    try:
        db = get_db()

        if Product.delete(db, product_id):
            return jsonify({'message': 'Product deleted successfully'}), 200
        else:
            return jsonify({'error': 'Product not found'}), 404

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """List all categories"""
    try:
        db = get_db()
        categories = list(db.categories.find({'is_active': True}))

        return jsonify({
            'categories': [Category.to_dict(c) for c in categories]
        }), 200

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/categories', methods=['POST'])
@admin_required
def create_category(current_user):
    """Create new category (admin only)"""
    try:
        data = request.get_json()

        if 'name' not in data:
            return jsonify({'error': 'name is required'}), 400

        db = get_db()
        category = Category.create(db, data)

        return jsonify({
            'message': 'Category created successfully',
            'category': category
        }), 201

    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@products_bp.route('/seed', methods=['POST'])
def seed_products():
    """Seed database with sample products (development only)"""
    try:
        db = get_db()

        # Check if already seeded
        if db.products.count_documents({}) > 0:
            return jsonify({'message': 'Database already seeded'}), 200

        # Sample products
        sample_products = [
            {
                'name': 'Notebook Dell Inspiron',
                'description': 'Notebook com processador Intel Core i7, 16GB RAM, SSD 512GB',
                'price': 4599.90,
                'stock': 15,
                'category': 'electronics',
                'images': ['notebook-dell-1.jpg'],
                'attributes': {'brand': 'Dell', 'color': 'Silver', 'processor': 'Intel Core i7'}
            },
            {
                'name': 'Mouse Gamer Logitech',
                'description': 'Mouse gamer com sensor óptico de alta precisão',
                'price': 299.90,
                'stock': 50,
                'category': 'electronics',
                'images': ['mouse-logitech-1.jpg'],
                'attributes': {'brand': 'Logitech', 'color': 'Black', 'dpi': '16000'}
            },
            {
                'name': 'Teclado Mecânico RGB',
                'description': 'Teclado mecânico com switches blue e iluminação RGB',
                'price': 499.90,
                'stock': 30,
                'category': 'electronics',
                'images': ['keyboard-rgb-1.jpg'],
                'attributes': {'brand': 'Redragon', 'color': 'Black', 'switch': 'Blue'}
            },
            {
                'name': 'Headset Gamer HyperX',
                'description': 'Headset com som surround 7.1 virtual',
                'price': 399.90,
                'stock': 25,
                'category': 'electronics',
                'images': ['headset-hyperx-1.jpg'],
                'attributes': {'brand': 'HyperX', 'color': 'Black/Red', 'connection': 'USB'}
            },
            {
                'name': 'Webcam Logitech C920',
                'description': 'Webcam Full HD 1080p com microfone integrado',
                'price': 599.90,
                'stock': 20,
                'category': 'electronics',
                'images': ['webcam-logitech-1.jpg'],
                'attributes': {'brand': 'Logitech', 'resolution': '1080p', 'fps': '30'}
            }
        ]

        for product_data in sample_products:
            Product.create(db, product_data)

        # Sample categories
        sample_categories = [
            {'name': 'Electronics', 'slug': 'electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Computers', 'slug': 'computers', 'description': 'Computers and accessories'},
            {'name': 'Gaming', 'slug': 'gaming', 'description': 'Gaming peripherals'},
        ]

        for category_data in sample_categories:
            Category.create(db, category_data)

        return jsonify({
            'message': 'Database seeded successfully',
            'products_count': len(sample_products),
            'categories_count': len(sample_categories)
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500
