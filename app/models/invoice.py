from sqlalchemy import Column, String, Float, DateTime, Enum, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.base import BaseModel
from app.core.constants import InvoiceStatus


class Invoice(Base, BaseModel):
    """Invoice model"""
    
    __tablename__ = "invoices"
    
    group_id = Column(String(36), ForeignKey("mealifast_groups.id"), nullable=False)
    
    billing_start_date = Column(DateTime, nullable=False)
    billing_end_date = Column(DateTime, nullable=False)
    
    total_meals_delivered = Column(String(36), nullable=True)
    total_amount = Column(Float, nullable=False)
    amount_due = Column(Float, nullable=False)
    
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False)
    
    # JSON: itemized billing details
    line_items = Column(JSON, default=[], nullable=True)
    # JSON: Paystack transaction details
    payment_record = Column(JSON, default={}, nullable=True)
    
    # Relationships
    group = relationship(
        "MealiFastGroup",
        back_populates="invoices",
    )
    
    __table_args__ = (
        Index("idx_group_id", "group_id"),
        Index("idx_status", "status"),
        Index("idx_billing_end_date", "billing_end_date"),
    )
