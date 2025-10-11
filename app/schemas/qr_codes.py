"""Pydantic schemas for QR code generation and management."""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


class QRCodeCreate(BaseModel):
    """Schema for creating a QR code."""
    destination_url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    error_correction_level: str = "M"  # L, M, Q, H
    size: int = 10
    border: int = 4
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"
    logo_url: Optional[str] = None
    expires_at: Optional[datetime] = None


class QRCodeUpdate(BaseModel):
    """Schema for updating a QR code."""
    title: Optional[str] = None
    description: Optional[str] = None
    destination_url: Optional[HttpUrl] = None
    foreground_color: Optional[str] = None
    background_color: Optional[str] = None
    logo_url: Optional[str] = None
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class QRCodeResponse(BaseModel):
    """Schema for QR code response."""
    id: int
    user_id: int
    short_url: str
    destination_url: str
    title: Optional[str]
    description: Optional[str]
    error_correction_level: str
    size: int
    border: int
    foreground_color: str
    background_color: str
    logo_url: Optional[str]
    scan_count: int
    last_scanned_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    expires_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class QRCodeGenerate(BaseModel):
    """Schema for generating QR code image."""
    data: str
    size: int = 10
    border: int = 4
    error_correction: str = "M"
    foreground_color: str = "#000000"
    background_color: str = "#FFFFFF"
    logo_path: Optional[str] = None


class QRCodeImage(BaseModel):
    """Schema for QR code image response."""
    image_base64: str
    qr_data: str
    image_info: Dict[str, Any]


class QRCodeInfo(BaseModel):
    """Schema for QR code information."""
    length: int
    is_url: bool
    estimated_version: int
    max_capacity: int
    domain: Optional[str] = None
    scheme: Optional[str] = None
    path: Optional[str] = None


class QRCodeStats(BaseModel):
    """Schema for QR code statistics."""
    total_qr_codes: int
    active_qr_codes: int
    total_scans: int
    scans_today: int
    top_performing: List[Dict[str, Any]]


class QRCodeBulkCreate(BaseModel):
    """Schema for bulk QR code creation."""
    qr_codes: List[QRCodeCreate]
    batch_name: Optional[str] = None


class QRCodeBulkResponse(BaseModel):
    """Schema for bulk QR code response."""
    batch_id: str
    total_created: int
    failed: int
    qr_codes: List[QRCodeResponse]
    errors: List[Dict[str, Any]]
