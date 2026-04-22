from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# Dashboard Schemas
class PlatformDashboardSchema(BaseModel):
    """Platform dashboard schema"""
    
    total_users: int
    total_groups: int
    active_subscriptions: int
    total_orders: int
    total_revenue: float
    recent_transactions: Optional[List[Dict[str, Any]]] = None


class GroupDashboardSchema(BaseModel):
    """Group dashboard schema"""
    
    group_name: str
    total_members: int
    active_members: int
    pending_orders: int
    submitted_orders: int
    upcoming_deliveries: Optional[List[Dict[str, Any]]] = None
    invoice_summary: Optional[Dict[str, Any]] = None


# Rating Schemas
class MealRatingCreateSchema(BaseModel):
    """Meal rating creation schema"""
    
    meal_id: str
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None


class MealRatingResponseSchema(BaseModel):
    """Meal rating response schema"""
    
    id: str
    meal_id: str
    member_id: str
    rating: int
    review: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True
