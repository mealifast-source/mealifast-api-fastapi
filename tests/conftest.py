import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import asyncio

from app.main import app
from app.database import get_db, Base
from app.config import settings


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create test tables
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture(scope="function")
def admin_user_data():
    """Sample admin user data"""
    return {
        "email": "admin@test.com",
        "password": "AdminPassword123!",
        "full_name": "Admin User",
        "phone_number": "+1234567890",
    }


@pytest.fixture(scope="function")
def member_user_data():
    """Sample member user data"""
    return {
        "email": "member@test.com",
        "password": "MemberPassword123!",
        "full_name": "Member User",
        "phone_number": "+1987654321",
    }


@pytest.fixture(scope="function")
async def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()
