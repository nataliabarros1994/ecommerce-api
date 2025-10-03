"""Order schemas"""
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
