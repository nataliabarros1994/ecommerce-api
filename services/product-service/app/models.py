from datetime import datetime
from bson import ObjectId

class Product:
    """Product model for MongoDB"""

    @staticmethod
    def to_dict(doc):
        """Convert MongoDB document to dict"""
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
            # Convert datetime to ISO format
            if 'created_at' in doc:
                doc['created_at'] = doc['created_at'].isoformat()
            if 'updated_at' in doc:
                doc['updated_at'] = doc['updated_at'].isoformat()
        return doc

    @staticmethod
    def create(db, data):
        """Create new product"""
        product = {
            'name': data['name'],
            'description': data.get('description', ''),
            'price': float(data['price']),
            'stock': int(data.get('stock', 0)),
            'category': data.get('category', 'general'),
            'images': data.get('images', []),
            'attributes': data.get('attributes', {}),  # Campos dinâmicos
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        # Validações
        if product['price'] < 0:
            raise ValueError('Price cannot be negative')
        if product['stock'] < 0:
            raise ValueError('Stock cannot be negative')

        result = db.products.insert_one(product)
        product['_id'] = result.inserted_id
        return Product.to_dict(product)

    @staticmethod
    def update(db, product_id, data):
        """Update product"""
        update_data = {
            'updated_at': datetime.utcnow()
        }

        # Only update provided fields
        if 'name' in data:
            update_data['name'] = data['name']
        if 'description' in data:
            update_data['description'] = data['description']
        if 'price' in data:
            price = float(data['price'])
            if price < 0:
                raise ValueError('Price cannot be negative')
            update_data['price'] = price
        if 'stock' in data:
            stock = int(data['stock'])
            if stock < 0:
                raise ValueError('Stock cannot be negative')
            update_data['stock'] = stock
        if 'category' in data:
            update_data['category'] = data['category']
        if 'images' in data:
            update_data['images'] = data['images']
        if 'attributes' in data:
            update_data['attributes'] = data['attributes']
        if 'is_active' in data:
            update_data['is_active'] = data['is_active']

        result = db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': update_data}
        )

        return result.modified_count > 0

    @staticmethod
    def delete(db, product_id):
        """Soft delete product"""
        result = db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0

class Category:
    """Category model for MongoDB"""

    @staticmethod
    def to_dict(doc):
        """Convert MongoDB document to dict"""
        if doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc

    @staticmethod
    def create(db, data):
        """Create new category"""
        category = {
            'name': data['name'],
            'slug': data.get('slug', data['name'].lower().replace(' ', '-')),
            'description': data.get('description', ''),
            'parent_id': data.get('parent_id'),
            'is_active': True,
            'created_at': datetime.utcnow()
        }

        result = db.categories.insert_one(category)
        category['_id'] = result.inserted_id
        return Category.to_dict(category)
