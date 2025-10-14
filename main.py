# Standard Library Imports
import sys
import os

# Third-Party Imports
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

# Local Imports
from routes import otp_router, user_routes, admin_routes, hall_register_router, hall_booking_router
from models import user, admin, event_hall_register, booking, invoice_table
from routes.payments import payment_order_create, payment_verify, free_trial
from database_config.database import engine, Base
from middleware import configure_middleware

# Ensure "uploaded_images" directory exists
if not os.path.exists("uploaded_images"):
    os.makedirs("uploaded_images")

# Initialize FastAPI App
app = FastAPI(docs_url="/docs", redoc_url="/redoc")

# Configure Middleware
configure_middleware(app)

# Mount Static Files
app.mount("/api/uploaded_images", StaticFiles(directory="uploaded_images"), name="uploaded_images")

# Create Database Tables
Base.metadata.create_all(bind=engine)  # ✅ Correct way to create tables

# Register Routes
# -----------------------------------------------------------------------------------
# Payment Routes
app.include_router(payment_order_create.payment_create_router, prefix="/api", tags=["Payment-create"])
app.include_router(payment_verify.payment_verify_router, prefix="/api", tags=["Payment_verify"])  # ✅ Consistent prefix
app.include_router(free_trial.free_trial_router, prefix="/trial", tags=["register_free_trial"])

# OTP Routes
app.include_router(otp_router.router, prefix="/api", tags=["OTP"])

# User Routes
app.include_router(user_routes.user_router, prefix="/user", tags=["User"])

# Admin Routes
app.include_router(admin_routes.admin_router, prefix="/admin", tags=["Admin"])

# Hall Register Routes
app.include_router(hall_register_router.hall_register_router, prefix="/hall", tags=["Hall"])

# Hall Booking Routes
app.include_router(hall_booking_router.hall_booking_user_router, prefix="/hall/user", tags=["Hall"])

# # Start Uvicorn Server
# if __name__ == "__main__":
#     port = int(os.getenv("PORT", 8000))
#     print(f"Starting FastAPI server on port {port}...")
#     uvicorn.run(app, host="0.0.0.0", port=port, reload=True)