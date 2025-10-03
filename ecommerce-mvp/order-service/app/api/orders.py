"""Order API endpoints"""
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
