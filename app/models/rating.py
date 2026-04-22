from sqlalchemy import Column, String, Integer, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel


class MealRating(Base, BaseModel):
    """Meal rating model"""
    
    __tablename__ = "meal_ratings"
    
    meal_id = Column(String(36), ForeignKey("meals.id"), nullable=False)
    member_id = Column(String(36), ForeignKey("group_members.id"), nullable=False)
    
    rating = Column(Integer, nullable=False)  # 1-5
    review = Column(Text, nullable=True)
    
    # Relationships
    member = relationship(
        "GroupMember",
        back_populates="meal_ratings",
    )
    
    __table_args__ = (
        Index("idx_meal_id", "meal_id"),
        Index("idx_member_id", "member_id"),
    )
