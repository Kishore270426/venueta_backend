from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InvoiceCreate(BaseModel):
    booking_id: int
    hall_id: int
    user_id: int
    maintenance_charge: float = 0.0
    cleaning_charge: float = 0.0
    hall_total_price: float = 0.0
    useremail:str

class InvoiceResponse(BaseModel):
    id: int
    booking_id: int
    hall_id: int
    user_id: int
    maintenance_charge: float
    cleaning_charge: float
    hall_total_price: float
    invoice_print_date: datetime

    class Config:
        orm_mode = True
