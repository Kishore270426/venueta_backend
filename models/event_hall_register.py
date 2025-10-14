from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database_config.database import Base

class EventHallRegister(Base):
    
    __tablename__ = 'event_hall_register'

    id = Column(Integer, primary_key=True, index=True)
    
    hall_name = Column(String, nullable=False)
    
    hall_location = Column(String, nullable=False)
    
    hall_address = Column(String, nullable=False)
    
    hall_price_per_day = Column(Float, nullable=False)
    
    maintenance_charge_per_day = Column(Float, nullable=False)
    
    cleaning_charge_per_day = Column(Float, nullable=False)
    
    catering_work_members = Column(Integer, nullable=False)
    
    total_hall_capacity = Column(Integer, nullable=False)
    
    number_of_rooms = Column(Integer, nullable=False)
    
    about_hall = Column(String, nullable=True)
    
    image_url = Column(String, nullable=True)

    admin_id = Column(Integer, ForeignKey('admin.id'), nullable=False)
    
    admin = relationship("Admin", back_populates="event_halls")
    
    bookings = relationship("Booking", back_populates="hall")
    invoices = relationship("Invoice", back_populates="hall")
