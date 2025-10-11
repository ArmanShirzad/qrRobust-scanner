"""Pydantic schemas for analytics."""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class TopQRCode(BaseModel):
    """Schema for top QR code statistics."""
    content: str
    scan_count: int


class DeviceStats(BaseModel):
    """Schema for device statistics."""
    device_type: str
    count: int


class LocationStats(BaseModel):
    """Schema for location statistics."""
    country: str
    count: int


class DashboardStats(BaseModel):
    """Schema for dashboard statistics."""
    total_scans: int
    scans_today: int
    unique_qr_codes: int
    top_qr_codes: List[TopQRCode]
    device_stats: List[DeviceStats]
    period_days: int


class ScanHistory(BaseModel):
    """Schema for scan history."""
    id: int
    content: str
    filename: Optional[str]
    scan_timestamp: datetime
    device_type: Optional[str]
    browser: Optional[str]
    country: Optional[str]


class ScanStats(BaseModel):
    """Schema for detailed scan statistics."""
    total_scans: int
    daily_scans: List[Dict[str, Any]]
    browser_stats: List[Dict[str, Any]]
    country_stats: List[Dict[str, Any]]
    period_days: int


class AnalyticsExport(BaseModel):
    """Schema for analytics export."""
    format: str
    total_records: int
    period_days: int
    data: List[Dict[str, Any]]
