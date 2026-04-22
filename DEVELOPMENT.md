# MealiFast API - Development Guide

This guide explains the architecture, design patterns, and best practices used in the MealiFast FastAPI implementation.

## Architecture Overview

The application follows a **Layered Hexagonal Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│      HTTP Layer (FastAPI Routes)        │
│  - Handles HTTP requests/responses      │
│  - Input validation via Pydantic        │
│  - Authentication/Authorization         │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│     Service Layer (Business Logic)      │
│  - Core business rules                  │
│  - Data transformations                 │
│  - Cross-cutting concerns               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│   Repository Layer (Data Access)        │
│  - SQLAlchemy ORM operations            │
│  - Query composition                    │
│  - Transaction management               │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│      Data Layer (Database Models)       │
│  - ORM entity definitions               │
│  - Relationships and constraints        │
└─────────────────────────────────────────┘
```

## Core Design Patterns

### 1. Generic Base Service (DRY Principle)

Instead of repeating CRUD operations in every service, we use a generic `BaseService[T]` class:

```python
from app.services.base_service import BaseService
from app.models import User

class UserService(BaseService[User]):
    def __init__(self):
        super().__init__(User)
    
    # Inherited CRUD methods:
    # - create(db, **kwargs) -> User
    # - get_by_id(db, id) -> User | None
    # - get_all(db, skip=0, limit=20) -> tuple[List[User], int]
    # - update(db, id, **kwargs) -> User
    # - delete(db, id) -> bool
    # - count(db) -> int
    
    # Add domain-specific methods:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()
```

**Benefits:**
- 60%+ reduction in CRUD code
- Consistent error handling
- Automatic transaction management
- Type-safe operations

### 2. Dependency Injection

We use FastAPI's dependency injection for:

**1. Database Session Injection:**
```python
from fastapi import Depends
from app.database import get_db

@router.post("/users/")
async def create_user(
    user_data: UserCreateSchema,
    db: Session = Depends(get_db),  # Injected
):
    # Use db session
    service = UserService()
    user = service.create(db, **user_data.dict())
```

**2. Authentication/Authorization:**
```python
from app.api.dependencies import get_current_user, get_current_admin_user

@router.get("/users/")
async def list_users(
    current_user: User = Depends(get_current_user),  # Any authenticated user
    db: Session = Depends(get_db),
):
    # Only authenticated users can access

@router.post("/users/")
async def create_user(
    current_user: User = Depends(get_current_admin_user),  # Admin only
    db: Session = Depends(get_db),
):
    # Only admin users can access
```

**3. Service Injection:**
```python
# Create factory functions
def get_user_service():
    return UserService()

# Use in endpoints
@router.post("/users/")
async def create_user(
    user_data: UserCreateSchema,
    user_service: UserService = Depends(get_user_service),
    db: Session = Depends(get_db),
):
    user = user_service.create(db, **user_data.dict())
```

### 3. Pydantic Schemas for Validation

Schemas serve multiple purposes:

```python
# 1. Input Validation
from pydantic import BaseModel, EmailStr, Field

class UserCreateSchema(BaseModel):
    email: EmailStr  # Auto-validates email format
    password: str = Field(..., min_length=8)  # Min length validation
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Must contain uppercase')
        if not any(c.isdigit() for c in v):
            raise ValueError('Must contain digit')
        return v

# 2. Response Serialization
class UserResponseSchema(BaseModel):
    id: str
    email: str
    full_name: str
    role: UserRole
    created_at: datetime
    
    class Config:
        from_attributes = True  # Convert ORM objects to Pydantic

# 3. API Documentation
@router.post(
    "/users/",
    response_model=UserResponseSchema,  # Auto-generates OpenAPI schema
)
async def create_user(
    user_data: UserCreateSchema,  # Auto-generates request schema
):
    ...
```

### 4. Exception Hierarchy

Custom exceptions with automatic HTTP status mapping:

```python
from app.core.exceptions import MealiFastException

class MealiFastException(Exception):
    """Base exception with HTTP mapping"""
    def __init__(self, message: str, status_code: int = 400, error_code: str = "400"):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = {}

# Specialized exceptions
class BadRequestException(MealiFastException):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, 400, "BAD_REQUEST")
        self.details = details or {}

class UnauthorizedException(MealiFastException):
    def __init__(self, message: str = "Invalid credentials"):
        super().__init__(message, 401, "UNAUTHORIZED")

class EmailAlreadyExistsException(MealiFastException):
    def __init__(self, email: str):
        super().__init__(f"Email already exists: {email}", 409, "EMAIL_EXISTS")

# Usage
try:
    user = db.query(User).filter(User.email == email).first()
    if user:
        raise EmailAlreadyExistsException(email)
except MealiFastException as e:
    raise HTTPException(status_code=e.status_code, detail=e.message)
```

## Adding New Features

### Step 1: Define Database Model

```python
# app/models/my_entity.py
from app.models.base import BaseModel

class MyEntity(BaseModel):
    __tablename__ = "my_entities"
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by_id = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    created_by = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index("idx_created_by_id", "created_by_id"),
    )
```

### Step 2: Create Pydantic Schemas

```python
# app/schemas/my_entity.py
from pydantic import BaseModel, Field

class MyEntityCreateSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(None, max_length=1000)

class MyEntityResponseSchema(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Step 3: Create Service

```python
# app/services/my_entity_service.py
from app.services.base_service import BaseService
from app.models import MyEntity

class MyEntityService(BaseService[MyEntity]):
    def __init__(self):
        super().__init__(MyEntity)
    
    def get_by_name(self, db: Session, name: str) -> MyEntity | None:
        return db.query(MyEntity).filter(MyEntity.name == name).first()
    
    def get_by_creator(self, db: Session, creator_id: str) -> List[MyEntity]:
        return db.query(MyEntity).filter(MyEntity.created_by_id == creator_id).all()
```

### Step 4: Create API Routes

```python
# app/api/v1/my_entities.py
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.services import MyEntityService
from app.schemas.my_entity import MyEntityCreateSchema, MyEntityResponseSchema
from app.api.dependencies import get_current_user
from app.utils.response import success_response, created_response

router = APIRouter(prefix="/my-entities", tags=["My Entities"])

@router.post("/", response_model=dict)
async def create_my_entity(
    entity_data: MyEntityCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = MyEntityService()
        entity = service.create(
            db,
            name=entity_data.name,
            description=entity_data.description,
            created_by_id=current_user.id,
        )
        
        return created_response(
            data={
                "id": entity.id,
                "name": entity.name,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{entity_id}", response_model=dict)
async def get_my_entity(
    entity_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        service = MyEntityService()
        entity = service.get_by_id(db, entity_id)
        
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        return success_response(
            data={
                "id": entity.id,
                "name": entity.name,
                "description": entity.description,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Step 5: Register Router in main.py

```python
# app/main.py
from app.api.v1 import my_entities

app.include_router(my_entities.router, prefix="/api/v1", tags=["My Entities"])
```

## Testing Strategy

### Unit Tests

Test individual service methods in isolation:

```python
# tests/test_my_entity_service.py
import pytest
from app.services import MyEntityService
from app.models import MyEntity

class TestMyEntityService:
    def test_create_entity(self, db):
        service = MyEntityService()
        
        entity = service.create(
            db,
            name="Test Entity",
            description="Test description",
        )
        
        assert entity.name == "Test Entity"
        assert entity.id is not None

    def test_get_by_name(self, db):
        service = MyEntityService()
        
        # Create entity
        created = service.create(db, name="Unique Name")
        
        # Retrieve by name
        found = service.get_by_name(db, "Unique Name")
        
        assert found.id == created.id
```

### Integration Tests

Test endpoints with actual HTTP requests:

```python
# tests/test_my_entity_api.py
import pytest
from fastapi.testclient import TestClient

class TestMyEntityEndpoints:
    def test_create_entity(self, client: TestClient, admin_token: str):
        response = client.post(
            "/api/v1/my-entities/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Test Entity",
                "description": "Test description",
            },
        )
        
        assert response.status_code == 201
        assert response.json()["response_code"] == "201"

    def test_get_entity(self, client: TestClient, admin_token: str):
        # Create entity
        create_response = client.post(
            "/api/v1/my-entities/",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Test Entity"},
        )
        entity_id = create_response.json()["data"]["id"]
        
        # Get entity
        get_response = client.get(
            f"/api/v1/my-entities/{entity_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        
        assert get_response.status_code == 200
```

## Logging & Monitoring

### Application Logging

```python
import logging

logger = logging.getLogger(__name__)

# Info: Important application events
logger.info(f"User {user_id} created group {group_id}")

# Warning: Unexpected but recoverable situations
logger.warning(f"Payment verification delayed for {invoice_id}")

# Error: Error conditions that need attention
logger.error(f"Failed to send invoice email: {error}")

# Debug: Detailed diagnostic information
logger.debug(f"Query executed: {query}")
```

### Structured Logging

For better log parsing and analysis:

```python
import json

# Bad
logger.info(f"User login: {user_id} from {ip_address}")

# Good
logger.info("User login", extra={
    "user_id": user_id,
    "ip_address": ip_address,
    "action": "LOGIN",
})
```

## Performance Optimization

### Database Query Optimization

```python
# Bad: N+1 query problem
users = db.query(User).all()
for user in users:
    groups = db.query(Group).filter(Group.admin_id == user.id).all()

# Good: Use relationships and eager loading
from sqlalchemy.orm import joinedload

users = db.query(User).options(
    joinedload(User.groups)
).all()
```

### Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_subscription_plan_price(plan_id: str) -> float:
    """Cache subscription plan prices"""
    db = SessionLocal()
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    return plan.price_per_meal if plan else 0.0
```

### Async Operations

```python
from concurrent.futures import ThreadPoolExecutor

# Run blocking operations in thread pool
executor = ThreadPoolExecutor(max_workers=4)

async def process_payment_async(invoice_id: str):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        executor,
        lambda: PaymentService.verify_payment(invoice_id),
    )
    return result
```

## Security Best Practices

### Input Validation

Always validate and sanitize user input:

```python
# Use Pydantic validators
from pydantic import BaseModel, validator

class UserUpdateSchema(BaseModel):
    full_name: str
    
    @validator('full_name')
    @classmethod
    def validate_full_name(cls, v):
        # Remove extra whitespace
        v = v.strip()
        
        # Check length
        if len(v) < 2:
            raise ValueError('Name too short')
        
        # Prevent SQL injection (though Pydantic handles this)
        if any(char in v for char in ['<', '>', '"', "'"]):
            raise ValueError('Invalid characters')
        
        return v
```

### Authentication & Authorization

```python
# Always use HTTPS in production
# Store secrets in environment variables
# Implement rate limiting for sensitive endpoints
# Use CORS carefully

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginSchema):
    # Limited to 5 attempts per minute
    ...
```

## Code Quality

### Type Hints

Always use type hints for better code quality and IDE support:

```python
from typing import List, Optional, Dict, Tuple

def get_group_orders(
    db: Session,
    group_id: str,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[MemberOrder], int]:
    """Get orders for a group
    
    Args:
        db: Database session
        group_id: Group ID to filter by
        skip: Number of records to skip
        limit: Number of records to return
    
    Returns:
        Tuple of (orders list, total count)
    """
    ...
```

### Documentation

Write clear docstrings following Google/NumPy style:

```python
def generate_invoice(
    self,
    db: Session,
    group_id: str,
    billing_period: DateRange,
) -> Invoice:
    """Generate invoice for a group's billing period.
    
    Calculates total meals from LOCKED orders and applies subscription
    plan pricing to create an invoice in DRAFT status.
    
    Args:
        db: Database session
        group_id: ID of group to invoice
        billing_period: Start and end dates for billing
    
    Returns:
        Created Invoice object
    
    Raises:
        NotFoundException: If group doesn't exist
        ValidationException: If no orders found in period
    
    Example:
        >>> invoice = service.generate_invoice(
        ...     db,
        ...     "group-123",
        ...     DateRange(start=date(2024,1,1), end=date(2024,1,31))
        ... )
    """
```

## Deployment Checklist

- [ ] Set strong JWT secret key
- [ ] Configure database backups
- [ ] Set up Redis persistence
- [ ] Configure email SMTP credentials
- [ ] Set Paystack production keys
- [ ] Enable CORS only for trusted origins
- [ ] Set DEBUG=false in production
- [ ] Configure logging to external service
- [ ] Set up monitoring and alerting
- [ ] Configure rate limiting
- [ ] Test payment flow end-to-end
- [ ] Set up automatic database migrations
- [ ] Configure secrets management

---

For more information, see [README.md](README.md) for complete documentation.
