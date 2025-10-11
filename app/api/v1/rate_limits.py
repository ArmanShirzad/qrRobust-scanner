"""Rate limiting endpoints for users to check their usage."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.models import User
from app.utils.dependencies import get_current_user
from app.services.rate_limiter import rate_limiter

router = APIRouter()


@router.get("/usage", response_model=Dict[str, Any])
async def get_rate_limit_usage(
    current_user: User = Depends(get_current_user)
):
    """Get current rate limit usage for the authenticated user."""
    
    if not rate_limiter.is_redis_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiting service is currently unavailable"
        )
    
    identifier = f"user:{current_user.id}"
    usage_stats = rate_limiter.get_usage_stats(identifier, current_user.tier)
    
    return {
        "user_id": current_user.id,
        "tier": current_user.tier,
        "usage_stats": usage_stats
    }


@router.get("/limits", response_model=Dict[str, Any])
async def get_rate_limits(
    current_user: User = Depends(get_current_user)
):
    """Get rate limits for the user's subscription tier."""
    
    limits = rate_limiter.get_rate_limits(current_user.tier)
    
    return {
        "tier": current_user.tier,
        "limits": limits,
        "description": _get_tier_description(current_user.tier)
    }


@router.post("/reset")
async def reset_rate_limits(
    current_user: User = Depends(get_current_user)
):
    """Reset rate limits for the current user (admin function)."""
    
    # Only allow admins or users with enterprise tier to reset limits
    if current_user.tier not in ["enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only enterprise users can reset rate limits"
        )
    
    if not rate_limiter.is_redis_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Rate limiting service is currently unavailable"
        )
    
    identifier = f"user:{current_user.id}"
    success = rate_limiter.reset_limits(identifier)
    
    if success:
        return {"message": "Rate limits reset successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset rate limits"
        )


@router.get("/status")
async def get_rate_limit_status():
    """Get rate limiting service status."""
    
    redis_available = rate_limiter.is_redis_available()
    
    return {
        "service_status": "available" if redis_available else "unavailable",
        "redis_connected": redis_available,
        "message": "Rate limiting service is operational" if redis_available else "Rate limiting service is down"
    }


def _get_tier_description(tier: str) -> str:
    """Get description for subscription tier."""
    descriptions = {
        "free": "Free tier with basic rate limits for personal use",
        "pro": "Pro tier with increased limits for professionals",
        "business": "Business tier with high limits for growing businesses",
        "enterprise": "Enterprise tier with maximum limits and priority support"
    }
    return descriptions.get(tier, "Unknown tier")
