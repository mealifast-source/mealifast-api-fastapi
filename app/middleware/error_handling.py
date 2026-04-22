import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from datetime import datetime
import json

from app.core.exceptions import MealiFastException
from app.utils.response import error_response

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except MealiFastException as e:
            logger.warning(f"MealiFast exception: {e.message}")
            return JSONResponse(
                status_code=e.status_code,
                content=error_response(e.message, e.error_code, e.details),
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content=error_response(
                    "Internal server error",
                    "500",
                    {"error": str(e)},
                ),
            )


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for audit logging of all requests"""

    async def dispatch(self, request: Request, call_next):
        # Get request info
        method = request.method
        path = request.url.path
        query_params = dict(request.query_params)
        
        # Get user info from JWT if available
        user_id = None
        try:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                from app.core.security import JWTManager
                
                token = auth_header.split(" ")[1]
                jwt_manager = JWTManager()
                user_id = jwt_manager.get_subject_from_token(token)
        except Exception:
            pass
        
        # Log request
        logger.info(
            f"Request: {method} {path} | User: {user_id} | QueryParams: {query_params}"
        )
        
        # Process request
        response = await call_next(request)
        
        # Log response
        logger.info(f"Response: {method} {path} | Status: {response.status_code}")
        
        return response


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all responses"""

    async def dispatch(self, request: Request, call_next):
        import uuid
        
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        
        return response
