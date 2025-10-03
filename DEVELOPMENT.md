# 💻 Guia de Desenvolvimento

## Boas Práticas de Código

### 1. Estrutura de um Microserviço

```
service-name/
├── Dockerfile
├── requirements.txt
├── run.py
├── config.py
├── app/
│   ├── __init__.py
│   ├── models.py      # Modelos de dados
│   ├── routes.py      # Endpoints da API
│   ├── utils.py       # Funções auxiliares
│   └── schemas.py     # Validação (marshmallow)
└── tests/
    ├── __init__.py
    ├── test_routes.py
    └── test_models.py
```

### 2. Padrões de Código Python

#### Imports
```python
# Standard library
import os
from datetime import datetime

# Third-party
from flask import Flask, request, jsonify
from sqlalchemy import Column, Integer, String

# Local
from app.models import User
from app.utils import create_token
```

#### Docstrings
```python
def create_user(email, password):
    """
    Create a new user in the database.

    Args:
        email (str): User email address
        password (str): Plain text password

    Returns:
        User: The created user object

    Raises:
        ValueError: If email already exists
    """
    pass
```

#### Type Hints
```python
from typing import Dict, List, Optional

def get_user(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    pass
```

### 3. Tratamento de Erros

```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Em rotas
try:
    # código
except ValueError as e:
    return jsonify({'error': str(e)}), 400
except Exception as e:
    return jsonify({'error': 'Internal server error'}), 500
```

### 4. Validação de Input

```python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(
        required=True,
        validate=validate.Length(min=6, max=100)
    )

# Uso
schema = UserSchema()
try:
    data = schema.load(request.get_json())
except ValidationError as err:
    return jsonify({'errors': err.messages}), 400
```

## Desenvolvimento de Novos Microserviços

### Passo a Passo: Criar Product Service

#### 1. Criar estrutura de diretórios

```bash
mkdir -p services/product-service/app
cd services/product-service
```

#### 2. Criar Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "run.py"]
```

#### 3. Criar requirements.txt

```txt
Flask==3.0.0
Flask-CORS==4.0.0
pymongo==4.6.0
python-dotenv==1.0.0
marshmallow==3.20.1
gunicorn==21.2.0
```

#### 4. Criar config.py

```python
import os

class Config:
    MONGO_USER = os.getenv('MONGO_USER')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'ecommerce_products')

    MONGO_URI = (
        f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@'
        f'{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin'
    )
```

#### 5. Criar app/__init__.py

```python
from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import Config

mongo_client = None

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Initialize MongoDB
    global mongo_client
    mongo_client = MongoClient(Config.MONGO_URI)

    # Register blueprints
    from app.routes import products_bp
    app.register_blueprint(products_bp, url_prefix='/api/products')

    @app.route('/health')
    def health():
        return {'status': 'healthy', 'service': 'product-service'}

    return app
```

#### 6. Criar app/models.py (MongoDB)

```python
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
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        result = db.products.insert_one(product)
        product['_id'] = result.inserted_id
        return Product.to_dict(product)
```

#### 7. Criar app/routes.py

```python
from flask import Blueprint, request, jsonify
from bson import ObjectId
from app import mongo_client
from config import Config

products_bp = Blueprint('products', __name__)
db = None

@products_bp.before_request
def get_db():
    global db
    db = mongo_client[Config.MONGO_DB]

@products_bp.route('', methods=['GET'])
def get_products():
    """List all products with pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        skip = (page - 1) * per_page

        products = list(db.products.find({'is_active': True})
                       .skip(skip)
                       .limit(per_page))

        total = db.products.count_documents({'is_active': True})

        return jsonify({
            'products': [Product.to_dict(p) for p in products],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/<product_id>', methods=['GET'])
def get_product(product_id):
    """Get product by ID"""
    try:
        product = db.products.find_one({'_id': ObjectId(product_id)})

        if not product:
            return jsonify({'error': 'Product not found'}), 404

        return jsonify(Product.to_dict(product)), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

#### 8. Criar run.py

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

#### 9. Adicionar ao docker-compose.yml

Já está configurado! ✅

#### 10. Testar

```bash
# Build e start
docker-compose up --build product-service

# Testar endpoint
curl http://localhost:5003/health
```

## Testes

### Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py          # Fixtures compartilhadas
├── test_models.py       # Testes de modelos
├── test_routes.py       # Testes de endpoints
└── test_utils.py        # Testes de utilitários
```

### Exemplo: conftest.py

```python
import pytest
from app import create_app
from app.models import db

@pytest.fixture
def app():
    """Create test app"""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    """Get auth headers"""
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'test123'
    })
    token = response.json['tokens']['access_token']
    return {'Authorization': f'Bearer {token}'}
```

### Exemplo: test_routes.py

```python
def test_register_user(client):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'email': 'newuser@example.com',
        'password': 'password123'
    })

    assert response.status_code == 201
    assert 'tokens' in response.json
    assert 'user' in response.json

def test_login_invalid_credentials(client):
    """Test login with invalid credentials"""
    response = client.post('/api/auth/login', json={
        'email': 'wrong@example.com',
        'password': 'wrongpassword'
    })

    assert response.status_code == 401
    assert 'error' in response.json
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com coverage
pytest --cov=app --cov-report=html

# Testes específicos
pytest tests/test_routes.py::test_register_user

# Verbose
pytest -v
```

## Git Workflow

### Branch Strategy

```
main          # Produção (protegida)
  └── develop # Desenvolvimento
       ├── feature/auth-service
       ├── feature/product-service
       └── fix/cors-issue
```

### Commits

Seguir padrão Conventional Commits:

```bash
feat: add product search endpoint
fix: correct JWT expiration time
docs: update API documentation
test: add tests for order service
refactor: improve error handling
chore: update dependencies
```

### Pull Requests

Template:
```markdown
## Descrição
Breve descrição das mudanças

## Tipo de mudança
- [ ] Nova feature
- [ ] Bug fix
- [ ] Breaking change
- [ ] Documentação

## Checklist
- [ ] Código testado
- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Sem warnings
```

## Performance

### Database Queries

```python
# ❌ N+1 Problem
users = User.query.all()
for user in users:
    print(user.orders)  # Query separada para cada usuário

# ✅ Eager Loading
users = User.query.options(joinedload(User.orders)).all()
```

### Caching (futuro)

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.cached(timeout=300)
def get_products():
    return Product.query.all()
```

## Monitoramento

### Logs

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Uso
logger.info(f'User {user_id} logged in')
logger.warning(f'Failed login attempt for {email}')
logger.error(f'Database error: {str(e)}')
```

### Métricas (futuro)

```python
from prometheus_flask_exporter import PrometheusMetrics

metrics = PrometheusMetrics(app)

# Métricas customizadas
@metrics.counter('orders_created', 'Number of orders created')
def create_order():
    pass
```

## Recursos

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PyMongo Tutorial](https://pymongo.readthedocs.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

---

**Happy Coding! 🎉**
