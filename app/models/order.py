from sqlalchemy import Column, String, DateTime, Enum, JSON, Text, ForeignKey, Index, Boolean
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import OrderStatus, OrderWindowStatus


class OrderWindow(Base, BaseModel):
    """Order window model"""
    
    __tablename__ = "order_windows"
    
    group_id = Column(String(36), ForeignKey("mealifast_groups.id"), nullable=False)
    week_start_date = Column(DateTime, nullable=False)
    
    open_date_time = Column(DateTime, nullable=False)
    close_date_time = Column(DateTime, nullable=False)
    
    status = Column(Enum(OrderWindowStatus), default=OrderWindowStatus.SCHEDULED, nullable=False)
    
    # Relationships
    group = relationship(
        "MealiFastGroup",
        back_populates="order_windows",
    )
    
    __table_args__ = (
        Index("idx_group_id", "group_id"),
        Index("idx_status", "status"),
        Index("idx_week_start_date", "week_start_date"),
    )


class MemberOrder(Base, BaseModel):
    """Member order model"""
    
    __tablename__ = "member_orders"
    
    member_id = Column(String(36), ForeignKey("group_members.id"), nullable=False)
    group_id = Column(String(36), ForeignKey("mealifast_groups.id"), nullable=False)
    menu_id = Column(String(36), ForeignKey("menus.id"), nullable=True)
    
    week_start_date = Column(DateTime, nullable=False)
    
    status = Column(Enum(OrderStatus), default=OrderStatus.DRAFT, nullable=False)
    
    # JSON structure: {"Monday": {"breakfast": 1, "lunch": 1}, "Tuesday": {...}, ...}
    daily_meals = Column(JSON, default={}, nullable=True)
    special_notes = Column(Text, nullable=True)
    
    submit_date = Column(DateTime, nullable=True)
    
    # Relationships
    member = relationship(
        "GroupMember",
        back_populates="member_orders",
    )
    group = relationship(
        "MealiFastGroup",
        back_populates="member_orders",
    )
    menu = relationship(
        "Menu",
        back_populates="member_orders",
    )
    
    __table_args__ = (
        Index("idx_member_id", "member_id"),
        Index("idx_group_id", "group_id"),
        Index("idx_status", "status"),
        Index("idx_week_start_date", "week_start_date"),
    )
