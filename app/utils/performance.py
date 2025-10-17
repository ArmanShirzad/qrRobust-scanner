# Performance Monitoring and Optimization

import time
import asyncio
from functools import wraps
from typing import Callable, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to monitor and log request performance."""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        # Add performance headers
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log slow requests
        if process_time > 1.0:  # Log requests taking more than 1 second
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {process_time:.3f}s"
            )
        
        return response


def cache_result(ttl: int = 300):
    """Decorator to cache function results for specified TTL."""
    def decorator(func: Callable) -> Callable:
        cache = {}
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from arguments
            cache_key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"
            
            # Check if cached result exists and is still valid
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < ttl:
                    return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator


def async_timeout(seconds: int = 30):
    """Decorator to add timeout to async functions."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                logger.error(f"Function {func.__name__} timed out after {seconds}s")
                raise
            
        return wrapper
    return decorator


class DatabaseConnectionPool:
    """Simple connection pool for database optimization."""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = asyncio.Queue(maxsize=max_connections)
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Initialize connection pool."""
        # This would be implemented with actual database connections
        pass
    
    async def get_connection(self):
        """Get a connection from the pool."""
        return await self.connections.get()
    
    async def return_connection(self, connection):
        """Return a connection to the pool."""
        await self.connections.put(connection)


# Global connection pool instance
db_pool = DatabaseConnectionPool()


def optimize_query(query_func: Callable) -> Callable:
    """Decorator to optimize database queries."""
    @wraps(query_func)
    async def wrapper(*args, **kwargs):
        # Add query optimization logic here
        # For example: query caching, connection pooling, etc.
        return await query_func(*args, **kwargs)
    
    return wrapper
