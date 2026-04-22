from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime

from app.core.constants import UserRole


class UserBaseSchema(BaseModel):
    """Base user schema"""
    
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, max_length=20)
    role: UserRole = Field(default=UserRole.MEMBER)


class UserCreateSchema(UserBaseSchema):
    """User creation schema"""
    
    password: str = Field(..., min_length=8, max_length=255)
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """Password must contain uppercase, lowercase, and number"""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserResponseSchema(UserBaseSchema):
    """User response schema"""
    
    id: str
    email_verified: bool
    active: bool
    mfa_enabled: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserProfileSchema(UserResponseSchema):
    """User profile schema"""
    pass


class LoginSchema(BaseModel):
    """Login schema"""
    
    email: EmailStr
    password: str


class LoginResponseSchema(BaseModel):
    """Login response schema"""
    
    user_id: str
    email: str
    token: str
    role: UserRole


class OTPVerificationSchema(BaseModel):
    """OTP verification schema"""
    
    email: EmailStr
    otp: str


class OTPResendSchema(BaseModel):
    """OTP resend schema"""
    
    email: EmailStr


class ForgotPasswordSchema(BaseModel):
    """Forgot password schema"""
    
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    """Reset password schema"""
    
    email: EmailStr
    token: str
    new_password: str = Field(..., min_length=8, max_length=255)


class ChangePasswordSchema(BaseModel):
    """Change password schema"""
    
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=255)


class LogoutSchema(BaseModel):
    """Logout schema - empty body"""
    pass
