from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.models import MemberOrder, OrderWindow
from app.core.constants import OrderStatus, OrderWindowStatus
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class OrderWindowService(BaseService[OrderWindow]):
    """Service for order window operations"""
    
    def __init__(self):
        super().__init__(OrderWindow)
    
    def open_order_window(
        self,
        db: Session,
        group_id: str,
        week_start_date: datetime,
        open_date_time: datetime,
        close_date_time: datetime,
    ) -> OrderWindow:
        """Open order window for a group"""
        # Check if window already exists for this week
        existing_window = db.query(OrderWindow).filter(
            OrderWindow.group_id == group_id,
            OrderWindow.week_start_date == week_start_date,
        ).first()
        
        if existing_window:
            raise ConflictException(f"Order window already exists for this week")
        
        try:
            window = self.create(
                db,
                group_id=group_id,
                week_start_date=week_start_date,
                open_date_time=open_date_time,
                close_date_time=close_date_time,
                status=OrderWindowStatus.OPEN,
            )
            logger.info(f"Order window opened: {window.id}")
            return window
        except Exception as e:
            logger.error(f"Failed to open order window: {e}")
            raise
    
    def close_order_window(self, db: Session, window_id: str) -> OrderWindow:
        """Close order window"""
        window = self.get_by_id(db, window_id)
        
        if not window:
            raise NotFoundException("OrderWindow", window_id)
        
        if window.status == OrderWindowStatus.CLOSED:
            raise ConflictException("Window is already closed")
        
        window = self.update(db, window_id, status=OrderWindowStatus.CLOSED)
        logger.info(f"Order window closed: {window_id}")
        return window
    
    def is_window_open(self, db: Session, window_id: str) -> bool:
        """Check if window is open"""
        window = self.get_by_id(db, window_id)
        
        if not window:
            return False
        
        now = datetime.utcnow()
        return (
            window.status == OrderWindowStatus.OPEN and
            window.open_date_time <= now <= window.close_date_time
        )
    
    def get_group_window(self, db: Session, group_id: str, week_start_date: datetime) -> Optional[OrderWindow]:
        """Get window for specific week"""
        try:
            return db.query(OrderWindow).filter(
                OrderWindow.group_id == group_id,
                OrderWindow.week_start_date == week_start_date,
            ).first()
        except Exception as e:
            logger.error(f"Failed to get order window: {e}")
            raise


class MemberOrderService(BaseService[MemberOrder]):
    """Service for member order operations"""
    
    def __init__(self):
        super().__init__(MemberOrder)
    
    def create_order(
        self,
        db: Session,
        member_id: str,
        group_id: str,
        daily_meals: dict,
        special_notes: Optional[str] = None,
    ) -> MemberOrder:
        """Create draft order"""
        try:
            order = self.create(
                db,
                member_id=member_id,
                group_id=group_id,
                daily_meals=daily_meals,
                special_notes=special_notes,
                status=OrderStatus.DRAFT,
                week_start_date=datetime.utcnow(),
            )
            logger.info(f"Order created: {order.id}")
            return order
        except Exception as e:
            logger.error(f"Failed to create order: {e}")
            raise
    
    def submit_order(self, db: Session, order_id: str, window_id: str) -> MemberOrder:
        """Submit draft order"""
        order = self.get_by_id(db, order_id)
        
        if not order:
            raise NotFoundException("Order", order_id)
        
        if order.status != OrderStatus.DRAFT:
            raise ConflictException(f"Cannot submit order with status {order.status}")
        
        # Check if window is still open
        order_window_service = OrderWindowService()
        if not order_window_service.is_window_open(db, window_id):
            raise BadRequestException("Order window is closed")
        
        order = self.update(
            db,
            order_id,
            status=OrderStatus.SUBMITTED,
            submit_date=datetime.utcnow(),
        )
        logger.info(f"Order submitted: {order_id}")
        return order
    
    def approve_order(self, db: Session, order_id: str) -> MemberOrder:
        """Approve submitted order"""
        order = self.get_by_id(db, order_id)
        
        if not order:
            raise NotFoundException("Order", order_id)
        
        if order.status != OrderStatus.SUBMITTED:
            raise ConflictException(f"Cannot approve order with status {order.status}")
        
        order = self.update(db, order_id, status=OrderStatus.APPROVED)
        logger.info(f"Order approved: {order_id}")
        return order
    
    def reject_order(self, db: Session, order_id: str) -> MemberOrder:
        """Reject submitted order"""
        order = self.get_by_id(db, order_id)
        
        if not order:
            raise NotFoundException("Order", order_id)
        
        if order.status != OrderStatus.SUBMITTED:
            raise ConflictException(f"Cannot reject order with status {order.status}")
        
        order = self.update(db, order_id, status=OrderStatus.REJECTED)
        logger.info(f"Order rejected: {order_id}")
        return order
    
    def lock_order(self, db: Session, order_id: str) -> MemberOrder:
        """Lock order for delivery"""
        order = self.get_by_id(db, order_id)
        
        if not order:
            raise NotFoundException("Order", order_id)
        
        if order.status != OrderStatus.APPROVED:
            raise ConflictException(f"Cannot lock order with status {order.status}")
        
        order = self.update(db, order_id, status=OrderStatus.LOCKED)
        logger.info(f"Order locked: {order_id}")
        return order
    
    def get_group_orders(
        self,
        db: Session,
        group_id: str,
        week_start_date: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[MemberOrder], int]:
        """Get orders for a group"""
        try:
            query = db.query(MemberOrder).filter(MemberOrder.group_id == group_id)
            
            if week_start_date:
                query = query.filter(MemberOrder.week_start_date == week_start_date)
            
            total = query.count()
            orders = query.offset(skip).limit(limit).all()
            return orders, total
        except Exception as e:
            logger.error(f"Failed to get group orders: {e}")
            raise
    
    def get_member_orders(
        self,
        db: Session,
        member_id: str,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[MemberOrder], int]:
        """Get orders for a member"""
        try:
            total = db.query(MemberOrder).filter(MemberOrder.member_id == member_id).count()
            orders = db.query(MemberOrder).filter(
                MemberOrder.member_id == member_id
            ).offset(skip).limit(limit).all()
            return orders, total
        except Exception as e:
            logger.error(f"Failed to get member orders: {e}")
            raise
