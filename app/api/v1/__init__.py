"""Main API router for v1 endpoints."""

from fastapi import APIRouter
from app.api.v1.qr import router as qr_router
from app.api.v1.auth import router as auth_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.qr_codes import router as qr_codes_router
from app.api.v1.rate_limits import router as rate_limits_router
from app.api.v1.qr_designer import router as qr_designer_router

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(qr_router, prefix="/qr", tags=["QR Code Processing"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(subscriptions_router, prefix="/subscriptions", tags=["Subscriptions"])
api_router.include_router(qr_codes_router, prefix="/qr-codes", tags=["QR Code Management"])
api_router.include_router(rate_limits_router, prefix="/rate-limits", tags=["Rate Limiting"])
api_router.include_router(qr_designer_router, prefix="/qr-designer", tags=["QR Code Designer"])
