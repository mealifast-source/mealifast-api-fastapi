# MealiFast API - FastAPI Implementation

A complete rewrite of the MealiFast corporate meal management platform using FastAPI, emphasizing senior-level engineering practices, DRY principles, and production-ready code.

## Project Overview

MealiFast is a comprehensive meal ordering and group subscription management system designed for corporate environments. It handles:

- **User Management**: Multi-role authentication (Platform Admin, Group Admin, Member) with JWT and OTP verification
- **Group Management**: Create meal groups, manage members, track subscriptions
- **Meal Catalog**: Create and manage meals with dietary tags and pricing
- **Menu Planning**: Weekly/periodic menu creation and publishing
- **Order Management**: Order windows, member orders, order approvals and locking
- **Billing & Invoicing**: Automated invoice generation, Paystack payment integration
- **Delivery Tracking**: Track deliveries, record missed meals, manage status
- **Ratings & Feedback**: Member meal ratings and reviews
- **Audit Logging**: Complete audit trail for compliance

## Architecture

The application follows a **Hexagonal (Ports & Adapters) Architecture** with clear separation of concerns:

```
HTTP Layer (API Routes)
    ↓
Service Layer (Business Logic)
    ↓
Repository Layer (Data Access via SQLAlchemy)
    ↓
Data Layer (Database Models)
```

### Key Design Principles

1. **DRY (Don't Repeat Yourself)**: 
   - Generic `BaseService[T]` class eliminates CRUD code duplication
   - Reusable Pydantic schemas for validation
   - Centralized response formatting

2. **Type Safety**:
   - Full type hints throughout
   - Pydantic models for automatic validation
   - SQLAlchemy ORM for database type safety

3. **Security**:
   - JWT authentication with 24-hour expiration
   - Token blacklist for logout functionality
   - Password hashing with bcrypt (12 rounds)
   - OTP verification for email registration
   - Role-based access control (RBAC)

4. **Maintainability**:
   - Single responsibility principle
   - Dependency injection for testability
   - Comprehensive error handling
   - Structured logging

## Technology Stack

### Core Framework
- **FastAPI** 0.104.1 - Modern async web framework
- **Python** 3.9+ - Language requirement
- **Uvicorn** - ASGI server

### Data & Persistence
- **SQLAlchemy** 2.0.23 - ORM with async support
- **MySQL** / PyMySQL - Relational database
- **Alembic** - Database migrations (optional)

### Authentication & Security
- **python-jose** - JWT handling
- **passlib** - Password hashing
- **bcrypt** - Secure hashing algorithm

### External Services
- **Paystack** - Payment gateway for invoices
- **Redis** - Caching, OTP storage, token blacklist
- **SMTP/Gmail** - Email delivery
- **APScheduler** - Background task scheduling

### Utilities
- **Pydantic** 2.5.0 - Data validation and serialization
- **python-multipart** - File upload handling
- **requests** - HTTP client for Paystack API

## Project Structure

```
mealifast-api-fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── config.py                  # Configuration management
│   ├── database.py                # SQLAlchemy setup, session management
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py        # JWT auth, role checks, service factories
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py            # Authentication endpoints (register, login, OTP)
│   │       ├── groups.py          # Group management endpoints
│   │       ├── meals.py           # Meal CRUD endpoints
│   │       ├── menus.py           # Menu CRUD and publishing
│   │       ├── orders.py          # Order windows and member orders
│   │       ├── invoices.py        # Invoice generation and Paystack payments
│   │       ├── delivery.py        # Delivery tracking endpoints
│   │       └── dashboard.py       # Analytics and ratings
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py           # Enums: UserRole, GroupStatus, OrderStatus, etc.
│   │   ├── exceptions.py          # 21 custom exception classes with HTTP mapping
│   │   ├── schemas.py             # Base response schemas
│   │   └── security.py            # JWT, OTP, password, and token managers
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # BaseModel mixin with id, created_at, updated_at
│   │   ├── user.py                # User entity
│   │   ├── group.py               # MealiFastGroup and GroupMember
│   │   ├── meal.py                # Meal entity
│   │   ├── menu.py                # Menu entity
│   │   ├── order.py               # OrderWindow and MemberOrder
│   │   ├── subscription_plan.py   # SubscriptionPlan entity
│   │   ├── invoice.py             # Invoice entity
│   │   ├── delivery.py            # DeliveryTracking entity
│   │   ├── rating.py              # MealRating entity
│   │   └── audit.py               # AuditLog entity
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                # 9 user-related schemas
│   │   ├── group.py               # 10 group/member schemas
│   │   ├── catalog.py             # 11 meal/menu/plan schemas
│   │   ├── order.py               # 10 order/invoice/delivery schemas
│   │   └── dashboard.py           # 3 dashboard schemas
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py        # Generic BaseService[T] for CRUD operations
│   │   ├── user_service.py        # Authentication and user operations
│   │   ├── group_service.py       # Group and member management
│   │   ├── meal_service.py        # Meal and menu operations
│   │   ├── order_service.py       # Order windows and member orders
│   │   ├── operations_service.py  # Invoices, payments, delivery, ratings
│   │   ├── auxiliary_service.py   # Subscription plans and email
│   │   ├── dashboard_service.py   # Analytics and dashboard data
│   │   └── billing_scheduler_service.py  # Scheduled billing tasks
│   │
│   ├── middleware/
│   │   ├── error_handling.py      # Global error handling and request logging
│   │   └── audit_log_service.py   # Audit trail recording
│   │
│   └── utils/
│       ├── __init__.py
│       ├── response.py            # Response formatting utilities
│       └── logging_config.py      # Logging configuration
│
├── tests/                         # Unit and integration tests (optional)
│
├── requirements.txt               # Python dependencies (26 packages)
├── .env.example                   # Configuration template
├── .gitignore                     # Git ignore rules
├── build.gradle                   # Original Spring Boot build (reference)
├── README.md                      # This file
└── Procfile                       # Heroku/deployment configuration
```

## Installation & Setup

### Prerequisites
- Python 3.9 or higher
- MySQL 5.7 or higher
- Redis 5.0 or higher
- Git

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/mealifast-api-fastapi.git
cd mealifast-api-fastapi
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n mealifast python=3.9
conda activate mealifast
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your values
nano .env
```

Required environment variables:
```env
# Application
APP_NAME=MealiFast API
APP_VERSION=1.0.0
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/mealifast
SQLALCHEMY_ECHO=false

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_ASYNC_URL=redis://localhost:6379/1

# JWT
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Email (SMTP)
EMAIL_FROM=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Paystack
PAYSTACK_PUBLIC_KEY=pk_test_xxx
PAYSTACK_SECRET_KEY=sk_test_xxx
PAYSTACK_API_URL=https://api.paystack.co

# CORS
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Server
HOST=0.0.0.0
PORT=8000

# Application URL
APP_URL=http://localhost:8000
```

### 5. Initialize Database
```bash
# Create database
mysql -u root -p < scripts/init_db.sql

# Or let the app create tables on first run
python -c "from app.database import init_db; init_db()"
```

### 6. Run Application
```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

API documentation will be auto-generated at `http://localhost:8000/docs` (Swagger UI)

## API Endpoints Overview

### Authentication (`/api/v1/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/verify-otp` - Verify email with OTP
- `POST /auth/resend-otp` - Resend OTP
- `POST /auth/login` - Login and get JWT token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token
- `POST /auth/logout` - Logout and blacklist token
- `GET /auth/me` - Get current user profile

### Groups (`/api/v1/groups`)
- `POST /groups/` - Create new group
- `GET /groups/{group_id}` - Get group details
- `PUT /groups/{group_id}/approve` - Approve pending group (admin)
- `POST /groups/{group_id}/members/invite` - Invite member
- `GET /groups/{group_id}/members` - List group members
- `PUT /groups/{group_id}/members/{member_id}/role` - Update member role
- `PUT /groups/{group_id}/suspend` - Suspend group (admin)

### Meals (`/api/v1/meals`)
- `POST /meals/` - Create meal (admin)
- `GET /meals/` - List meals with pagination
- `GET /meals/{meal_id}` - Get meal details
- `PUT /meals/{meal_id}` - Update meal (admin)
- `DELETE /meals/{meal_id}` - Delete meal (admin)
- `GET /meals/?category=breakfast` - Filter by category

### Menus (`/api/v1/menus`)
- `POST /menus/` - Create menu (draft)
- `GET /menus/` - List menus
- `GET /menus/{menu_id}` - Get menu details
- `PUT /menus/{menu_id}/publish` - Publish menu
- `PUT /menus/{menu_id}/archive` - Archive menu

### Orders (`/api/v1/orders`)
- `POST /orders/windows/` - Open order window (admin)
- `GET /orders/windows/{window_id}` - Get order window
- `PUT /orders/windows/{window_id}/close` - Close order window (admin)
- `POST /orders/` - Create order
- `GET /orders/{order_id}` - Get order details
- `PUT /orders/{order_id}/submit` - Submit order
- `PUT /orders/{order_id}/approve` - Approve order (admin)
- `PUT /orders/{order_id}/lock` - Lock order (admin)

### Invoices (`/api/v1/invoices`)
- `POST /invoices/{group_id}/generate` - Generate invoice (admin)
- `GET /invoices/{invoice_id}` - Get invoice
- `PUT /invoices/{invoice_id}/send` - Send invoice
- `POST /invoices/{invoice_id}/pay` - Initialize Paystack payment
- `GET /invoices/{group_id}/list` - List group invoices

### Delivery (`/api/v1/delivery`)
- `POST /delivery/` - Create delivery record
- `GET /delivery/{delivery_id}` - Get delivery details
- `PUT /delivery/{delivery_id}/status` - Update delivery status
- `PUT /delivery/{delivery_id}/record-missed` - Record missed meals
- `GET /delivery/group/{group_id}` - Get group deliveries

### Dashboard (`/api/v1/dashboard`)
- `GET /dashboard/platform` - Platform analytics (admin)
- `GET /dashboard/group/{group_id}` - Group analytics
- `GET /dashboard/member/{member_id}` - Member dashboard
- `GET /dashboard/summary` - Current user summary
- `POST /dashboard/ratings/` - Create meal rating
- `GET /dashboard/ratings/meal/{meal_id}` - Get meal ratings

## Authentication Flow

### Registration & Email Verification
1. User calls `POST /auth/register` with email and password
2. System creates inactive user, hashes password, generates OTP
3. OTP email sent to user's email address (10-minute TTL in Redis)
4. User calls `POST /auth/verify-otp` with email and OTP
5. System verifies OTP, marks email as verified, activates user
6. User can now login

### Login & JWT
1. User calls `POST /auth/login` with email and password
2. System validates credentials, generates JWT token with 24-hour expiration
3. Client stores JWT in Authorization header: `Bearer <token>`
4. All subsequent requests validated using JWT
5. Token blacklisted in Redis on logout (24-hour TTL)

### Password Reset
1. User calls `POST /auth/forgot-password` with email
2. System generates secure reset token (1-hour TTL)
3. Email sent with reset link containing token
4. User calls `POST /auth/reset-password` with email, token, new password
5. System verifies token, updates password, consumes token

## Database Schema

### Core Entities

**Users**
- id (UUID)
- email (unique)
- password_hash
- full_name
- phone_number
- role (PLATFORM_ADMIN, GROUP_ADMIN, MEMBER)
- email_verified, active, mfa_enabled
- created_at, updated_at

**MealiFastGroup**
- id (UUID)
- group_name, company_name
- group_admin_id (FK: User)
- subscription_plan_id (FK: SubscriptionPlan)
- plan_start_date, plan_end_date
- status (PENDING, ACTIVE, SUSPENDED, INACTIVE)
- created_at, updated_at

**GroupMember**
- id (UUID)
- user_id (FK: User)
- group_id (FK: MealiFastGroup)
- status (INVITED, ACTIVE, SUSPENDED, INACTIVE)
- member_role (MEMBER, COORDINATOR)
- dietary_preferences (JSON array)
- created_at, updated_at

**Meal**
- id (UUID)
- name, description, photo_url
- category (BREAKFAST, LUNCH, DINNER, SNACK)
- cost_price
- dietary_tags (JSON array: VEGETARIAN, VEGAN, GLUTEN_FREE, etc.)
- active

**Menu**
- id (UUID)
- name
- start_date, end_date
- status (DRAFT, PUBLISHED, ARCHIVED)
- menu_items (JSON: {"Monday": {"breakfast": [meal_ids], "lunch": [...]}})
- created_at, updated_at

**OrderWindow**
- id (UUID)
- group_id (FK: MealiFastGroup)
- week_start_date
- open_date_time, close_date_time
- status (OPEN, CLOSED)

**MemberOrder**
- id (UUID)
- member_id (FK: GroupMember)
- group_id (FK: MealiFastGroup)
- menu_id (FK: Menu)
- week_start_date
- status (DRAFT, SUBMITTED, APPROVED, REJECTED, LOCKED)
- daily_meals (JSON: {"Monday": {"breakfast": 2, "lunch": 1}, ...})
- special_notes
- submit_date, created_at, updated_at

**Invoice**
- id (UUID)
- group_id (FK: MealiFastGroup)
- billing_start_date, billing_end_date
- total_meals_delivered
- total_amount, amount_due
- status (DRAFT, SENT, PAID, PARTIAL_PAID, OVERDUE)
- line_items (JSON array)
- payment_record (JSON: Paystack reference and details)
- created_at, updated_at

**DeliveryTracking**
- id (UUID)
- group_id (FK: MealiFastGroup)
- delivery_date
- status (PENDING, IN_PROGRESS, DELIVERED, PARTIAL_DELIVERY, FAILED)
- meal_summary (JSON)
- missed_meals (JSON)
- notes
- created_at, updated_at

**MealRating**
- id (UUID)
- meal_id (FK: Meal)
- member_id (FK: GroupMember)
- rating (1-5)
- review
- created_at

**AuditLog**
- id (UUID)
- user_id (FK: User, nullable)
- action (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, etc.)
- entity_type, entity_id
- old_value, new_value (text)
- description
- created_at

## Security Considerations

1. **Password Security**:
   - Hashed with bcrypt (12 rounds) equivalent to PBKDF2
   - Minimum 8 characters with uppercase, lowercase, and digit
   - Never returned in API responses

2. **JWT Authentication**:
   - HS256 algorithm with 32+ character secret key
   - 24-hour expiration (refresh tokens in future)
   - Token blacklist for logout (24-hr TTL in Redis)
   - Subject and role claims included

3. **OTP Verification**:
   - 6-digit codes generated cryptographically
   - 10-minute TTL, single-use
   - Redis-backed for high performance

4. **Password Reset**:
   - Secure tokens with 1-hour TTL
   - Email verification required
   - Single-use tokens consumed after use

5. **CORS Protection**:
   - Whitelist of allowed origins
   - Credentials only from trusted sources
   - Methods and headers restricted

6. **Role-Based Access Control**:
   - PLATFORM_ADMIN: Full system access
   - GROUP_ADMIN: Group and billing management
   - MEMBER: Own orders and ratings only

7. **Audit Logging**:
   - All sensitive operations logged
   - User ID, action, entity, changes tracked
   - Compliance ready

## Background Tasks

### Daily Billing (2 AM UTC)
- Query groups with plan_end_date = today
- Generate invoices with calculated meals and amounts
- Send invoice emails to group admins
- Update group billing dates for next cycle

### Weekly Reminders (Monday 8 AM UTC)
- Get open order windows closing in next 24 hours
- Send reminder emails to all group members
- Include closing time and ordering deadline

## Error Handling

All errors return consistent JSON format:
```json
{
  "response_code": "400",
  "response_message": "Bad Request",
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "details": {
      "field": "email",
      "message": "Invalid email format"
    }
  }
}
```

### Exception Hierarchy
- `MealiFastException` (base)
  - `BadRequestException` (400)
  - `UnauthorizedException` (401)
  - `ForbiddenException` (403)
  - `NotFoundException` (404)
  - `ConflictException` (409)
  - `ValidationException` (422)
  - Domain-specific exceptions (InvalidCredentialsException, etc.)

## Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Deployment

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn

# Run with 4 workers
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Using Docker

```bash
# Build image
docker build -t mealifast-api .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="mysql+pymysql://user:pass@db:3306/mealifast" \
  -e REDIS_URL="redis://redis:6379/0" \
  mealifast-api
```

### Using Heroku

```bash
# Deploy
heroku create mealifast-api
heroku config:set DATABASE_URL="mysql+pymysql://..."
git push heroku main
```

## Monitoring & Logging

- Console logs with structured format
- Rotating file logs (10MB per file, 10 backup files)
- Separate error log for critical issues
- Request ID tracking via middleware
- Audit logs for compliance

Log files location: `./logs/`
- `app.log` - All application logs
- `error.log` - Errors only

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature/feature-name`
5. Submit pull request

### Code Standards
- Follow PEP 8
- Use type hints throughout
- Write docstrings for public functions
- Keep functions focused and testable
- Use meaningful variable names

## API Documentation

Once running, access interactive documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, feature requests, or questions:
- GitHub Issues: [Create an issue]
- Email: support@mealifast.com

## Changelog

### Version 1.0.0 (Initial Release)
- Complete FastAPI rewrite
- All 40+ endpoints implemented
- JWT authentication with OTP
- Paystack payment integration
- Background task scheduling
- Comprehensive audit logging
- Senior-level code architecture

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python best practices.**
