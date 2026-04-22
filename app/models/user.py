from sqlalchemy import Column, String, Boolean, Text, Enum, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import UserRole


class User(Base, BaseModel):
    """User model"""
    
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.MEMBER, nullable=False)
    
    email_verified = Column(Boolean, default=False, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    groups_admin = relationship(
        "MealiFastGroup",
        back_populates="group_admin_user",
        foreign_keys="MealiFastGroup.group_admin_id",
    )
    group_memberships = relationship(
        "GroupMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs = relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    
    __table_args__ = (
        Index("idx_email", "email"),
        Index("idx_role", "role"),
        Index("idx_active", "active"),
    )
