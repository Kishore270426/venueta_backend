from sqlalchemy import Column, Integer, String, ForeignKey, Date, DateTime, Boolean,Float,Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_config.database import Base

class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    admin_id = Column(Integer, ForeignKey("admin.id"))
    hall_id = Column(Integer, ForeignKey("event_hall_register.id"))
    function_start_date = Column(Date)
    function_end_date = Column(Date)
    status = Column(String, default="Pending")
    user_status = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    function_type = Column(String, nullable=False)
    minimum_people_coming = Column(Integer, default=0)
    maximum_people_coming = Column(Integer, default=0)
    no_of_rooms_booked = Column(Integer, default=0)
    additional_details = Column(String(40), nullable=True)
    
    user_name = Column(String, nullable=False)
    user_email = Column(String, nullable=False) 
    
    total_price = Column(Float, default=0.0)
    gst = Column(Float, default=18.0)
    
    # Time details
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)
    
    full_day_slot = Column(Boolean, default=False)
    
    invoice_sent = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    admin = relationship("Admin", back_populates="bookings")
    hall = relationship("EventHallRegister", back_populates="bookings")
    invoices = relationship("Invoice", back_populates="booking")

