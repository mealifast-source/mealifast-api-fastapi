from sqlalchemy.orm import Session
from typing import List, Optional
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.models import SubscriptionPlan
from app.core.exceptions import NotFoundException
from app.config import settings
from app.core.security import OTPManager
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class SubscriptionPlanService(BaseService[SubscriptionPlan]):
    """Service for subscription plan operations"""
    
    def __init__(self):
        super().__init__(SubscriptionPlan)
    
    def get_active_plans(self, db: Session, skip: int = 0, limit: int = 20) -> tuple[List[SubscriptionPlan], int]:
        """Get active subscription plans"""
        try:
            total = db.query(SubscriptionPlan).filter(SubscriptionPlan.active == True).count()
            plans = db.query(SubscriptionPlan).filter(
                SubscriptionPlan.active == True
            ).offset(skip).limit(limit).all()
            return plans, total
        except Exception as e:
            logger.error(f"Failed to get active plans: {e}")
            raise
    
    def deactivate_plan(self, db: Session, plan_id: str) -> SubscriptionPlan:
        """Deactivate plan"""
        plan = self.get_by_id(db, plan_id)
        
        if not plan:
            raise NotFoundException("SubscriptionPlan", plan_id)
        
        plan = self.update(db, plan_id, active=False)
        logger.info(f"Plan deactivated: {plan_id}")
        return plan


class EmailService:
    """Service for sending emails"""
    
    @staticmethod
    def send_email(
        to_email: str,
        subject: str,
        html_content: str,
    ) -> bool:
        """Send email via SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.mail_from
            msg["To"] = to_email
            
            msg.attach(MIMEText(html_content, "html"))
            
            with smtplib.SMTP(settings.mail_server, settings.mail_port) as server:
                server.starttls()
                server.login(settings.mail_username, settings.mail_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    @staticmethod
    def send_otp_email(email: str, otp: str, full_name: str = "") -> bool:
        """Send OTP email"""
        html_content = f"""
        <html>
            <body>
                <h2>MealiFast - Email Verification</h2>
                <p>Hi {full_name or 'User'},</p>
                <p>Your One-Time Password (OTP) for email verification is:</p>
                <h3 style="color: #2E86AB; font-family: monospace;">{otp}</h3>
                <p>This OTP will expire in {settings.otp_expiration_minutes} minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <hr>
                <p><small>© MealiFast. All rights reserved.</small></p>
            </body>
        </html>
        """
        return EmailService.send_email(
            email,
            "MealiFast - Email Verification OTP",
            html_content,
        )
    
    @staticmethod
    def send_welcome_email(email: str, full_name: str) -> bool:
        """Send welcome email"""
        html_content = f"""
        <html>
            <body>
                <h2>Welcome to MealiFast!</h2>
                <p>Hi {full_name},</p>
                <p>Welcome to MealiFast, your corporate meal management platform.</p>
                <p>You can now:</p>
                <ul>
                    <li>Browse available meals</li>
                    <li>Join or create meal groups</li>
                    <li>Place weekly meal orders</li>
                    <li>Track deliveries</li>
                    <li>Rate and review meals</li>
                </ul>
                <p>Get started by exploring menus and connecting with your team!</p>
                <hr>
                <p><small>© MealiFast. All rights reserved.</small></p>
            </body>
        </html>
        """
        return EmailService.send_email(
            email,
            "Welcome to MealiFast!",
            html_content,
        )
    
    @staticmethod
    def send_reset_password_email(email: str, reset_token: str, full_name: str = "") -> bool:
        """Send password reset email"""
        reset_link = f"{settings.app_url}/reset-password?token={reset_token}&email={email}"
        
        html_content = f"""
        <html>
            <body>
                <h2>MealiFast - Password Reset</h2>
                <p>Hi {full_name or 'User'},</p>
                <p>We received a request to reset your password. Click the link below to proceed:</p>
                <p><a href="{reset_link}" style="color: #2E86AB; text-decoration: none;">Reset Password</a></p>
                <p>This link will expire in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
                <hr>
                <p><small>© MealiFast. All rights reserved.</small></p>
            </body>
        </html>
        """
        return EmailService.send_email(
            email,
            "MealiFast - Password Reset",
            html_content,
        )
    
    @staticmethod
    def send_invoice_email(
        email: str,
        invoice_id: str,
        total_amount: float,
        group_name: str,
        payment_url: Optional[str] = None,
    ) -> bool:
        """Send invoice email"""
        payment_button = ""
        if payment_url:
            payment_button = f'<p><a href="{payment_url}" style="background-color: #2E86AB; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Pay Now</a></p>'
        
        html_content = f"""
        <html>
            <body>
                <h2>MealiFast - Invoice</h2>
                <p>Hi,</p>
                <p>Your invoice for <strong>{group_name}</strong> is ready for payment.</p>
                <p><strong>Invoice ID:</strong> {invoice_id}</p>
                <p><strong>Total Amount:</strong> #{total_amount:,.2f}</p>
                {payment_button}
                <p>Thank you for using MealiFast!</p>
                <hr>
                <p><small>© MealiFast. All rights reserved.</small></p>
            </body>
        </html>
        """
        return EmailService.send_email(
            email,
            f"MealiFast - Invoice {invoice_id}",
            html_content,
        )
