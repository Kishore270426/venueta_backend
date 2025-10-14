from pydantic import BaseModel
from datetime import date, time ,datetime
from typing import Literal

class HallResponse(BaseModel):
    id: int

    hall_name: str

    hall_location: str

    hall_address: str

    hall_price_per_day: float

    maintenance_charge_per_day: float

    cleaning_charge_per_day: float

    catering_work_members: int

    total_hall_capacity: int

    number_of_rooms: int

    about_hall: str

    image_path: str  

    class Config:

        orm_mode = True 
        
class HallBookingRequest(BaseModel):
    
    hall_id: int
    
    admin_id: int
    
    user_id: int
    
    function_start_date: date
    
    function_end_date: date
    
    function_type: str
    
    minimum_people_coming: int
    
    maximum_people_coming: int
    
    no_of_rooms_booked: int
    
    additional_details: str = None
    
    user_name: str
    
    user_email: str
    
    total_price: float
    
    gst: float = 18.0  
    
    start_time: time
    
    end_time: time
    
    full_day_slot: bool




class BookingResponse(BaseModel):
    id: int
    user_name: str
    user_email: str
    hall_id: int
    function_start_date: date
    function_end_date: date
    status: str
    total_price: float
    gst: float
    start_time: time 
    end_time: time  
    full_day_slot: bool
    additional_details: str | None

    class Config:
        orm_mode = True

class Bookingapprovedlist(BaseModel):
    id: int
    user_id:int
    admin_id:int
    user_name: str
    user_email: str
    hall_id: int
    function_type:str
    function_start_date: date
    function_end_date: date
    status: str
    total_price: float
    no_of_rooms_booked:int
    gst: float
    start_time: time 
    end_time: time  
    full_day_slot: bool
    additional_details: str | None

    class Config:
        orm_mode = True
class UpdateStatusRequest(BaseModel):
    id:int
    status: Literal["Pending", "Approved", "Rejected"] 