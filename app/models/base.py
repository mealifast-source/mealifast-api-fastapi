from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.orm import declarative_mixin
from uuid import uuid4
from datetime import datetime
import uuid

from app.database import Base


@declarative_mixin
class BaseModel:
    """Base model with common fields"""
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
        }
