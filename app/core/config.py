"""Configuration settings for the QR Code Reader Premium Platform."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings."""
    
    # App Configuration
    app_name: str = "QR Code Reader Premium"
    app_version: str = "2.0.0"
    debug: bool = False
    secret_key: str = "dev-key-change-in-production"
    environment: str = "development"
    
    # Database Configuration
    database_url: str = "sqlite:///./qr_reader.db"
    postgres_user: Optional[str] = None
    postgres_password: Optional[str] = None
    postgres_server: Optional[str] = None
    postgres_db: Optional[str] = None
    
    # Supabase Configuration
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # JWT Configuration
    jwt_secret_key: str = "jwt-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Email Configuration
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
    # Stripe Configuration
    stripe_secret_key: Optional[str] = None
    stripe_publishable_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # File Upload Configuration
    upload_folder: str = "uploads"
    max_file_size: int = 16 * 1024 * 1024  # 16MB
    allowed_extensions: str = "png,jpg,jpeg,gif,bmp,tiff"
    
    # Rate Limiting Configuration
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # CORS Configuration
    cors_origins: str = "*"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
    
    # Frontend Configuration
    react_app_api_url: str = "http://localhost:8000/api/v1"
    
    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info) -> str:
        """Assemble database URL from components if not provided directly."""
        if isinstance(v, str) and v.startswith("postgresql"):
            return v
        
        # Check for Supabase DATABASE_URL first
        supabase_db_url = os.getenv("DATABASE_URL")
        if supabase_db_url and supabase_db_url.startswith("postgresql"):
            return supabase_db_url
        
        # Check for PostgreSQL environment variables
        postgres_user = os.getenv("POSTGRES_USER")
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        postgres_server = os.getenv("POSTGRES_SERVER", "localhost")
        postgres_db = os.getenv("POSTGRES_DB", "qr_app")
        
        if postgres_user and postgres_password:
            return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}:5432/{postgres_db}"
        
        # Fallback to SQLite
        return v or "sqlite:///./qr_reader.db"
    
    model_config = {"env_file": ".env", "case_sensitive": False}


# Global settings instance
settings = Settings()
