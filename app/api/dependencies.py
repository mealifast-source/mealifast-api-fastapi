from fastapi import Depends, HTTPException, status

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.database import get_db
from app.core.security import JWTManager, TokenBlacklist
from app.core.exceptions import UnauthorizedException, InvalidTokenException
from app.models import User
from app.core.constants import UserRole

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    
    # Check if token is blacklisted
    if TokenBlacklist.is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
        )
    
    # Verify token
    try:
        payload = JWTManager.verify_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise InvalidTokenException()
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    if not user.active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
        )
    
    return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current admin user"""
    if current_user.role != UserRole.PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    
    return current_user


async def get_current_group_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current group admin or platform admin"""
    if current_user.role not in (UserRole.GROUP_ADMIN, UserRole.PLATFORM_ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Group admin access required",
        )
    
    return current_user


def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Get optional current user (can be None)"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except:
        return None


# Dependency factories
def get_user_service():
    """Get user service"""
    from app.services import UserService
    return UserService()


def get_group_service():
    """Get group service"""
    from app.services import GroupService
    return GroupService()


def get_member_service():
    """Get member service"""
    from app.services import GroupMemberService
    return GroupMemberService()


def get_meal_service():
    """Get meal service"""
    from app.services import MealService
    return MealService()


def get_menu_service():
    """Get menu service"""
    from app.services import MenuService
    return MenuService()


def get_order_service():
    """Get order service"""
    from app.services import MemberOrderService
    return MemberOrderService()


def get_order_window_service():
    """Get order window service"""
    from app.services import OrderWindowService
    return OrderWindowService()


def get_invoice_service():
    """Get invoice service"""
    from app.services import InvoiceService
    return InvoiceService()


def get_delivery_service():
    """Get delivery service"""
    from app.services import DeliveryService
    return DeliveryService()


def get_plan_service():
    """Get subscription plan service"""
    from app.services import SubscriptionPlanService
    return SubscriptionPlanService()
