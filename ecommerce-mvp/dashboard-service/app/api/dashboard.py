"""Dashboard API endpoints"""
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
