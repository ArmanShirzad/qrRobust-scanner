"""Redis-based rate limiting service."""

import redis
import time
from typing import Optional, Dict, Any
from app.core.config import settings
from app.services.stripe_service import StripeService


class RateLimiter:
    """Redis-based rate limiter with tiered plans."""
    
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    
    def get_rate_limits(self, tier: str) -> Dict[str, int]:
        """Get rate limits for a subscription tier."""
        limits = {
            "free": {
                "per_minute": 10,
                "per_hour": 100,
                "per_day": 1000
            },
            "pro": {
                "per_minute": 60,
                "per_hour": 1000,
                "per_day": 10000
            },
            "business": {
                "per_minute": 120,
                "per_hour": 5000,
                "per_day": 50000
            },
            "enterprise": {
                "per_minute": 300,
                "per_hour": 20000,
                "per_day": 200000
            }
        }
        return limits.get(tier, limits["free"])
    
    def is_allowed(
        self, 
        identifier: str, 
        tier: str = "free",
        endpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check if request is allowed based on rate limits.
        
        Args:
            identifier: Unique identifier (user_id, ip_address, api_key)
            tier: Subscription tier
            endpoint: Optional endpoint-specific rate limiting
        
        Returns:
            Dict with 'allowed', 'remaining', 'reset_time', 'limit' info
        """
        limits = self.get_rate_limits(tier)
        current_time = int(time.time())
        
        # Create keys for different time windows
        minute_key = f"rate_limit:{identifier}:minute:{current_time // 60}"
        hour_key = f"rate_limit:{identifier}:hour:{current_time // 3600}"
        day_key = f"rate_limit:{identifier}:day:{current_time // 86400}"
        
        # Add endpoint-specific keys if provided
        if endpoint:
            minute_key += f":{endpoint}"
            hour_key += f":{endpoint}"
            day_key += f":{endpoint}"
        
        # Check minute limit
        minute_count = self.redis_client.get(minute_key)
        if minute_count is None:
            minute_count = 0
        else:
            minute_count = int(minute_count)
        
        if minute_count >= limits["per_minute"]:
            return {
                "allowed": False,
                "limit_type": "minute",
                "limit": limits["per_minute"],
                "remaining": 0,
                "reset_time": ((current_time // 60) + 1) * 60,
                "retry_after": ((current_time // 60) + 1) * 60 - current_time
            }
        
        # Check hour limit
        hour_count = self.redis_client.get(hour_key)
        if hour_count is None:
            hour_count = 0
        else:
            hour_count = int(hour_count)
        
        if hour_count >= limits["per_hour"]:
            return {
                "allowed": False,
                "limit_type": "hour",
                "limit": limits["per_hour"],
                "remaining": 0,
                "reset_time": ((current_time // 3600) + 1) * 3600,
                "retry_after": ((current_time // 3600) + 1) * 3600 - current_time
            }
        
        # Check day limit
        day_count = self.redis_client.get(day_key)
        if day_count is None:
            day_count = 0
        else:
            day_count = int(day_count)
        
        if day_count >= limits["per_day"]:
            return {
                "allowed": False,
                "limit_type": "day",
                "limit": limits["per_day"],
                "remaining": 0,
                "reset_time": ((current_time // 86400) + 1) * 86400,
                "retry_after": ((current_time // 86400) + 1) * 86400 - current_time
            }
        
        # Increment counters
        pipe = self.redis_client.pipeline()
        
        # Minute counter (expires in 60 seconds)
        pipe.incr(minute_key)
        pipe.expire(minute_key, 60)
        
        # Hour counter (expires in 3600 seconds)
        pipe.incr(hour_key)
        pipe.expire(hour_key, 3600)
        
        # Day counter (expires in 86400 seconds)
        pipe.incr(day_key)
        pipe.expire(day_key, 86400)
        
        pipe.execute()
        
        # Calculate remaining requests
        remaining_minute = limits["per_minute"] - (minute_count + 1)
        remaining_hour = limits["per_hour"] - (hour_count + 1)
        remaining_day = limits["per_day"] - (day_count + 1)
        
        return {
            "allowed": True,
            "limit_type": "minute",
            "limit": limits["per_minute"],
            "remaining": min(remaining_minute, remaining_hour, remaining_day),
            "reset_time": ((current_time // 60) + 1) * 60,
            "retry_after": None,
            "counts": {
                "minute": minute_count + 1,
                "hour": hour_count + 1,
                "day": day_count + 1
            }
        }
    
    def get_usage_stats(self, identifier: str, tier: str = "free") -> Dict[str, Any]:
        """Get current usage statistics for an identifier."""
        limits = self.get_rate_limits(tier)
        current_time = int(time.time())
        
        # Get current counts
        minute_key = f"rate_limit:{identifier}:minute:{current_time // 60}"
        hour_key = f"rate_limit:{identifier}:hour:{current_time // 3600}"
        day_key = f"rate_limit:{identifier}:day:{current_time // 86400}"
        
        minute_count = int(self.redis_client.get(minute_key) or 0)
        hour_count = int(self.redis_client.get(hour_key) or 0)
        day_count = int(self.redis_client.get(day_key) or 0)
        
        return {
            "tier": tier,
            "limits": limits,
            "current_usage": {
                "minute": minute_count,
                "hour": hour_count,
                "day": day_count
            },
            "remaining": {
                "minute": max(0, limits["per_minute"] - minute_count),
                "hour": max(0, limits["per_hour"] - hour_count),
                "day": max(0, limits["per_day"] - day_count)
            },
            "reset_times": {
                "minute": ((current_time // 60) + 1) * 60,
                "hour": ((current_time // 3600) + 1) * 3600,
                "day": ((current_time // 86400) + 1) * 86400
            }
        }
    
    def reset_limits(self, identifier: str) -> bool:
        """Reset rate limits for an identifier (admin function)."""
        try:
            # Get all keys matching the identifier pattern
            pattern = f"rate_limit:{identifier}:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
            
            return True
        except Exception:
            return False
    
    def is_redis_available(self) -> bool:
        """Check if Redis is available."""
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False


# Global rate limiter instance
rate_limiter = RateLimiter()
