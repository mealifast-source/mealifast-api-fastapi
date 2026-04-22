from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, verify_redis_connection, init_async_redis, close_async_redis
from app.api.v1 import auth, groups, meals, menus, orders, invoices, delivery, dashboard

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Lifespan event handlers
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting MealiFast API...")
    try:
        init_db()
        verify_redis_connection()
        await init_async_redis()
        logger.info("MealiFast API started successfully")
    except Exception as e:
        logger.error(f"Failed to start MealiFast API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down MealiFast API...")
    try:
        await close_async_redis()
        logger.info("MealiFast API shut down successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Corporate Meal Management and Group Ordering Platform",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


# API v1 endpoints
app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])
app.include_router(groups.router, prefix="/api/v1", tags=["Groups"])
app.include_router(meals.router, prefix="/api/v1", tags=["Meals"])
app.include_router(menus.router, prefix="/api/v1", tags=["Menus"])
app.include_router(orders.router, prefix="/api/v1", tags=["Orders"])
app.include_router(invoices.router, prefix="/api/v1", tags=["Invoices"])
app.include_router(delivery.router, prefix="/api/v1", tags=["Delivery"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
