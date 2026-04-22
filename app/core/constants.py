from enum import Enum
from typing import Dict


class UserRole(str, Enum):
    """User roles in the system"""
    PLATFORM_ADMIN = "PLATFORM_ADMIN"
    GROUP_ADMIN = "GROUP_ADMIN"
    MEMBER = "MEMBER"


class GroupStatus(str, Enum):
    """Status of a group"""
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"


class MemberStatus(str, Enum):
    """Status of a group member"""
    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"


class MemberRole(str, Enum):
    """Role within a group"""
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class MealCategory(str, Enum):
    """Meal category"""
    BREAKFAST = "BREAKFAST"
    LUNCH = "LUNCH"
    SUPPER = "SUPPER"
    SNACK = "SNACK"


class DietaryTag(str, Enum):
    """Dietary preferences/restrictions"""
    VEGETARIAN = "VEGETARIAN"
    VEGAN = "VEGAN"
    GLUTEN_FREE = "GLUTEN_FREE"
    DAIRY_FREE = "DAIRY_FREE"
    NUT_FREE = "NUT_FREE"
    HALAL = "HALAL"
    KOSHER = "KOSHER"


class MenuStatus(str, Enum):
    """Status of a menu"""
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class MealsIncluded(str, Enum):
    """Meal tiers in subscription plan"""
    LUNCH_ONLY = "LUNCH_ONLY"
    BREAKFAST_LUNCH = "BREAKFAST_LUNCH"
    THREE_MEALS_A_DAY = "THREE_MEALS_A_DAY"


class BillingCycle(str, Enum):
    """Billing frequency"""
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class OrderStatus(str, Enum):
    """Status of a member order"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    LOCKED = "LOCKED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class OrderWindowStatus(str, Enum):
    """Status of order window"""
    SCHEDULED = "SCHEDULED"
    OPEN = "OPEN"
    CLOSED = "CLOSED"


class InvoiceStatus(str, Enum):
    """Status of invoice"""
    DRAFT = "DRAFT"
    SENT = "SENT"
    PAID = "PAID"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class DeliveryStatus(str, Enum):
    """Status of delivery"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    DELIVERED = "DELIVERED"
    PARTIAL_DELIVERY = "PARTIAL_DELIVERY"
    FAILED = "FAILED"


class AuditAction(str, Enum):
    """Audit log action types"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    PAYMENT = "PAYMENT"
    DELIVERY = "DELIVERY"


# Response codes
RESPONSE_CODES: Dict[str, str] = {
    "SUCCESS": "01",
    "CREATED": "201",
    "BAD_REQUEST": "400",
    "UNAUTHORIZED": "401",
    "FORBIDDEN": "403",
    "NOT_FOUND": "404",
    "CONFLICT": "409",
    "VALIDATION_ERROR": "422",
    "INTERNAL_ERROR": "500",
}

# Response messages
RESPONSE_MESSAGES: Dict[str, str] = {
    "SUCCESS": "Operation successful",
    "CREATED": "Resource created successfully",
    "BAD_REQUEST": "Invalid request data",
    "UNAUTHORIZED": "Unauthorized access",
    "FORBIDDEN": "Access forbidden",
    "NOT_FOUND": "Resource not found",
    "CONFLICT": "Resource already exists",
    "VALIDATION_ERROR": "Validation error",
    "INTERNAL_ERROR": "Internal server error",
}
