"""Database configuration"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import os

# PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ecommerce:ecommerce123@localhost:5432/ecommerce")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# MongoDB
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://ecommerce:ecommerce123@localhost:27017/")
MONGODB_DB = os.getenv("MONGODB_DB", "ecommerce_products")
mongo_client = AsyncIOMotorClient(MONGODB_URL)
mongo_db = mongo_client[MONGODB_DB]
