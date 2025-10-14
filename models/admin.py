from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database_config.database import Base

# Define FreeTrial class first
class FreeTrial(Base):
    __tablename__ = "free_trials"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin.id", ondelete="CASCADE"), unique=True, nullable=False)
    start_date = Column(Date, nullable=False)
    expiry_date = Column(Date, nullable=False)
    status = Column(Boolean, default=False)  

    admin = relationship("Admin", back_populates="free_trial")

# Define Admin class second
class Admin(Base):
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=True)
    googleId = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    address = Column(String, nullable=False)
    state = Column(String, nullable=False)
    country = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    event_halls = relationship("EventHallRegister", back_populates="admin")
    bookings = relationship("Booking", back_populates="admin")
    subscriptions = relationship("Subscription", back_populates="admin")
    
    free_trial = relationship("FreeTrial", back_populates="admin", uselist=False)  # Ensure consistency
