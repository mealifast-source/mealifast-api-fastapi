from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.models import Meal, Menu
from app.core.constants import MealCategory, MenuStatus
from app.core.exceptions import NotFoundException, ConflictException
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class MealService(BaseService[Meal]):
    """Service for meal operations"""
    
    def __init__(self):
        super().__init__(Meal)
    
    def get_by_category(self, db: Session, category: MealCategory, skip: int = 0, limit: int = 20) -> tuple[List[Meal], int]:
        """Get meals by category"""
        try:
            total = db.query(Meal).filter(Meal.category == category, Meal.active == True).count()
            meals = db.query(Meal).filter(
                Meal.category == category,
                Meal.active == True
            ).offset(skip).limit(limit).all()
            return meals, total
        except Exception as e:
            logger.error(f"Failed to get meals by category: {e}")
            raise
    
    def get_active_meals(self, db: Session, skip: int = 0, limit: int = 20) -> tuple[List[Meal], int]:
        """Get all active meals"""
        try:
            total = db.query(Meal).filter(Meal.active == True).count()
            meals = db.query(Meal).filter(Meal.active == True).offset(skip).limit(limit).all()
            return meals, total
        except Exception as e:
            logger.error(f"Failed to get active meals: {e}")
            raise
    
    def deactivate_meal(self, db: Session, meal_id: str) -> Meal:
        """Deactivate meal"""
        meal = self.get_by_id(db, meal_id)
        
        if not meal:
            raise NotFoundException("Meal", meal_id)
        
        meal = self.update(db, meal_id, active=False)
        logger.info(f"Meal deactivated: {meal_id}")
        return meal
    
    def reactivate_meal(self, db: Session, meal_id: str) -> Meal:
        """Reactivate meal"""
        meal = self.get_by_id(db, meal_id)
        
        if not meal:
            raise NotFoundException("Meal", meal_id)
        
        meal = self.update(db, meal_id, active=True)
        logger.info(f"Meal reactivated: {meal_id}")
        return meal


class MenuService(BaseService[Menu]):
    """Service for menu operations"""
    
    def __init__(self):
        super().__init__(Menu)
    
    def publish_menu(self, db: Session, menu_id: str) -> Menu:
        """Publish menu"""
        menu = self.get_by_id(db, menu_id)
        
        if not menu:
            raise NotFoundException("Menu", menu_id)
        
        if menu.status != MenuStatus.DRAFT:
            raise ConflictException(f"Cannot publish menu with status {menu.status}")
        
        menu = self.update(db, menu_id, status=MenuStatus.PUBLISHED)
        logger.info(f"Menu published: {menu_id}")
        return menu
    
    def archive_menu(self, db: Session, menu_id: str) -> Menu:
        """Archive menu"""
        menu = self.get_by_id(db, menu_id)
        
        if not menu:
            raise NotFoundException("Menu", menu_id)
        
        menu = self.update(db, menu_id, status=MenuStatus.ARCHIVED)
        logger.info(f"Menu archived: {menu_id}")
        return menu
    
    def get_published_menus(self, db: Session, skip: int = 0, limit: int = 20) -> tuple[List[Menu], int]:
        """Get published menus"""
        try:
            total = db.query(Menu).filter(Menu.status == MenuStatus.PUBLISHED).count()
            menus = db.query(Menu).filter(
                Menu.status == MenuStatus.PUBLISHED
            ).offset(skip).limit(limit).all()
            return menus, total
        except Exception as e:
            logger.error(f"Failed to get published menus: {e}")
            raise
    
    def get_draft_menus(self, db: Session, skip: int = 0, limit: int = 20) -> tuple[List[Menu], int]:
        """Get draft menus"""
        try:
            total = db.query(Menu).filter(Menu.status == MenuStatus.DRAFT).count()
            menus = db.query(Menu).filter(
                Menu.status == MenuStatus.DRAFT
            ).offset(skip).limit(limit).all()
            return menus, total
        except Exception as e:
            logger.error(f"Failed to get draft menus: {e}")
            raise
