from sqlalchemy import Column, String, Text, Float, Boolean, Enum, JSON, Index

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import MealCategory, DietaryTag


class Meal(Base, BaseModel):
    """Meal model"""
    
    __tablename__ = "meals"
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    photo_url = Column(String(500), nullable=True)
    
    category = Column(Enum(MealCategory), nullable=False)
    cost_price = Column(Float, nullable=False)
    
    dietary_tags = Column(JSON, default=[], nullable=True)  # List of DietaryTags
    
    active = Column(Boolean, default=True, nullable=False)
    
    __table_args__ = (
        Index("idx_category", "category"),
        Index("idx_active", "active"),
    )
