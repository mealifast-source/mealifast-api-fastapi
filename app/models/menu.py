from sqlalchemy import Column, String, DateTime, Enum, JSON, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import MenuStatus


class Menu(Base, BaseModel):
    """Menu model"""
    
    __tablename__ = "menus"
    
    name = Column(String(255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    
    status = Column(Enum(MenuStatus), default=MenuStatus.DRAFT, nullable=False)
    
    # JSON structure: {"Monday": {"breakfast": ["meal_id"], "lunch": ["meal_id"]}, ...}
    menu_items = Column(JSON, default={}, nullable=True)
    
    # Relationships
    member_orders = relationship(
        "MemberOrder",
        back_populates="menu",
    )
    
    __table_args__ = (
        Index("idx_status", "status"),
        Index("idx_start_date", "start_date"),
        Index("idx_end_date", "end_date"),
    )
