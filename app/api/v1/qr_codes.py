"""QR Code generation and management endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import User, QRCode, QRCodeAnalytics
from app.utils.dependencies import get_current_user, get_optional_current_user
from app.schemas.qr_codes import (
    QRCodeCreate, QRCodeUpdate, QRCodeResponse, QRCodeGenerate,
    QRCodeImage, QRCodeInfo, QRCodeStats, QRCodeBulkCreate, QRCodeBulkResponse
)
from app.services.qr_generator import QRCodeGenerator

router = APIRouter()


@router.post("/generate", response_model=QRCodeImage)
async def generate_qr_code(
    qr_data: QRCodeGenerate,
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Generate a QR code image from data."""
    
    # Validate QR code data
    is_valid, error_msg = QRCodeGenerator.validate_qr_data(qr_data.data)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    try:
        # Generate QR code
        image_base64 = QRCodeGenerator.generate_qr_base64(
            data=qr_data.data,
            size=qr_data.size,
            border=qr_data.border,
            error_correction=qr_data.error_correction,
            foreground_color=qr_data.foreground_color,
            background_color=qr_data.background_color,
            logo_path=qr_data.logo_path
        )
        
        # Get QR code info
        qr_info = QRCodeGenerator.get_qr_info(qr_data.data)
        
        return QRCodeImage(
            image_base64=image_base64,
            qr_data=qr_data.data,
            image_info=qr_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate QR code: {str(e)}"
        )


@router.get("/info", response_model=QRCodeInfo)
async def get_qr_info(data: str = Query(..., description="QR code data to analyze")):
    """Get information about QR code data."""
    
    is_valid, error_msg = QRCodeGenerator.validate_qr_data(data)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    qr_info = QRCodeGenerator.get_qr_info(data)
    return QRCodeInfo(**qr_info)


@router.post("/create", response_model=QRCodeResponse)
async def create_qr_code(
    qr_data: QRCodeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a dynamic QR code with tracking."""
    
    # Generate short URL
    short_url = QRCodeGenerator.generate_short_url()
    
    # Create QR code record
    db_qr_code = QRCode(
        user_id=current_user.id,
        short_url=short_url,
        destination_url=str(qr_data.destination_url),
        title=qr_data.title,
        description=qr_data.description,
        error_correction_level=qr_data.error_correction_level,
        size=qr_data.size,
        border=qr_data.border,
        foreground_color=qr_data.foreground_color,
        background_color=qr_data.background_color,
        logo_url=qr_data.logo_url,
        expires_at=qr_data.expires_at,
        scan_count=0,
        is_active=True
    )
    
    db.add(db_qr_code)
    db.commit()
    db.refresh(db_qr_code)
    
    return db_qr_code


@router.get("/my-codes", response_model=List[QRCodeResponse])
async def get_my_qr_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    active_only: bool = Query(False)
):
    """Get user's QR codes."""
    
    query = db.query(QRCode).filter(QRCode.user_id == current_user.id)
    
    if active_only:
        query = query.filter(QRCode.is_active == True)
    
    qr_codes = query.order_by(QRCode.created_at.desc()).offset(offset).limit(limit).all()
    
    return qr_codes


@router.get("/{qr_code_id}", response_model=QRCodeResponse)
async def get_qr_code(
    qr_code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific QR code."""
    
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_code_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    return qr_code


@router.put("/{qr_code_id}", response_model=QRCodeResponse)
async def update_qr_code(
    qr_code_id: int,
    qr_update: QRCodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a QR code."""
    
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_code_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    # Update fields
    update_data = qr_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(qr_code, field, value)
    
    qr_code.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(qr_code)
    
    return qr_code


@router.delete("/{qr_code_id}")
async def delete_qr_code(
    qr_code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a QR code."""
    
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_code_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    db.delete(qr_code)
    db.commit()
    
    return {"message": "QR code deleted successfully"}


@router.get("/{qr_code_id}/image", response_model=QRCodeImage)
async def get_qr_code_image(
    qr_code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get QR code image."""
    
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_code_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    try:
        # Generate QR code image
        image_base64 = QRCodeGenerator.generate_qr_base64(
            data=qr_code.short_url,
            size=qr_code.size,
            border=qr_code.border,
            error_correction=qr_code.error_correction_level,
            foreground_color=qr_code.foreground_color,
            background_color=qr_code.background_color,
            logo_path=qr_code.logo_url
        )
        
        qr_info = QRCodeGenerator.get_qr_info(qr_code.short_url)
        
        return QRCodeImage(
            image_base64=image_base64,
            qr_data=qr_code.short_url,
            image_info=qr_info
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate QR code image: {str(e)}"
        )


@router.get("/{qr_code_id}/stats")
async def get_qr_code_stats(
    qr_code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    days: int = Query(30, ge=1, le=365)
):
    """Get QR code statistics."""
    
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_code_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get analytics data
    analytics = db.query(QRCodeAnalytics).filter(
        QRCodeAnalytics.qr_code_id == qr_code_id,
        QRCodeAnalytics.scan_timestamp >= start_date,
        QRCodeAnalytics.scan_timestamp <= end_date
    ).all()
    
    # Process analytics data
    total_scans = len(analytics)
    scans_today = len([a for a in analytics if a.scan_timestamp.date() == datetime.utcnow().date()])
    
    # Device breakdown
    device_stats = {}
    browser_stats = {}
    country_stats = {}
    
    for analytic in analytics:
        if analytic.device_type:
            device_stats[analytic.device_type] = device_stats.get(analytic.device_type, 0) + 1
        if analytic.browser:
            browser_stats[analytic.browser] = browser_stats.get(analytic.browser, 0) + 1
        if analytic.country:
            country_stats[analytic.country] = country_stats.get(analytic.country, 0) + 1
    
    return {
        "qr_code_id": qr_code_id,
        "total_scans": total_scans,
        "scans_today": scans_today,
        "period_days": days,
        "device_stats": device_stats,
        "browser_stats": browser_stats,
        "country_stats": country_stats,
        "last_scanned_at": qr_code.last_scanned_at
    }


@router.post("/bulk-create", response_model=QRCodeBulkResponse)
async def bulk_create_qr_codes(
    bulk_data: QRCodeBulkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create multiple QR codes in bulk."""
    
    batch_id = str(uuid.uuid4())
    created_qr_codes = []
    errors = []
    
    for i, qr_data in enumerate(bulk_data.qr_codes):
        try:
            # Generate short URL
            short_url = QRCodeGenerator.generate_short_url()
            
            # Create QR code record
            db_qr_code = QRCode(
                user_id=current_user.id,
                short_url=short_url,
                destination_url=str(qr_data.destination_url),
                title=qr_data.title,
                description=qr_data.description,
                error_correction_level=qr_data.error_correction_level,
                size=qr_data.size,
                border=qr_data.border,
                foreground_color=qr_data.foreground_color,
                background_color=qr_data.background_color,
                logo_url=qr_data.logo_url,
                expires_at=qr_data.expires_at,
                scan_count=0,
                is_active=True
            )
            
            db.add(db_qr_code)
            db.commit()
            db.refresh(db_qr_code)
            
            created_qr_codes.append(db_qr_code)
            
        except Exception as e:
            errors.append({
                "index": i,
                "error": str(e),
                "data": qr_data.dict()
            })
    
    return QRCodeBulkResponse(
        batch_id=batch_id,
        total_created=len(created_qr_codes),
        failed=len(errors),
        qr_codes=created_qr_codes,
        errors=errors
    )


@router.get("/stats/overview", response_model=QRCodeStats)
async def get_qr_codes_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overview statistics for user's QR codes."""
    
    # Total QR codes
    total_qr_codes = db.query(QRCode).filter(QRCode.user_id == current_user.id).count()
    
    # Active QR codes
    active_qr_codes = db.query(QRCode).filter(
        QRCode.user_id == current_user.id,
        QRCode.is_active == True
    ).count()
    
    # Total scans
    total_scans = db.query(QRCode).filter(QRCode.user_id == current_user.id).with_entities(
        db.func.sum(QRCode.scan_count)
    ).scalar() or 0
    
    # Scans today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = db.query(QRCodeAnalytics).join(QRCode).filter(
        QRCode.user_id == current_user.id,
        QRCodeAnalytics.scan_timestamp >= today_start
    ).count()
    
    # Top performing QR codes
    top_performing = db.query(QRCode).filter(
        QRCode.user_id == current_user.id
    ).order_by(QRCode.scan_count.desc()).limit(5).all()
    
    top_performing_data = [
        {
            "id": qr.id,
            "title": qr.title,
            "scan_count": qr.scan_count,
            "short_url": qr.short_url
        }
        for qr in top_performing
    ]
    
    return QRCodeStats(
        total_qr_codes=total_qr_codes,
        active_qr_codes=active_qr_codes,
        total_scans=total_scans,
        scans_today=scans_today,
        top_performing=top_performing_data
    )


@router.post("/bulk-generate", response_model=List[QRCodeResponse])
async def bulk_generate_qr_codes(
    qr_data_list: List[QRCodeGenerate],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate multiple QR codes in bulk."""
    
    if len(qr_data_list) > 100:  # Limit bulk size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many QR codes. Maximum bulk size is 100 QR codes."
        )
    
    created_qr_codes = []
    
    try:
        for qr_data in qr_data_list:
            # Generate QR code
            qr_result = QRCodeGenerator.generate_qr_base64(
                data=qr_data.data,
                size=qr_data.size,
                border=qr_data.border,
                error_correction=qr_data.error_correction_level,
                foreground_color=qr_data.foreground_color,
                background_color=qr_data.background_color,
                logo_path=qr_data.logo_url
            )
            
            if not qr_result["success"]:
                continue  # Skip failed QR codes
            
            # Create QR code record
            qr_code = QRCode(
                user_id=current_user.id,
                name=qr_data.name,
                data=qr_data.data,
                qr_type=qr_data.qr_type,
                size=qr_data.size,
                border=qr_data.border,
                error_correction_level=qr_data.error_correction_level,
                foreground_color=qr_data.foreground_color,
                background_color=qr_data.background_color,
                logo_url=qr_data.logo_url,
                short_url=qr_result["short_url"],
                scan_count=0,
                is_active=True
            )
            
            db.add(qr_code)
            db.commit()
            db.refresh(qr_code)
            
            created_qr_codes.append(qr_code)
        
        return created_qr_codes
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk generation error: {str(e)}"
        )


@router.post("/bulk-update/{qr_code_id}", response_model=QRCodeResponse)
async def bulk_update_qr_codes(
    qr_code_ids: List[int],
    qr_data: QRCodeUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update multiple QR codes in bulk."""
    
    if len(qr_code_ids) > 50:  # Limit bulk size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many QR codes. Maximum bulk update size is 50 QR codes."
        )
    
    updated_qr_codes = []
    
    try:
        for qr_code_id in qr_code_ids:
            qr_code = db.query(QRCode).filter(
                QRCode.id == qr_code_id,
                QRCode.user_id == current_user.id
            ).first()
            
            if not qr_code:
                continue  # Skip non-existent QR codes
            
            # Update QR code
            update_data = qr_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(qr_code, field, value)
            
            db.commit()
            db.refresh(qr_code)
            updated_qr_codes.append(qr_code)
        
        return updated_qr_codes[0] if updated_qr_codes else None
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk update error: {str(e)}"
        )


@router.delete("/bulk-delete")
async def bulk_delete_qr_codes(
    qr_code_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete multiple QR codes in bulk."""
    
    if len(qr_code_ids) > 50:  # Limit bulk size
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many QR codes. Maximum bulk delete size is 50 QR codes."
        )
    
    deleted_count = 0
    
    try:
        for qr_code_id in qr_code_ids:
            qr_code = db.query(QRCode).filter(
                QRCode.id == qr_code_id,
                QRCode.user_id == current_user.id
            ).first()
            
            if qr_code:
                db.delete(qr_code)
                deleted_count += 1
        
        db.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} QR codes",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bulk delete error: {str(e)}"
        )
