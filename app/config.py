from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings loaded from environment variables"""
    
    # Application
    app_name: str = "MealiFast API"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    db_driver: str = "mysql+pymysql"
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "mealifast"
    db_user: str = "mealifast_user"
    db_password: str = "password"
    db_pool_size: int = 20
    db_max_overflow: int = 0
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Email
    mail_from: str = "noreply@mealifast.com"
    mail_username: str = ""
    mail_password: str = ""
    mail_server: str = "smtp.gmail.com"
    mail_port: int = 587
    mail_tls: bool = True
    
    # Paystack
    paystack_secret_key: str = ""
    paystack_public_key: str = ""
    paystack_api_url: str = "https://api.paystack.co"
    
    # Security
    password_hash_algorithm: str = "bcrypt"
    otp_expiration_minutes: int = 10
    otp_length: int = 6
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"
    
    @property
    def database_url(self) -> str:
        """Generate database URL from components"""
        return (
            f"{self.db_driver}://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )
    
    @property
    def redis_async_url(self) -> str:
        """Generate async Redis URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export for convenience
settings = get_settings()
