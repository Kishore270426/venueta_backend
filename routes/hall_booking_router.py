from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import BaseModel
from models import Booking, User, Admin, EventHallRegister
from database_config.database import get_db
from services.auth import get_current_userID
from datetime import date, time
from schemas.hall_schemas import HallBookingRequest

hall_booking_user_router = APIRouter()

@hall_booking_user_router.post("/book_hall", response_model=None)
def book_hall(
    
    booking_request: HallBookingRequest,
    
    db: Session = Depends(get_db),
    
    current_user: User = Depends(get_current_userID)
):
   
    try:
  
        hall_id = booking_request.hall_id
        
        admin_id = booking_request.admin_id
        
        user_id = booking_request.user_id
        
        function_start_date = booking_request.function_start_date
        
        function_end_date = booking_request.function_end_date
        
        function_type = booking_request.function_type
        
        minimum_people_coming = booking_request.minimum_people_coming
        
        maximum_people_coming = booking_request.maximum_people_coming
        
        no_of_rooms_booked = booking_request.no_of_rooms_booked
        
        additional_details = booking_request.additional_details
        
        user_name = booking_request.user_name
        
        user_email = booking_request.user_email
        
        total_price = booking_request.total_price
        
        gst = booking_request.gst
        
        start_time = booking_request.start_time
        
        end_time = booking_request.end_time
        
        full_day_slot = booking_request.full_day_slot

  
        if current_user.id != user_id:
            
            print("c-user: ", current_user.id, "give user id: ", user_id)
            
            raise HTTPException(status_code=403, detail="You are not authorized to book on behalf of another user")


        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            
            raise HTTPException(status_code=404, detail="User not found")

      
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        
        if not admin:
            
            raise HTTPException(status_code=404, detail="Admin not found")

      
        hall = db.query(EventHallRegister).filter(EventHallRegister.id == hall_id).first()
        
        if not hall:
            
            raise HTTPException(status_code=404, detail="Event hall not found")

      
        existing_booking = db.query(Booking).filter(
            
            Booking.hall_id == hall_id,
            
            Booking.function_start_date <= function_end_date,
            
            Booking.function_end_date >= function_start_date,
            
            Booking.status == "Pending"
            
        ).first()
        print(existing_booking)

        if existing_booking:
            
            raise HTTPException(status_code=400, detail="Hall is booked for the selected dates. Please choose different dates.")

     
        new_booking = Booking(
            
            hall_id=hall_id,
            
            user_id=user_id,
            
            admin_id=admin_id,
            
            function_start_date=function_start_date,
            
            function_end_date=function_end_date,
            
            function_type=function_type,
            
            minimum_people_coming=minimum_people_coming,
            
            maximum_people_coming=maximum_people_coming,
            
            no_of_rooms_booked=no_of_rooms_booked,
            
            additional_details=additional_details,
            
            user_name=user_name,
            
            user_email=user_email,
            
            total_price=total_price,
            
            gst=gst,  
            
            start_time=start_time,
            
            end_time=end_time,
            
            full_day_slot=full_day_slot,
            
            status="Pending"
        )

        db.add(new_booking)
        
        db.commit()
        
        db.refresh(new_booking)

        return {"message": "Hall booked successfully", "booking_id": new_booking.id}

    except SQLAlchemyError:
        
        db.rollback()  
        
        raise HTTPException(status_code=500, detail="A database error occurred")
    
    except Exception as e:
        
        raise HTTPException(status_code=400, detail=str(e))


@hall_booking_user_router.get("/booking_status", response_model=list)
def get_booking_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_userID)
):
    try:
        bookings = (
            db.query(Booking, EventHallRegister.hall_name)
            .join(EventHallRegister, Booking.hall_id == EventHallRegister.id)
            .filter(Booking.user_id == current_user.id)
            .all()
        )
        
        if not bookings:
            raise HTTPException(status_code=404, detail="No bookings found for this user")
        
        booking_status_list = [
            {
                "booking_id": booking.id,
                "hall_id": booking.hall_id,
                "hall_name": hall_name,  # Include the hall name here
                "admin_id": booking.admin_id,
                "function_start_date": booking.function_start_date,
                "function_end_date": booking.function_end_date,
                "function_type": booking.function_type,
                "minimum_people_coming": booking.minimum_people_coming,
                "maximum_people_coming": booking.maximum_people_coming,
                "no_of_rooms_booked": booking.no_of_rooms_booked,
                "additional_details": booking.additional_details,
                "user_name": booking.user_name,
                "user_email": booking.user_email,
                "total_price": booking.total_price,
                "gst": booking.gst,
                "start_time": booking.start_time,
                "end_time": booking.end_time,
                "full_day_slot": booking.full_day_slot,
                "status": booking.status
            }
            for booking, hall_name in bookings
        ]
        
        return booking_status_list
    
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="A database error occurred")
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
