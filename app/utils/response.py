from typing import Generic, TypeVar, Any, Optional, List, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseData(BaseModel, Generic[T]):
    """Standard response wrapper"""
    
    response_code: str = Field(..., description="Response code")
    response_message: str = Field(..., description="Response message")
    data: Optional[T] = Field(None, description="Response data")


def success_response(
    data: Any = None,
    message: str = "Operation successful",
    code: str = "01",
) -> Dict[str, Any]:
    """Create success response"""
    return {
        "response_code": code,
        "response_message": message,
        "data": data,
    }


def created_response(
    data: Any = None,
    message: str = "Resource created successfully",
) -> Dict[str, Any]:
    """Create resource response"""
    return {
        "response_code": "201",
        "response_message": message,
        "data": data,
    }


def error_response(
    message: str,
    code: str = "500",
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create error response"""
    response = {
        "response_code": code,
        "response_message": message,
    }
    
    if details:
        response["details"] = details
    
    return response


def paginated_response(
    items: List[Any],
    total: int,
    skip: int,
    limit: int,
) -> Dict[str, Any]:
    """Create paginated response"""
    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "pages": (total + limit - 1) // limit,
        "current_page": (skip // limit) + 1 if limit > 0 else 1,
    }
