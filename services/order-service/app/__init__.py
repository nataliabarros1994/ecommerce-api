from flask import Flask
from flask_cors import CORS
from config import config
import os

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    from app.models import db
    db.init_app(app)

    CORS(app)

    # Register blueprints
    from app.routes import orders_bp
    app.register_blueprint(orders_bp, url_prefix='/api/orders')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'order-service'}, 200

    return app
