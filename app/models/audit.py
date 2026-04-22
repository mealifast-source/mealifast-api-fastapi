from sqlalchemy import Column, String, Text, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import AuditAction


class AuditLog(Base, BaseModel):
    """Audit log model"""
    
    __tablename__ = "audit_logs"
    
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    action = Column(Enum(AuditAction), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(36), nullable=True)
    
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    description = Column(Text, nullable=True)
    
    # Relationships
    user = relationship(
        "User",
        back_populates="audit_logs",
    )
    
    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_action", "action"),
        Index("idx_entity_type", "entity_type"),
        Index("idx_entity_id", "entity_id"),
    )
