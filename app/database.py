from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import redis
from typing import AsyncGenerator, Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Database configuration
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    poolclass=QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,  # Test connections before using
    pool_recycle=3600,   # Recycle connections every hour
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)

# Base for models
Base = declarative_base()

# Redis synchronous client
redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_keepalive=True,
)

# Async Redis client
async_redis_client = None


async def init_async_redis():
    """Initialize async Redis connection"""
    global async_redis_client
    try:
        async_redis_client = redis.from_url(
            settings.redis_async_url,
            decode_responses=True,
        )
        logger.info("Async Redis connected")
    except Exception as e:
        logger.error(f"Failed to connect async Redis: {e}")
        raise


async def close_async_redis():
    """Close async Redis connection"""
    global async_redis_client
    if async_redis_client:
        await async_redis_client.close()
        logger.info("Async Redis disconnected")


def get_db() -> Generator[Session, None, None]:
    """Get database session for dependency injection"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database, create tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def verify_redis_connection():
    """Verify Redis connection"""
    try:
        redis_client.ping()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
