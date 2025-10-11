"""Rate limiting middleware for FastAPI."""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import time

from app.services.rate_limiter import rate_limiter
from app.utils.dependencies import get_optional_current_user
from app.models import User


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests."""
    
    def __init__(self, app, excluded_paths: Optional[list] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc", 
            "/openapi.json",
            "/health",
            "/favicon.ico"
        ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Skip rate limiting for non-API paths
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
        
        # Check if Redis is available
        if not rate_limiter.is_redis_available():
            # If Redis is not available, allow the request but add warning headers
            print("Warning: Redis not available, skipping rate limiting")
            response = await call_next(request)
            response.headers["X-RateLimit-Status"] = "disabled"
            response.headers["X-RateLimit-Reason"] = "redis-unavailable"
            return response
        
        # Get identifier for rate limiting
        identifier = await self._get_identifier(request)
        if not identifier:
            return await call_next(request)
        
        # Get user tier for rate limiting
        tier = await self._get_user_tier(request)
        
        # Check rate limits
        rate_result = rate_limiter.is_allowed(identifier, tier, request.url.path)
        
        if not rate_result["allowed"]:
            # Rate limit exceeded
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {rate_result['limit']} requests per {rate_result['limit_type']}",
                    "retry_after": rate_result["retry_after"],
                    "reset_time": rate_result["reset_time"]
                }
            )
            
            # Add rate limit headers
            response.headers["X-RateLimit-Limit"] = str(rate_result["limit"])
            response.headers["X-RateLimit-Remaining"] = str(rate_result["remaining"])
            response.headers["X-RateLimit-Reset"] = str(rate_result["reset_time"])
            response.headers["Retry-After"] = str(rate_result["retry_after"])
            
            return response
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        response.headers["X-RateLimit-Limit"] = str(rate_result["limit"])
        response.headers["X-RateLimit-Remaining"] = str(rate_result["remaining"])
        response.headers["X-RateLimit-Reset"] = str(rate_result["reset_time"])
        
        if "counts" in rate_result:
            response.headers["X-RateLimit-Count-Minute"] = str(rate_result["counts"]["minute"])
            response.headers["X-RateLimit-Count-Hour"] = str(rate_result["counts"]["hour"])
            response.headers["X-RateLimit-Count-Day"] = str(rate_result["counts"]["day"])
        
        return response
    
    async def _get_identifier(self, request: Request) -> Optional[str]:
        """Get unique identifier for rate limiting."""
        # Try to get user ID from JWT token first
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from app.utils.auth import get_user_id_from_token
                token = auth_header.split(" ")[1]
                user_id = get_user_id_from_token(token)
                return f"user:{user_id}"
        except Exception:
            pass
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def _get_user_tier(self, request: Request) -> str:
        """Get user subscription tier for rate limiting."""
        try:
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from app.utils.auth import get_user_id_from_token
                from app.database import SessionLocal
                from app.models import User
                
                token = auth_header.split(" ")[1]
                user_id = get_user_id_from_token(token)
                
                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.id == user_id).first()
                    if user:
                        return user.tier
                finally:
                    db.close()
        except Exception:
            pass
        
        # Default to free tier
        return "free"
