from sqlalchemy.orm import Session
from typing import Optional
import logging

from app.models import User
from app.schemas.user import (
    UserCreateSchema,
    UserProfileSchema,
    LoginSchema,
)
from app.core.security import PasswordManager, JWTManager, OTPManager, PasswordResetTokenManager
from app.core.exceptions import (
    InvalidCredentialsException,
    EmailAlreadyExistsException,
    NotFoundException,
    AccountNotVerifiedException,
    AccountInactiveException,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class UserService(BaseService[User]):
    """Service for user operations"""
    
    def __init__(self):
        super().__init__(User)
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return db.query(User).filter(User.email == email).first()
        except Exception as e:
            logger.error(f"Failed to get user by email: {e}")
            raise
    
    def register(self, db: Session, user_data: UserCreateSchema) -> User:
        """Register new user"""
        # Check if email already exists
        existing_user = self.get_by_email(db, user_data.email)
        if existing_user:
            raise EmailAlreadyExistsException(user_data.email)
        
        # Hash password
        password_hash = PasswordManager.hash_password(user_data.password)
        
        # Create user (inactive until email verified)
        user = self.create(
            db,
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number,
            role=user_data.role,
            active=True,  # Account active but email not verified
            email_verified=False,
        )
        
        logger.info(f"User registered: {user.email}")
        return user
    
    def login(self, db: Session, login_data: LoginSchema) -> tuple[User, str]:
        """Authenticate user and return JWT token"""
        user = self.get_by_email(db, login_data.email)
        
        if not user:
            raise InvalidCredentialsException()
        
        # Verify password
        if not PasswordManager.verify_password(login_data.password, user.password_hash):
            raise InvalidCredentialsException()
        
        # Check if account is active
        if not user.active:
            raise AccountInactiveException()
        
        # Generate JWT token
        token = JWTManager.create_token(
            subject=user.id,
            additional_claims={
                "email": user.email,
                "role": user.role.value,
            },
        )
        
        logger.info(f"User logged in: {user.email}")
        return user, token
    
    def verify_email(self, db: Session, email: str, otp: str) -> User:
        """Verify user email with OTP"""
        user = self.get_by_email(db, email)
        
        if not user:
            raise NotFoundException("User", email)
        
        # Verify OTP
        if not OTPManager.verify_otp(email, otp):
            from app.core.exceptions import InvalidOTPException
            raise InvalidOTPException()
        
        # Update user
        user = self.update(db, user.id, email_verified=True)
        
        logger.info(f"Email verified: {email}")
        return user
    
    def request_password_reset(self, db: Session, email: str) -> str:
        """Request password reset token"""
        user = self.get_by_email(db, email)
        
        if not user:
            # Don't reveal if email exists
            logger.warning(f"Password reset requested for non-existent email: {email}")
            return ""
        
        # Generate reset token
        token = PasswordResetTokenManager.create_reset_token(email)
        
        logger.info(f"Password reset token created for: {email}")
        return token
    
    def reset_password(self, db: Session, email: str, token: str, new_password: str) -> User:
        """Reset password with token"""
        user = self.get_by_email(db, email)
        
        if not user:
            raise NotFoundException("User", email)
        
        # Verify reset token
        if not PasswordResetTokenManager.verify_reset_token(email, token):
            from app.core.exceptions import InvalidResetTokenException
            raise InvalidResetTokenException()
        
        # Hash new password
        password_hash = PasswordManager.hash_password(new_password)
        
        # Update password
        user = self.update(db, user.id, password_hash=password_hash)
        
        # Consume token
        PasswordResetTokenManager.consume_reset_token(email)
        
        logger.info(f"Password reset successful: {email}")
        return user
    
    def change_password(self, db: Session, user_id: str, current_password: str, new_password: str) -> User:
        """Change password for authenticated user"""
        user = self.get_by_id(db, user_id)
        
        if not user:
            raise NotFoundException("User", user_id)
        
        # Verify current password
        if not PasswordManager.verify_password(current_password, user.password_hash):
            raise InvalidCredentialsException()
        
        # Hash new password
        password_hash = PasswordManager.hash_password(new_password)
        
        # Update password
        user = self.update(db, user.id, password_hash=password_hash)
        
        logger.info(f"Password changed: {user.email}")
        return user
    
    def update_profile(self, db: Session, user_id: str, **kwargs) -> User:
        """Update user profile"""
        user = self.get_by_id(db, user_id)
        
        if not user:
            raise NotFoundException("User", user_id)
        
        # Remove password hash from updates if present
        kwargs.pop("password_hash", None)
        kwargs.pop("email", None)  # Don't allow email change via this method
        
        user = self.update(db, user_id, **kwargs)
        
        logger.info(f"Profile updated: {user.email}")
        return user
