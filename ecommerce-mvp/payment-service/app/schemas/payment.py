"""Payment schemas"""
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
