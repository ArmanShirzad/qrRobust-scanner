"""Main FastAPI application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

from app.core.config import settings
from app.api.v1 import api_router
from app.middleware.rate_limit import RateLimitMiddleware

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Premium QR Code Reader Platform with Analytics and API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Create upload directory
os.makedirs(settings.upload_folder, exist_ok=True)

# Static files and templates are handled by Vercel routing

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Serve the React frontend."""
    # In Vercel, the frontend will be served by the static build
    # This endpoint should not be reached due to routing configuration
    return {"message": "API is running", "frontend": "served by Vercel static build"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
