"""MongoDB database configuration"""
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging

logger = logging.getLogger(__name__)

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://ecommerce:ecommerce123@localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "ecommerce_products")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[MONGODB_DB]


async def init_db():
    """Initialize database and create indexes"""
    try:
        # Create indexes
        await database.products.create_index("name")
        await database.products.create_index("category")
        await database.products.create_index("price")
        await database.products.create_index([("name", "text"), ("description", "text")])

        logger.info("Database initialized successfully")

        # Seed sample data if empty
        count = await database.products.count_documents({})
        if count == 0:
            await seed_products()

    except Exception as e:
        logger.error(f"Error initializing database: {e}")


async def seed_products():
    """Seed sample products"""
    sample_products = [
        {
            "name": "Laptop Dell XPS 15",
            "description": "High-performance laptop with Intel i7 processor and 16GB RAM",
            "price": 1299.99,
            "category": "Electronics",
            "stock": 15,
            "images": ["laptop-xps15.jpg"],
            "is_active": True
        },
        {
            "name": "iPhone 15 Pro",
            "description": "Latest iPhone with A17 Pro chip and titanium design",
            "price": 999.99,
            "category": "Electronics",
            "stock": 30,
            "images": ["iphone15pro.jpg"],
            "is_active": True
        },
        {
            "name": "Sony WH-1000XM5",
            "description": "Premium noise-cancelling wireless headphones",
            "price": 399.99,
            "category": "Audio",
            "stock": 25,
            "images": ["sony-wh1000xm5.jpg"],
            "is_active": True
        },
        {
            "name": "Samsung 55\" QLED TV",
            "description": "4K QLED Smart TV with HDR and Quantum Processor",
            "price": 899.99,
            "category": "Electronics",
            "stock": 10,
            "images": ["samsung-qled55.jpg"],
            "is_active": True
        },
        {
            "name": "Apple MacBook Air M2",
            "description": "Ultra-portable laptop with M2 chip and 13.6-inch display",
            "price": 1199.99,
            "category": "Electronics",
            "stock": 20,
            "images": ["macbook-air-m2.jpg"],
            "is_active": True
        }
    ]

    await database.products.insert_many(sample_products)
    logger.info(f"Seeded {len(sample_products)} sample products")


def get_database():
    return database
