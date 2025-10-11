"""Database models for the QR Code Reader Premium Platform."""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """User model for authentication and subscription management."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    tier = Column(String(50), default="free")  # free, pro, business, enterprise
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    qr_scans = relationship("QRScan", back_populates="user")
    qr_codes = relationship("QRCode", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")


class QRScan(Base):
    """QR Code scan records for analytics."""
    __tablename__ = "qr_scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for anonymous scans
    content = Column(Text, nullable=False)
    filename = Column(String(255))
    file_size = Column(Integer)
    scan_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Analytics metadata
    ip_address = Column(String(45))  # IPv6 compatible
    user_agent = Column(Text)
    referer = Column(String(500))
    country = Column(String(2))  # ISO country code
    device_type = Column(String(50))  # mobile, desktop, tablet
    browser = Column(String(100))
    
    # Relationships
    user = relationship("User", back_populates="qr_scans")


class QRCode(Base):
    """Generated QR codes with analytics."""
    __tablename__ = "qr_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    short_url = Column(String(100), unique=True, index=True)
    destination_url = Column(Text, nullable=False)
    title = Column(String(255))
    description = Column(Text)
    
    # QR Code properties
    error_correction_level = Column(String(10), default="M")  # L, M, Q, H
    size = Column(Integer, default=10)
    border = Column(Integer, default=4)
    
    # Customization
    foreground_color = Column(String(7), default="#000000")  # Hex color
    background_color = Column(String(7), default="#FFFFFF")  # Hex color
    logo_url = Column(String(500))
    
    # Analytics
    scan_count = Column(Integer, default=0)
    last_scanned_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="qr_codes")


class Subscription(Base):
    """User subscription and billing information."""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stripe_customer_id = Column(String(255), unique=True, index=True)
    stripe_subscription_id = Column(String(255), unique=True, index=True)
    tier = Column(String(50), nullable=False)  # pro, business, enterprise
    status = Column(String(50), nullable=False)  # active, canceled, past_due, etc.
    
    # Billing
    current_period_start = Column(DateTime(timezone=True))
    current_period_end = Column(DateTime(timezone=True))
    cancel_at_period_end = Column(Boolean, default=False)
    
    # Usage tracking
    monthly_scan_limit = Column(Integer, nullable=False)
    scans_used_this_month = Column(Integer, default=0)
    last_reset_date = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")


class APIKey(Base):
    """API keys for developer access."""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key_hash = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    rate_limit_per_minute = Column(Integer, default=60)
    rate_limit_per_hour = Column(Integer, default=1000)
    
    # Usage tracking
    requests_this_minute = Column(Integer, default=0)
    requests_this_hour = Column(Integer, default=0)
    last_request_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    expires_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")


class QRCodeAnalytics(Base):
    """Detailed analytics for QR code scans."""
    __tablename__ = "qr_code_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    qr_code_id = Column(Integer, ForeignKey("qr_codes.id"), nullable=False)
    scan_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Location data
    ip_address = Column(String(45))
    country = Column(String(2))
    region = Column(String(100))
    city = Column(String(100))
    
    # Device and browser info
    user_agent = Column(Text)
    device_type = Column(String(50))
    browser = Column(String(100))
    os = Column(String(100))
    
    # Referral data
    referer = Column(String(500))
    utm_source = Column(String(100))
    utm_medium = Column(String(100))
    utm_campaign = Column(String(100))
    
    # Additional metadata
    scan_metadata = Column(JSON)  # For storing additional custom data
