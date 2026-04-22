from sqlalchemy import Column, String, DateTime, Enum, JSON, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import DeliveryStatus


class DeliveryTracking(Base, BaseModel):
    """Delivery tracking model"""
    
    __tablename__ = "delivery_tracking"
    
    group_id = Column(String(36), ForeignKey("mealifast_groups.id"), nullable=False)
    
    delivery_date = Column(DateTime, nullable=False)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False)
    
    # JSON: meal count per category
    meal_summary = Column(JSON, default={}, nullable=True)
    # JSON: tracking of missed meals
    missed_meals = Column(JSON, default={}, nullable=True)
    
    notes = Column(Text, nullable=True)
    
    # Relationships
    group = relationship(
        "MealiFastGroup",
        back_populates="delivery_tracking",
    )
    
    __table_args__ = (
        Index("idx_group_id", "group_id"),
        Index("idx_status", "status"),
        Index("idx_delivery_date", "delivery_date"),
    )
