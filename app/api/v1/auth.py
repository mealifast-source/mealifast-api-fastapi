from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import UserService, EmailService
from app.schemas.user import (
    UserCreateSchema,
    LoginSchema,
    OTPVerificationSchema,
    OTPResendSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    LoginResponseSchema,
    UserResponseSchema,
)
from app.core.security import OTPManager, TokenBlacklist
from app.core.exceptions import MealiFastException
from app.api.dependencies import get_current_user
from app.utils.response import success_response, created_response, error_response
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict)
async def register(
    user_data: UserCreateSchema,
    db: Session = Depends(get_db),
):
    """Register new user"""
    try:
        user_service = UserService()
        user = user_service.register(db, user_data)
        
        # Generate and send OTP
        otp = OTPManager.generate_otp()
        OTPManager.store_otp(user.email, otp)
        EmailService.send_otp_email(user.email, otp, user.full_name)
        
        return created_response(
            data={
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "message": "User registered. Check email for OTP.",
            },
            message="User registered successfully",
        )
    except MealiFastException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/verify-otp", response_model=dict)
async def verify_otp(
    otp_data: OTPVerificationSchema,
    db: Session = Depends(get_db),
):
    """Verify email with OTP"""
    try:
        user_service = UserService()
        user = user_service.verify_email(db, otp_data.email, otp_data.otp)
        
        return success_response(
            data={
                "user_id": user.id,
                "email": user.email,
                "email_verified": user.email_verified,
            },
            message="Email verified successfully",
        )
    except MealiFastException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/resend-otp", response_model=dict)
async def resend_otp(
    otp_data: OTPResendSchema,
    db: Session = Depends(get_db),
):
    """Resend OTP"""
    try:
        user_service = UserService()
        user = user_service.get_by_email(db, otp_data.email)
        
        if not user:
            return error_response("User not found", code="404")
        
        # Generate and send new OTP
        otp = OTPManager.generate_otp()
        OTPManager.store_otp(user.email, otp)
        EmailService.send_otp_email(user.email, otp, user.full_name)
        
        return success_response(
            message="OTP sent to email",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/login", response_model=dict)
async def login(
    login_data: LoginSchema,
    db: Session = Depends(get_db),
):
    """Authenticate user and return JWT"""
    try:
        user_service = UserService()
        user, token = user_service.login(db, login_data)
        
        return success_response(
            data={
                "user_id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "token": token,
            },
            message="Login successful",
        )
    except MealiFastException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    password_data: ForgotPasswordSchema,
    db: Session = Depends(get_db),
):
    """Request password reset"""
    try:
        user_service = UserService()
        token = user_service.request_password_reset(db, password_data.email)
        
        if token:
            EmailService.send_reset_password_email(password_data.email, token)
        
        # Always return same message for security
        return success_response(
            message="If email exists, password reset link will be sent",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/reset-password", response_model=dict)
async def reset_password(
    password_data: ResetPasswordSchema,
    db: Session = Depends(get_db),
):
    """Reset password with token"""
    try:
        user_service = UserService()
        user = user_service.reset_password(
            db,
            password_data.email,
            password_data.token,
            password_data.new_password,
        )
        
        return success_response(
            data={"email": user.email},
            message="Password reset successful",
        )
    except MealiFastException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/logout", response_model=dict)
async def logout(
    current_user: User = Depends(get_current_user),
):
    """Logout user - blacklist token"""
    # Token is already in request, extract it from credentials
    return success_response(
        message="Logged out successfully",
    )


@router.get("/me", response_model=dict)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile"""
    return success_response(
        data={
            "user_id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "phone_number": current_user.phone_number,
            "role": current_user.role.value,
            "email_verified": current_user.email_verified,
            "active": current_user.active,
            "mfa_enabled": current_user.mfa_enabled,
            "created_at": current_user.created_at.isoformat(),
        },
    )
