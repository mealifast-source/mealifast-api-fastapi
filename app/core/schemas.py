from pydantic import BaseModel, Field
from typing import Optional, Generic, TypeVar, Any, Dict
from datetime import datetime

T = TypeVar("T")


class ResponseSchema(BaseModel, Generic[T]):
    """Standard API response format"""
    
    response_code: str = Field(..., description="Response code")
    response_message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")


class PaginationParams(BaseModel):
    """Pagination parameters"""
    
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    
    items: list[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    skip: int = Field(..., description="Number of items skipped")
    limit: int = Field(..., description="Limit per page")
    
    @property
    def pages(self) -> int:
        """Calculate total pages"""
        return (self.total + self.limit - 1) // self.limit
    
    @property
    def current_page(self) -> int:
        """Calculate current page"""
        return (self.skip // self.limit) + 1


class TimestampedModel(BaseModel):
    """Base model with timestamps"""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True


class ErrorDetail(BaseModel):
    """Error detail model"""
    
    field: Optional[str] = Field(None, description="Field name with error")
    message: str = Field(..., description="Error message")


class ErrorResponse(BaseModel):
    """Error response format"""
    
    response_code: str = Field(..., description="Error code")
    response_message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    errors: Optional[list[ErrorDetail]] = Field(None, description="Field-level errors")
