from sqlalchemy import Column, String, Float, Text, Boolean, Enum, JSON, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import MealsIncluded, BillingCycle


class SubscriptionPlan(Base, BaseModel):
    """Subscription plan model"""
    
    __tablename__ = "subscription_plans"
    
    plan_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    price_per_meal = Column(Float, nullable=False)
    meals_included = Column(Enum(MealsIncluded), nullable=False)
    billing_cycle = Column(Enum(BillingCycle), nullable=False)
    
    min_members = Column(String(36), nullable=True)
    
    active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    groups = relationship(
        "MealiFastGroup",
        back_populates="subscription_plan",
    )
    
    __table_args__ = (
        Index("idx_active", "active"),
        Index("idx_meals_included", "meals_included"),
    )
