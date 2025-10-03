import os

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-secret-key')

    # MongoDB
    MONGO_USER = os.getenv('MONGO_USER', 'admin')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', 'password')
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', '27017')
    MONGO_DB = os.getenv('MONGO_DB', 'ecommerce_db')

    MONGO_URI = (
        f'mongodb://{MONGO_USER}:{MONGO_PASSWORD}@'
        f'{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin'
    )

    # JWT
    JWT_SECRET_KEY = SECRET_KEY

    # CORS
    CORS_HEADERS = 'Content-Type'

    # Payment gateway (Stripe simulation)
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', 'sk_test_mock')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
