# Import all models to ensure they're registered with Base.metadata
from app.models.base import BaseModel
from app.models.user import User
from app.models.group import MealiFastGroup, GroupMember
from app.models.meal import Meal
from app.models.menu import Menu
from app.models.order import OrderWindow, MemberOrder
from app.models.subscription_plan import SubscriptionPlan
from app.models.invoice import Invoice
from app.models.delivery import DeliveryTracking
from app.models.rating import MealRating
from app.models.audit import AuditLog

__all__ = [
    "BaseModel",
    "User",
    "MealiFastGroup",
    "GroupMember",
    "Meal",
    "Menu",
    "OrderWindow",
    "MemberOrder",
    "SubscriptionPlan",
    "Invoice",
    "DeliveryTracking",
    "MealRating",
    "AuditLog",
]
