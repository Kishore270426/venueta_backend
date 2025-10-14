from sqlalchemy import Column, Integer, Date, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database_config.database import Base
import enum

# Subscription Plan Enum with only ONE_YEAR option
class SubscriptionPlan(str, enum.Enum):
    ONE_YEAR = "12_months"

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("admin.id"), nullable=False)
    start_date = Column(Date, nullable=False)  # The date when the subscription starts
    expiry_date = Column(Date, nullable=False)  # The date when the subscription ends
    plan = Column(Enum(SubscriptionPlan), nullable=False)  # Subscription plan type, only 12 months allowed
    is_free_trial = Column(Boolean, default=False)  # Indicates if this subscription is a free trial

    admin = relationship("Admin", back_populates="subscriptions")  # Relationship to Admin model
