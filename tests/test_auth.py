"""
Tests for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models import User
from app.core.security import PasswordManager
from app.core.constants import UserRole


class TestAuthEndpoints:
    """Authentication endpoint tests"""

    def test_register_user_success(self, client: TestClient):
        """Test successful user registration"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "Password123!",
                "full_name": "New User",
                "phone_number": "+1234567890",
            },
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["response_code"] == "201"
        assert "user_id" in data["data"]

    def test_register_user_invalid_email(self, client: TestClient):
        """Test registration with invalid email"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "invalidemail",
                "password": "Password123!",
                "full_name": "New User",
                "phone_number": "+1234567890",
            },
        )
        
        assert response.status_code == 422  # Validation error

    def test_register_user_weak_password(self, client: TestClient):
        """Test registration with weak password"""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@test.com",
                "password": "weak",
                "full_name": "New User",
                "phone_number": "+1234567890",
            },
        )
        
        assert response.status_code == 422

    def test_register_duplicate_email(self, client: TestClient, db: Session):
        """Test registration with existing email"""
        # Create first user
        password_manager = PasswordManager()
        user = User(
            email="existing@test.com",
            password_hash=password_manager.hash_password("Password123!"),
            full_name="Existing User",
            phone_number="+1234567890",
            role=UserRole.MEMBER,
            email_verified=True,
            active=True,
        )
        db.add(user)
        db.commit()
        
        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "existing@test.com",
                "password": "Password123!",
                "full_name": "New User",
                "phone_number": "+1234567890",
            },
        )
        
        assert response.status_code == 409  # Conflict

    def test_login_success(self, client: TestClient, db: Session):
        """Test successful login"""
        # Create user
        password_manager = PasswordManager()
        user = User(
            email="testuser@test.com",
            password_hash=password_manager.hash_password("Password123!"),
            full_name="Test User",
            phone_number="+1234567890",
            role=UserRole.MEMBER,
            email_verified=True,
            active=True,
        )
        db.add(user)
        db.commit()
        
        # Login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@test.com",
                "password": "Password123!",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["response_code"] == "01"
        assert "access_token" in data["data"]
        assert data["data"]["user"]["email"] == "testuser@test.com"

    def test_login_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@test.com",
                "password": "Password123!",
            },
        )
        
        assert response.status_code == 401  # Unauthorized

    def test_login_wrong_password(self, client: TestClient, db: Session):
        """Test login with wrong password"""
        # Create user
        password_manager = PasswordManager()
        user = User(
            email="testuser@test.com",
            password_hash=password_manager.hash_password("Password123!"),
            full_name="Test User",
            phone_number="+1234567890",
            role=UserRole.MEMBER,
            email_verified=True,
            active=True,
        )
        db.add(user)
        db.commit()
        
        # Login with wrong password
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@test.com",
                "password": "WrongPassword123!",
            },
        )
        
        assert response.status_code == 401

    def test_get_current_user(self, client: TestClient, db: Session):
        """Test getting current user profile"""
        # Create and login user
        password_manager = PasswordManager()
        user = User(
            email="testuser@test.com",
            password_hash=password_manager.hash_password("Password123!"),
            full_name="Test User",
            phone_number="+1234567890",
            role=UserRole.MEMBER,
            email_verified=True,
            active=True,
        )
        db.add(user)
        db.commit()
        
        # Login to get token
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@test.com",
                "password": "Password123!",
            },
        )
        token = login_response.json()["data"]["access_token"]
        
        # Get profile
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["email"] == "testuser@test.com"

    def test_logout_success(self, client: TestClient, db: Session):
        """Test user logout"""
        # Create and login user
        password_manager = PasswordManager()
        user = User(
            email="testuser@test.com",
            password_hash=password_manager.hash_password("Password123!"),
            full_name="Test User",
            phone_number="+1234567890",
            role=UserRole.MEMBER,
            email_verified=True,
            active=True,
        )
        db.add(user)
        db.commit()
        
        # Login
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "testuser@test.com",
                "password": "Password123!",
            },
        )
        token = login_response.json()["data"]["access_token"]
        
        # Logout
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200
