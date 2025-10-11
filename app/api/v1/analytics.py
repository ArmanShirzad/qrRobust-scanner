"""Analytics endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.models import QRScan, User, QRCode, QRCodeAnalytics
from app.utils.dependencies import get_current_user
from app.schemas.analytics import (
    ScanStats, DashboardStats, ScanHistory, 
    TopQRCode, DeviceStats, LocationStats
)

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get dashboard statistics for the current user."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total scans in period
    total_scans = db.query(QRScan).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date
    ).count()
    
    # Scans today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = db.query(QRScan).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= today_start
    ).count()
    
    # Unique QR codes scanned
    unique_qr_codes = db.query(QRScan.content).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date
    ).distinct().count()
    
    # Top QR codes
    top_qr_codes = db.query(
        QRScan.content,
        func.count(QRScan.id).label('scan_count')
    ).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date
    ).group_by(QRScan.content).order_by(desc('scan_count')).limit(5).all()
    
    top_qr_list = [
        TopQRCode(content=qr.content, scan_count=qr.scan_count)
        for qr in top_qr_codes
    ]
    
    # Device breakdown
    device_stats = db.query(
        QRScan.device_type,
        func.count(QRScan.id).label('count')
    ).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date,
        QRScan.device_type.isnot(None)
    ).group_by(QRScan.device_type).all()
    
    device_list = [
        DeviceStats(device_type=device.device_type, count=device.count)
        for device in device_stats
    ]
    
    return DashboardStats(
        total_scans=total_scans,
        scans_today=scans_today,
        unique_qr_codes=unique_qr_codes,
        top_qr_codes=top_qr_list,
        device_stats=device_list,
        period_days=days
    )


@router.get("/scans", response_model=List[ScanHistory])
async def get_scan_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    days: int = Query(30, ge=1, le=365)
):
    """Get scan history for the current user."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    scans = db.query(QRScan).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date
    ).order_by(desc(QRScan.scan_timestamp)).offset(offset).limit(limit).all()
    
    return [
        ScanHistory(
            id=scan.id,
            content=scan.content,
            filename=scan.filename,
            scan_timestamp=scan.scan_timestamp,
            device_type=scan.device_type,
            browser=scan.browser,
            country=scan.country
        )
        for scan in scans
    ]


@router.get("/stats", response_model=ScanStats)
async def get_scan_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get detailed scan statistics."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total scans
    total_scans = db.query(QRScan).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date
    ).count()
    
    # Scans by day (last 7 days)
    daily_scans = []
    for i in range(7):
        day_start = (end_date - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_count = db.query(QRScan).filter(
            QRScan.user_id == current_user.id,
            QRScan.scan_timestamp >= day_start,
            QRScan.scan_timestamp < day_end
        ).count()
        
        daily_scans.append({
            "date": day_start.date().isoformat(),
            "count": day_count
        })
    
    # Browser breakdown
    browser_stats = db.query(
        QRScan.browser,
        func.count(QRScan.id).label('count')
    ).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date,
        QRScan.browser.isnot(None)
    ).group_by(QRScan.browser).all()
    
    # Country breakdown
    country_stats = db.query(
        QRScan.country,
        func.count(QRScan.id).label('count')
    ).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date,
        QRScan.country.isnot(None)
    ).group_by(QRScan.country).all()
    
    return ScanStats(
        total_scans=total_scans,
        daily_scans=daily_scans,
        browser_stats=[{"browser": b.browser, "count": b.count} for b in browser_stats],
        country_stats=[{"country": c.country, "count": c.count} for c in country_stats],
        period_days=days
    )


@router.get("/export")
async def export_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365),
    format: str = Query("json", regex="^(json|csv)$")
):
    """Export analytics data."""
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    scans = db.query(QRScan).filter(
        QRScan.user_id == current_user.id,
        QRScan.scan_timestamp >= start_date,
        QRScan.scan_timestamp <= end_date
    ).order_by(desc(QRScan.scan_timestamp)).all()
    
    if format == "csv":
        # TODO: Implement CSV export
        return {"message": "CSV export not yet implemented"}
    
    # JSON export
    export_data = [
        {
            "id": scan.id,
            "content": scan.content,
            "filename": scan.filename,
            "scan_timestamp": scan.scan_timestamp.isoformat(),
            "device_type": scan.device_type,
            "browser": scan.browser,
            "country": scan.country,
            "ip_address": scan.ip_address,
            "user_agent": scan.user_agent,
            "referer": scan.referer
        }
        for scan in scans
    ]
    
    return {
        "format": "json",
        "total_records": len(export_data),
        "period_days": days,
        "data": export_data
    }
