#!/usr/bin/env python3
"""
Script to generate remaining service files for E-commerce MVP
Run this script to create all missing files for Order, Payment, and Dashboard services
"""

import os
from pathlib import Path

# Base path
BASE_PATH = Path(__file__).parent

# ============================================
# ORDER SERVICE FILES
# ============================================

ORDER_FILES = {
    "order-service/app/core/database.py": '''"""Database configuration"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

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
''',

    "order-service/app/models/order.py": '''"""Order models"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    order_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(50), default="pending")
    total_amount = Column(Float, nullable=False)
    shipping_address = Column(Text)
    payment_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(String(50), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    order = relationship("Order", back_populates="items")
''',

    "order-service/app/schemas/order.py": '''"""Order schemas"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class OrderItemCreate(BaseModel):
    product_id: str
    quantity: int

class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    shipping_address: str

class OrderItemResponse(BaseModel):
    id: int
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: int
    order_number: str
    status: str
    total_amount: float
    shipping_address: str
    items: List[OrderItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True
''',

    "order-service/app/api/orders.py": '''"""Order API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import httpx
import secrets
import sys
sys.path.append('/app')
from shared.auth import get_current_user, require_admin
from app.core.database import get_db
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderResponse
import os

router = APIRouter()

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://product-service:8000")

async def get_product(product_id: str):
    """Fetch product from product service"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new order"""
    total_amount = 0
    order_items = []

    # Validate products and calculate total
    for item in order_data.items:
        product = await get_product(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")

        if product.get("stock", 0) < item.quantity:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")

        item_total = product["price"] * item.quantity
        total_amount += item_total

        order_items.append({
            "product_id": item.product_id,
            "product_name": product["name"],
            "quantity": item.quantity,
            "unit_price": product["price"],
            "total_price": item_total
        })

    # Create order
    order = Order(
        user_id=current_user["user_id"],
        order_number=f"ORD-{secrets.token_hex(8).upper()}",
        status="pending",
        total_amount=total_amount,
        shipping_address=order_data.shipping_address
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # Create order items
    for item_data in order_items:
        item = OrderItem(order_id=order.id, **item_data)
        db.add(item)

    db.commit()
    db.refresh(order)

    return order

@router.get("/", response_model=List[OrderResponse])
async def list_orders(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user orders"""
    orders = db.query(Order).filter(Order.user_id == current_user["user_id"]).all()
    return orders

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get order details"""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.user_id != current_user["user_id"] and not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Not authorized")

    return order

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status
    db.commit()

    return {"message": "Order status updated", "order_id": order_id, "status": status}
''',
}

# ============================================
# PAYMENT SERVICE FILES
# ============================================

PAYMENT_FILES = {
    "payment-service/requirements.txt": '''fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
''',

    "payment-service/Dockerfile": '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',

    "payment-service/app/main.py": '''"""Payment Service - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import payments
from app.core.database import engine, Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Payment Service",
    description="Payment Processing Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments.router, prefix="/api/payments", tags=["payments"])

@app.get("/")
async def root():
    return {"service": "Payment Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-service"}
''',

    "payment-service/app/core/database.py": '''"""Database configuration"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

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
''',

    "payment-service/app/models/payment.py": '''"""Payment models"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, unique=True, nullable=False)
    payment_method = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(50), default="pending")
    transaction_id = Column(String(255), unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
''',

    "payment-service/app/schemas/payment.py": '''"""Payment schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    order_id: int
    payment_method: str
    card_number: str
    card_holder: str
    cvv: str
    expiry: str

class PaymentResponse(BaseModel):
    id: int
    order_id: int
    payment_method: str
    amount: float
    status: str
    transaction_id: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
''',

    "payment-service/app/api/payments.py": '''"""Payment API endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import secrets
import sys
sys.path.append('/app')
from shared.auth import get_current_user
from app.core.database import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()

def fake_payment_gateway(amount: float, card_number: str) -> dict:
    """Fake payment gateway - always succeeds for valid card"""
    if card_number.startswith("4"):  # Visa cards
        return {
            "success": True,
            "transaction_id": f"TXN-{secrets.token_hex(16).upper()}",
            "message": "Payment successful"
        }
    else:
        return {
            "success": False,
            "transaction_id": None,
            "message": "Payment failed - Invalid card"
        }

@router.post("/process", response_model=PaymentResponse)
async def process_payment(
    payment_data: PaymentCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Process payment"""
    # Check if payment already exists for this order
    existing = db.query(Payment).filter(Payment.order_id == payment_data.order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Payment already processed for this order")

    # Get order details (in real app, call order service)
    # For now, we'll create a dummy amount
    amount = 100.00  # This should come from order service

    # Process payment through fake gateway
    result = fake_payment_gateway(amount, payment_data.card_number)

    # Create payment record
    payment = Payment(
        order_id=payment_data.order_id,
        payment_method=payment_data.payment_method,
        amount=amount,
        status="completed" if result["success"] else "failed",
        transaction_id=result["transaction_id"]
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment status"""
    payment = db.query(Payment).filter(Payment.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment
''',
}

# ============================================
# DASHBOARD SERVICE FILES
# ============================================

DASHBOARD_FILES = {
    "dashboard-service/requirements.txt": '''fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
motor==3.3.2
pydantic==2.5.3
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
httpx==0.26.0
''',

    "dashboard-service/Dockerfile": '''FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
''',

    "dashboard-service/app/main.py": '''"""Dashboard Service - FastAPI Application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import dashboard
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Dashboard Service",
    description="Admin Dashboard Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])

@app.get("/")
async def root():
    return {"service": "Dashboard Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "dashboard-service"}
''',

    "dashboard-service/app/core/database.py": '''"""Database configuration"""
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
''',

    "dashboard-service/app/api/dashboard.py": '''"""Dashboard API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import sys
sys.path.append('/app')
from shared.auth import require_admin
from app.core.database import get_db, mongo_db

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics (admin only)"""
    # Get user count from PostgreSQL
    from sqlalchemy import text
    user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
    order_count = db.execute(text("SELECT COUNT(*) FROM orders")).scalar()
    total_revenue = db.execute(text("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status = 'completed'")).scalar()

    # Get product count from MongoDB
    product_count = await mongo_db.products.count_documents({"is_active": True})

    return {
        "total_users": user_count,
        "total_products": product_count,
        "total_orders": order_count,
        "total_revenue": float(total_revenue) if total_revenue else 0.0,
        "recent_stats": {
            "today_orders": 0,
            "today_revenue": 0.0
        }
    }

@router.get("/users")
async def list_dashboard_users(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    from sqlalchemy import text
    result = db.execute(text("SELECT id, email, username, full_name, is_admin, created_at FROM users ORDER BY created_at DESC LIMIT 50"))
    users = [dict(row._mapping) for row in result]
    return {"users": users}

@router.get("/orders")
async def list_dashboard_orders(
    current_user: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all orders (admin only)"""
    from sqlalchemy import text
    result = db.execute(text("SELECT id, order_number, user_id, status, total_amount, created_at FROM orders ORDER BY created_at DESC LIMIT 50"))
    orders = [dict(row._mapping) for row in result]
    return {"orders": orders}

@router.get("/products")
async def list_dashboard_products(current_user: dict = Depends(require_admin)):
    """List all products (admin only)"""
    cursor = mongo_db.products.find({"is_active": True}).limit(50)
    products = await cursor.to_list(length=50)

    # Convert ObjectId to string
    for product in products:
        product["_id"] = str(product["_id"])

    return {"products": products}
''',
}

# ============================================
# GENERATE FILES
# ============================================

def create_file(path: str, content: str):
    """Create file with given content"""
    file_path = BASE_PATH / path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, 'w') as f:
        f.write(content)

    print(f"✅ Created: {path}")

def main():
    print("🚀 Generating service files...\n")

    print("📦 Order Service:")
    for path, content in ORDER_FILES.items():
        create_file(path, content)

    print("\n💳 Payment Service:")
    for path, content in PAYMENT_FILES.items():
        create_file(path, content)

    print("\n📊 Dashboard Service:")
    for path, content in DASHBOARD_FILES.items():
        create_file(path, content)

    # Create __init__.py files
    init_dirs = [
        "order-service/app",
        "order-service/app/api",
        "order-service/app/core",
        "order-service/app/models",
        "order-service/app/schemas",
        "payment-service/app",
        "payment-service/app/api",
        "payment-service/app/core",
        "payment-service/app/models",
        "payment-service/app/schemas",
        "dashboard-service/app",
        "dashboard-service/app/api",
        "dashboard-service/app/core",
    ]

    for dir_path in init_dirs:
        create_file(f"{dir_path}/__init__.py", "")

    print("\n✨ All files generated successfully!")
    print("\n📋 Next steps:")
    print("1. Run: docker-compose up --build")
    print("2. Wait for services to start")
    print("3. Test APIs at http://localhost:800X/docs")
    print("\n🎉 Your e-commerce platform is ready!")

if __name__ == "__main__":
    main()
