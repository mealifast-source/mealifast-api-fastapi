from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Index, JSON
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import GroupStatus, MemberStatus, MemberRole, DietaryTag


class MealiFastGroup(Base, BaseModel):
    """Group/Organization model"""
    
    __tablename__ = "mealifast_groups"
    
    group_name = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=False)
    group_admin_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subscription_plan_id = Column(String(36), ForeignKey("subscription_plans.id"), nullable=True)
    
    plan_start_date = Column(DateTime, nullable=True)
    plan_end_date = Column(DateTime, nullable=True)
    
    status = Column(Enum(GroupStatus), default=GroupStatus.PENDING, nullable=False)
    
    # Relationships
    group_admin_user = relationship(
        "User",
        back_populates="groups_admin",
        foreign_keys=[group_admin_id],
    )
    subscription_plan = relationship(
        "SubscriptionPlan",
        back_populates="groups",
    )
    members = relationship(
        "GroupMember",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    member_orders = relationship(
        "MemberOrder",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    order_windows = relationship(
        "OrderWindow",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    invoices = relationship(
        "Invoice",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    delivery_tracking = relationship(
        "DeliveryTracking",
        back_populates="group",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_group_admin_id", "group_admin_id"),
        Index("idx_status", "status"),
        Index("idx_plan_end_date", "plan_end_date"),
    )


class GroupMember(Base, BaseModel):
    """Group member model"""
    
    __tablename__ = "group_members"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    group_id = Column(String(36), ForeignKey("mealifast_groups.id"), nullable=False)
    
    status = Column(Enum(MemberStatus), default=MemberStatus.INVITED, nullable=False)
    member_role = Column(Enum(MemberRole), default=MemberRole.MEMBER, nullable=False)
    
    dietary_preferences = Column(JSON, default=[], nullable=True)  # List of DietaryTags
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship(
        "User",
        back_populates="group_memberships",
    )
    group = relationship(
        "MealiFastGroup",
        back_populates="members",
    )
    member_orders = relationship(
        "MemberOrder",
        back_populates="member",
        cascade="all, delete-orphan",
    )
    meal_ratings = relationship(
        "MealRating",
        back_populates="member",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_group_id", "group_id"),
        Index("idx_status", "status"),
        Index("idx_member_role", "member_role"),
    )
