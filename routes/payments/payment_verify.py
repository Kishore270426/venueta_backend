from datetime import date, timedelta
from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session
import razorpay
from pydantic import BaseModel
import os
from database_config.database import get_db
from models.subscription import Subscription, SubscriptionPlan
from sqlalchemy.sql import text
from services import auth
from models import Admin, FreeTrial

payment_verify_router = APIRouter()

# Razorpay Credentials
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_OWMIbAgJMlXJSy")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "I86r5qomPnLRpg4YpDo6CAGM")

# Initialize Razorpay Client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


class PaymentVerifyRequest(BaseModel):
    order_id: str
    payment_id: str
    signature: str
    admin_id: int
    plan: SubscriptionPlan


def verify_razorpay_payment(order_id: str, payment_id: str, signature: str):
    """Verify the payment signature with Razorpay"""
    params_dict = {
        "razorpay_order_id": order_id,
        "razorpay_payment_id": payment_id,
        "razorpay_signature": signature
    }
    try:
        client.utility.verify_payment_signature(params_dict)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False


def process_subscription(data: PaymentVerifyRequest, db: Session):
    """Handles subscription logic, including free trial validation and 12-month subscription processing."""
    today = db.execute(text("SELECT current_date")).scalar()

    # ✅ Step 1: Check if Admin Exists
    admin = db.query(Admin).filter(Admin.id == data.admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # ✅ Step 2: Check Active Free Trial (If any)
    existing_free_trial = db.query(FreeTrial).filter(FreeTrial.admin_id == admin.id).first()
    free_trial_expiry = None  # Default value

    if existing_free_trial:
        if existing_free_trial.expiry_date > today:
            free_trial_expiry = existing_free_trial.expiry_date  # Use free trial expiry as start date for subscription
        # If trial is expired, allow subscription normally

    # ✅ Step 3: Check Existing Subscription (Active 12-month subscription)
    existing_subscription = (
        db.query(Subscription)
        .filter(Subscription.admin_id == admin.id)
        .order_by(Subscription.expiry_date.desc())  # Get the latest subscription
        .first()
    )

    if existing_subscription and existing_subscription.expiry_date >= today:
        # Extend current active subscription by 12 months
        existing_subscription.expiry_date += timedelta(days=365)
        db.commit()
        db.refresh(existing_subscription)

        return {
            "status": "success",
            "message": "12-month subscription extended.",
            "subscription_id": existing_subscription.id,
            "new_expiry_date": existing_subscription.expiry_date
        }

    # ✅ Step 4: Create New 12-Month Subscription (Only If No Active One)
    if data.plan != SubscriptionPlan.ONE_YEAR:
        raise HTTPException(status_code=400, detail="Only 12-month subscription is allowed.")

    # If free trial was active, start new subscription from free trial expiry date, otherwise from today
    start_date = free_trial_expiry if free_trial_expiry else today
    new_expiry_date = start_date + timedelta(days=365)  # 12 months from start date

    new_subscription = Subscription(
        admin_id=admin.id,
        start_date=start_date,
        expiry_date=new_expiry_date,
        plan=data.plan,
        is_free_trial=False  # Mark this as a paid subscription
    )

    db.add(new_subscription)
    db.commit()
    db.refresh(new_subscription)

    return {
        "status": "success",
        "message": "12-month subscription activated.",
        "subscription_id": new_subscription.id,
        "new_expiry_date": new_expiry_date
    }


@payment_verify_router.post("/verify_payment")
async def verify_payment(data: PaymentVerifyRequest, db: Session = Depends(get_db), current_admin: str = Depends(auth.get_current_admin)) -> dict:
    """Main API endpoint: First verifies payment, then updates DB"""
    is_verified = verify_razorpay_payment(data.order_id, data.payment_id, data.signature)

    if not is_verified:
        raise HTTPException(status_code=400, detail="Invalid payment signature")

    return process_subscription(data, db)
