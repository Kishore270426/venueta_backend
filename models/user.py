from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_config.database import Base

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    # Allowing password_hash to be nullable to support Google authentication
    password_hash = Column(String, nullable=True)
    phone_number = Column(String, unique=True, index=True)
    address = Column(String)
    city_name = Column(String)
    # Added googleId column; nullable=True allows non-Google registrations
    googleId = Column(String, unique=True, index=True, nullable=True)
    country_name = Column(String)
    created_at = Column(DateTime, default=func.now())
    
    bookings = relationship("Booking", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")
