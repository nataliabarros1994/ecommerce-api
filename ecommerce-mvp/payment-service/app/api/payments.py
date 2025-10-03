"""Payment API endpoints"""
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
