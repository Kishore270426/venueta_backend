from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  # ✅ Import text for raw SQL queries
from database_config.database import get_db
from models import Admin, FreeTrial  # ✅ Use PascalCase for models
from services import auth
from pydantic import BaseModel

free_trial_router = APIRouter()

class FreeTrialRequest(BaseModel):
    admin_id: int

@free_trial_router.post("/register_free_trial")
async def register_free_trial(
    request: FreeTrialRequest,  
    db: Session = Depends(get_db)
):
    # ✅ Step 1: Check if Admin Exists
    admin = db.query(Admin).filter(Admin.id == request.admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    # ✅ Step 2: Check if the Admin Already Used the Free Trial
    existing_trial = db.query(FreeTrial).filter(FreeTrial.admin_id == admin.id).first()
    if existing_trial:
        raise HTTPException(status_code=400, detail="Free trial already used")

    # ✅ Step 3: Grant One-Month Free Trial
    start_date = db.execute(text("SELECT current_date")).scalar()
    expiry_date = db.execute(text("SELECT (current_date + interval '1 month')::date")).scalar()

    new_trial = FreeTrial(  # ✅ Use the correct model name: FreeTrial
        admin_id=admin.id,
        start_date=start_date,
        expiry_date=expiry_date,
        status=False  # Trial is initially inactive
    )

    db.add(new_trial)
    db.commit()
    db.refresh(new_trial)

    return {
        "status": "success",
        "message": "One-month free trial registered!",
        "trial_id": new_trial.id,
        "start_date": start_date,
        "expiry_date": expiry_date
    }
