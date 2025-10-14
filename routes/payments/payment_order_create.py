from fastapi import HTTPException, APIRouter
import razorpay
from pydantic import BaseModel
import os
import asyncio

payment_create_router = APIRouter()

# Razorpay Credentials
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_OWMIbAgJMlXJSy")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "I86r5qomPnLRpg4YpDo6CAGM")

# Initialize Razorpay Client
client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class CreateOrderRequest(BaseModel):
    amount: int 

@payment_create_router.post("/create_order/")
async def create_order(request_data: CreateOrderRequest) -> dict:
    try:
        order_data = {
            "amount": request_data.amount * 100,  
            "currency": "INR",
            "payment_capture": 1  # Auto-capture payment
        }
        # Run blocking I/O operation in a separate thread
        order = await asyncio.to_thread(client.order.create, order_data)
        return {"order_id": order["id"], "amount": order["amount"], "currency": order["currency"]}
    except razorpay.errors.BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except razorpay.errors.ServerError as e:
        raise HTTPException(status_code=500, detail="Razorpay server error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
