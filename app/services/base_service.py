from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import TypeVar, Generic, List, Optional, Type
import logging

logger = logging.getLogger(__name__)

T = TypeVar("T")


class BaseService(Generic[T]):
    """Base service class with common CRUD operations"""
    
    def __init__(self, model: Type[T]):
        self.model = model
    
    def create(self, db: Session, **kwargs) -> T:
        """Create new record"""
        try:
            instance = self.model(**kwargs)
            db.add(instance)
            db.commit()
            db.refresh(instance)
            logger.info(f"Created {self.model.__name__}: {instance.id}")
            return instance
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise
    
    def get_by_id(self, db: Session, id: str) -> Optional[T]:
        """Get record by ID"""
        try:
            return db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"Failed to get {self.model.__name__} by ID: {e}")
            raise
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 20) -> tuple[List[T], int]:
        """Get all records with pagination"""
        try:
            total = db.query(func.count(self.model.id)).scalar()
            records = db.query(self.model).offset(skip).limit(limit).all()
            return records, total
        except Exception as e:
            logger.error(f"Failed to get all {self.model.__name__}: {e}")
            raise
    
    def update(self, db: Session, id: str, **kwargs) -> Optional[T]:
        """Update record"""
        try:
            instance = self.get_by_id(db, id)
            if not instance:
                return None
            
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            db.commit()
            db.refresh(instance)
            logger.info(f"Updated {self.model.__name__}: {instance.id}")
            return instance
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update {self.model.__name__}: {e}")
            raise
    
    def delete(self, db: Session, id: str) -> bool:
        """Delete record"""
        try:
            instance = self.get_by_id(db, id)
            if not instance:
                return False
            
            db.delete(instance)
            db.commit()
            logger.info(f"Deleted {self.model.__name__}: {id}")
            return True
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to delete {self.model.__name__}: {e}")
            raise
    
    def count(self, db: Session) -> int:
        """Count total records"""
        try:
            return db.query(func.count(self.model.id)).scalar()
        except Exception as e:
            logger.error(f"Failed to count {self.model.__name__}: {e}")
            raise
