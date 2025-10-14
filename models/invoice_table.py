from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime,String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database_config.database import Base

class Invoice(Base):
    
    __tablename__ = "invoice_table"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    hall_id = Column(Integer, ForeignKey("event_hall_register.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    maintenance_charge = Column(Float, nullable=False, default=0.0)
    cleaning_charge = Column(Float, nullable=False, default=0.0)
    hall_total_price = Column(Float, nullable=False, default=0.0)
    invoice_print_date = Column(DateTime, server_default=func.now())


    # Relationships
    booking = relationship("Booking", back_populates="invoices")
    hall = relationship("EventHallRegister", back_populates="invoices")
    user = relationship("User", back_populates="invoices")
