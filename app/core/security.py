from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import logging

from app.config import settings
from app.database import redis_client

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


class PasswordManager:
    """Manage password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain password against hash"""
        return pwd_context.verify(plain_password, hashed_password)


class JWTManager:
    """Manage JWT token generation and validation"""
    
    @staticmethod
    def create_token(
        subject: str,
        additional_claims: Optional[Dict[str, Any]] = None,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create JWT token"""
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.jwt_expiration_hours)
        
        expire = datetime.utcnow() + expires_delta
        payload = {
            "sub": subject,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        try:
            encoded_jwt = jwt.encode(
                payload,
                settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm,
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Failed to create JWT token: {e}")
            raise
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """Verify JWT token and return claims"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm],
            )
            return payload
        except JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            raise
    
    @staticmethod
    def get_subject_from_token(token: str) -> str:
        """Extract subject (user ID) from token"""
        try:
            payload = JWTManager.verify_token(token)
            return payload.get("sub")
        except JWTError:
            return None


class OTPManager:
    """Manage OTP generation, storage, and verification"""
    
    @staticmethod
    def generate_otp() -> str:
        """Generate 6-digit OTP"""
        return str(secrets.randbelow(10 ** settings.otp_length)).zfill(settings.otp_length)
    
    @staticmethod
    def store_otp(email: str, otp: str) -> bool:
        """Store OTP in Redis with expiration"""
        try:
            key = f"otp:{email}"
            redis_client.setex(
                key,
                settings.otp_expiration_minutes * 60,
                otp,
            )
            logger.info(f"OTP stored for {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to store OTP: {e}")
            return False
    
    @staticmethod
    def verify_otp(email: str, otp: str) -> bool:
        """Verify OTP against stored value"""
        try:
            key = f"otp:{email}"
            stored_otp = redis_client.get(key)
            
            if not stored_otp:
                logger.warning(f"OTP not found or expired for {email}")
                return False
            
            if stored_otp != otp:
                logger.warning(f"OTP mismatch for {email}")
                return False
            
            # Delete OTP after verification
            redis_client.delete(key)
            logger.info(f"OTP verified and deleted for {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to verify OTP: {e}")
            return False
    
    @staticmethod
    def get_otp(email: str) -> Optional[str]:
        """Get OTP without verifying"""
        try:
            key = f"otp:{email}"
            return redis_client.get(key)
        except Exception as e:
            logger.error(f"Failed to get OTP: {e}")
            return None


class TokenBlacklist:
    """Manage JWT token blacklist for logout"""
    
    @staticmethod
    def blacklist_token(token: str, expiration_hours: int = settings.jwt_expiration_hours) -> bool:
        """Add token to blacklist"""
        try:
            key = f"blacklist:{token}"
            redis_client.setex(
                key,
                expiration_hours * 3600,
                "revoked",
            )
            logger.info("Token blacklisted")
            return True
        except Exception as e:
            logger.error(f"Failed to blacklist token: {e}")
            return False
    
    @staticmethod
    def is_token_blacklisted(token: str) -> bool:
        """Check if token is blacklisted"""
        try:
            key = f"blacklist:{token}"
            return redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {e}")
            return False


class PasswordResetTokenManager:
    """Manage password reset tokens"""
    
    @staticmethod
    def create_reset_token(email: str, expiration_hours: int = 1) -> str:
        """Create password reset token"""
        try:
            token = secrets.token_urlsafe(32)
            key = f"reset_token:{email}"
            redis_client.setex(
                key,
                expiration_hours * 3600,
                token,
            )
            logger.info(f"Reset token created for {email}")
            return token
        except Exception as e:
            logger.error(f"Failed to create reset token: {e}")
            raise
    
    @staticmethod
    def verify_reset_token(email: str, token: str) -> bool:
        """Verify password reset token"""
        try:
            key = f"reset_token:{email}"
            stored_token = redis_client.get(key)
            
            if not stored_token:
                logger.warning(f"Reset token not found or expired for {email}")
                return False
            
            if stored_token != token:
                logger.warning(f"Reset token mismatch for {email}")
                return False
            
            logger.info(f"Reset token verified for {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to verify reset token: {e}")
            return False
    
    @staticmethod
    def consume_reset_token(email: str) -> bool:
        """Delete reset token after use"""
        try:
            key = f"reset_token:{email}"
            redis_client.delete(key)
            logger.info(f"Reset token consumed for {email}")
            return True
        except Exception as e:
            logger.error(f"Failed to consume reset token: {e}")
            return False
