from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.core.constants import OrderStatus, InvoiceStatus, DeliveryStatus, OrderWindowStatus


# Order Window Schemas
class OrderWindowCreateSchema(BaseModel):
    """Order window creation schema"""
    
    group_id: str
    week_start_date: datetime
    open_date_time: datetime
    close_date_time: datetime


class OrderWindowResponseSchema(BaseModel):
    """Order window response schema"""
    
    id: str
    group_id: str
    week_start_date: datetime
    open_date_time: datetime
    close_date_time: datetime
    status: OrderWindowStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Member Order Schemas
class MemberOrderCreateSchema(BaseModel):
    """Member order creation schema"""
    
    group_id: str
    daily_meals: Dict[str, Dict[str, int]] = Field(
        ...,
        description="Daily meal selections, e.g., {'Monday': {'breakfast': 1, 'lunch': 1}}"
    )
    special_notes: Optional[str] = None


class MemberOrderUpdateSchema(BaseModel):
    """Member order update schema"""
    
    daily_meals: Optional[Dict[str, Dict[str, int]]] = None
    special_notes: Optional[str] = None


class MemberOrderResponseSchema(BaseModel):
    """Member order response schema"""
    
    id: str
    member_id: str
    group_id: str
    menu_id: Optional[str]
    week_start_date: datetime
    status: OrderStatus
    daily_meals: Optional[Dict[str, Any]]
    special_notes: Optional[str]
    submit_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MemberOrderListSchema(BaseModel):
    """Member order list item schema"""
    
    id: str
    member_id: str
    week_start_date: datetime
    status: OrderStatus
    submit_date: Optional[datetime]


# Invoice Schemas
class InvoiceGenerateSchema(BaseModel):
    """Invoice generation schema"""
    
    billing_start_date: datetime
    billing_end_date: datetime


class InvoiceResponseSchema(BaseModel):
    """Invoice response schema"""
    
    id: str
    group_id: str
    billing_start_date: datetime
    billing_end_date: datetime
    total_meals_delivered: Optional[int]
    total_amount: float
    amount_due: float
    status: InvoiceStatus
    line_items: Optional[List[Dict[str, Any]]]
    payment_record: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InvoiceListSchema(BaseModel):
    """Invoice list item schema"""
    
    id: str
    group_id: str
    billing_end_date: datetime
    total_amount: float
    amount_due: float
    status: InvoiceStatus


class InvoicePaymentSchema(BaseModel):
    """Invoice payment schema"""
    
    email: str = Field(..., description="Email for Paystack")


class InvoicePaymentResponseSchema(BaseModel):
    """Invoice payment response schema"""
    
    invoice_id: str
    payment_url: str
    paystack_reference: str


# Delivery Schemas
class DeliveryTrackingCreateSchema(BaseModel):
    """Delivery tracking creation schema"""
    
    group_id: str
    delivery_date: datetime
    meal_summary: Optional[Dict[str, Any]] = None


class DeliveryTrackingUpdateSchema(BaseModel):
    """Delivery tracking update schema"""
    
    status: DeliveryStatus
    missed_meals: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None


class DeliveryTrackingResponseSchema(BaseModel):
    """Delivery tracking response schema"""
    
    id: str
    group_id: str
    delivery_date: datetime
    status: DeliveryStatus
    meal_summary: Optional[Dict[str, Any]]
    missed_meals: Optional[Dict[str, Any]]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryTrackingListSchema(BaseModel):
    """Delivery tracking list item schema"""
    
    id: str
    group_id: str
    delivery_date: datetime
    status: DeliveryStatus
