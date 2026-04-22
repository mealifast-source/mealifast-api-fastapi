from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.constants import (
    MealCategory,
    DietaryTag,
    MenuStatus,
    MealsIncluded,
    BillingCycle,
)


# Meal Schemas
class MealBaseSchema(BaseModel):
    """Base meal schema"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    photo_url: Optional[str] = None
    category: MealCategory
    cost_price: float = Field(..., gt=0)
    dietary_tags: Optional[List[DietaryTag]] = Field(default=[])


class MealCreateSchema(MealBaseSchema):
    """Meal creation schema"""
    pass


class MealUpdateSchema(BaseModel):
    """Meal update schema"""
    
    name: Optional[str] = None
    description: Optional[str] = None
    photo_url: Optional[str] = None
    cost_price: Optional[float] = None
    dietary_tags: Optional[List[DietaryTag]] = None
    active: Optional[bool] = None


class MealResponseSchema(MealBaseSchema):
    """Meal response schema"""
    
    id: str
    active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MealListSchema(BaseModel):
    """Meal list item schema"""
    
    id: str
    name: str
    category: MealCategory
    cost_price: float
    active: bool


# Menu Schemas
class MenuBaseSchema(BaseModel):
    """Base menu schema"""
    
    name: str = Field(..., min_length=1, max_length=255)
    start_date: datetime
    end_date: datetime


class MenuCreateSchema(MenuBaseSchema):
    """Menu creation schema"""
    
    menu_items: Optional[Dict[str, Any]] = Field(default={})


class MenuPublishSchema(BaseModel):
    """Menu publish schema"""
    pass


class MenuResponseSchema(MenuBaseSchema):
    """Menu response schema"""
    
    id: str
    status: MenuStatus
    menu_items: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MenuListSchema(BaseModel):
    """Menu list item schema"""
    
    id: str
    name: str
    start_date: datetime
    end_date: datetime
    status: MenuStatus


# Subscription Plan Schemas
class SubscriptionPlanBaseSchema(BaseModel):
    """Base subscription plan schema"""
    
    plan_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price_per_meal: float = Field(..., gt=0)
    meals_included: MealsIncluded
    billing_cycle: BillingCycle
    min_members: Optional[int] = None


class SubscriptionPlanCreateSchema(SubscriptionPlanBaseSchema):
    """Subscription plan creation schema"""
    pass


class SubscriptionPlanUpdateSchema(BaseModel):
    """Subscription plan update schema"""
    
    plan_name: Optional[str] = None
    description: Optional[str] = None
    price_per_meal: Optional[float] = None
    meals_included: Optional[MealsIncluded] = None
    billing_cycle: Optional[BillingCycle] = None
    min_members: Optional[int] = None
    active: Optional[bool] = None


class SubscriptionPlanResponseSchema(SubscriptionPlanBaseSchema):
    """Subscription plan response schema"""
    
    id: str
    active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionPlanListSchema(BaseModel):
    """Subscription plan list item schema"""
    
    id: str
    plan_name: str
    price_per_meal: float
    meals_included: MealsIncluded
    billing_cycle: BillingCycle
    active: bool
