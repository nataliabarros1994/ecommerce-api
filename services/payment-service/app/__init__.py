from flask import Flask
from flask_cors import CORS
from pymongo import MongoClient
from config import Config

mongo_client = None

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)

    # Initialize MongoDB
    global mongo_client
    try:
        mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=5000)
        # Test connection
        mongo_client.admin.command('ping')
        print("✅ Connected to MongoDB successfully")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {str(e)}")

    # Register blueprints
    from app.routes import payments_bp
    app.register_blueprint(payments_bp, url_prefix='/api/payments')

    # Health check
    @app.route('/health')
    def health_check():
        try:
            mongo_client.admin.command('ping')
            db_status = 'connected'
        except:
            db_status = 'disconnected'

        return {
            'status': 'healthy',
            'service': 'payment-service',
            'database': db_status
        }, 200

    return app
