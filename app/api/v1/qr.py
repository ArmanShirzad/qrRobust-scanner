"""QR Code processing endpoints."""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import tempfile
import uuid
from datetime import datetime

from app.core.config import settings
from app.utils.qr_processor import decode_qr_code, decode_qr_from_base64
from app.database import get_db
from app.models import QRScan, User
from app.utils.dependencies import get_optional_current_user
from sqlalchemy.orm import Session

router = APIRouter()


def allowed_file(filename: str) -> bool:
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.allowed_extensions


def secure_filename(filename: str) -> str:
    """Secure filename by removing dangerous characters."""
    # Simple implementation - in production, use a proper library
    import re
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    return filename


def get_client_info(request: Request) -> dict:
    """Extract client information from request."""
    return {
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "referer": request.headers.get("referer"),
    }


@router.post("/decode")
async def decode_qr_endpoint(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Decode QR code from uploaded image file."""
    
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image file."
        )
    
    # Check file size
    if file.size and file.size > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size} bytes."
        )
    
    # Save uploaded file temporarily
    filename = secure_filename(file.filename)
    with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Decode QR code
        decoded_data, error = decode_qr_code(tmp_file_path)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        # Save scan to database for analytics
        client_info = get_client_info(request)
        scan_record = QRScan(
            user_id=current_user.id if current_user else None,
            content=decoded_data[0] if decoded_data else None,
            filename=filename,
            file_size=len(content),
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"],
            referer=client_info["referer"],
            scan_timestamp=datetime.utcnow()
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)
        
        return {
            "success": True,
            "decoded_data": decoded_data,
            "filename": filename,
            "scan_id": scan_record.id
        }
        
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)


@router.post("/decode-base64")
async def decode_qr_base64_endpoint(
    request_data: dict,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Decode QR code from base64 encoded image."""
    
    base64_image = request_data.get("image")
    if not base64_image:
        raise HTTPException(status_code=400, detail="No image data provided")
    
    try:
        decoded_data, error = decode_qr_from_base64(base64_image)
        
        if error:
            raise HTTPException(status_code=400, detail=error)
        
        # Save scan to database for analytics
        client_info = get_client_info(request)
        scan_record = QRScan(
            user_id=current_user.id if current_user else None,
            content=decoded_data[0] if decoded_data else None,
            filename="base64_image",
            file_size=len(base64_image),
            ip_address=client_info["ip_address"],
            user_agent=client_info["user_agent"],
            referer=client_info["referer"],
            scan_timestamp=datetime.utcnow()
        )
        db.add(scan_record)
        db.commit()
        db.refresh(scan_record)
        
        return {
            "success": True,
            "decoded_data": decoded_data,
            "scan_id": scan_record.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


@router.get("/health")
async def qr_health_check():
    """Health check for QR processing service."""
    return {"status": "healthy", "service": "qr_processor"}
