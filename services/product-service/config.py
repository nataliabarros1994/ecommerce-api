import os

class Config:
    """Configuration for Product Service"""

    # MongoDB Configuration
    MONGO_USER = os.getenv('MONGO_USER', 'mongo_user')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'mongo_pass')
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'ecommerce_products')

    MONGO_URI = (
        f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@'
        f'{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin'
    )

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
