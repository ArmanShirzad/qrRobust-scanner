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
           filename.rsplit('.', 1)[1].lower() in settings.allowed_extensions.split(',')


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


@router.post("/batch-decode")
async def batch_decode_qr_endpoint(
    files: List[UploadFile] = File(...),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Decode multiple QR codes from uploaded image files in batch."""
    
    if len(files) > 50:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Too many files. Maximum batch size is 50 files."
        )
    
    results = []
    temp_files = []
    
    try:
        for file in files:
            if not allowed_file(file.filename):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "Invalid file type"
                })
                continue
            
            # Check file size
            if file.size and file.size > settings.max_file_size:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": f"File too large. Maximum size is {settings.max_file_size} bytes."
                })
                continue
            
            # Save uploaded file temporarily
            filename = secure_filename(file.filename)
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}") as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
                temp_files.append(tmp_file_path)
            
            # Decode QR code
            decoded_data, error = decode_qr_code(tmp_file_path)
            
            if error:
                results.append({
                    "filename": filename,
                    "success": False,
                    "error": error
                })
            else:
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
                
                results.append({
                    "filename": filename,
                    "success": True,
                    "decoded_data": decoded_data,
                    "scan_id": scan_record.id
                })
        
        return {
            "success": True,
            "total_files": len(files),
            "processed_files": len(results),
            "results": results
        }
        
    finally:
        # Clean up temporary files
        for tmp_file_path in temp_files:
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)


@router.post("/batch-decode-base64")
async def batch_decode_qr_base64_endpoint(
    request_data: dict,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Decode multiple QR codes from base64 encoded images in batch."""
    
    images = request_data.get("images", [])
    if not images:
        raise HTTPException(status_code=400, detail="No images provided")
    
    if len(images) > 50:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Too many images. Maximum batch size is 50 images."
        )
    
    results = []
    
    try:
        for i, base64_image in enumerate(images):
            if not base64_image:
                results.append({
                    "index": i,
                    "success": False,
                    "error": "No image data provided"
                })
                continue
            
            try:
                decoded_data, error = decode_qr_from_base64(base64_image)
                
                if error:
                    results.append({
                        "index": i,
                        "success": False,
                        "error": error
                    })
                else:
                    # Save scan to database for analytics
                    client_info = get_client_info(request)
                    scan_record = QRScan(
                        user_id=current_user.id if current_user else None,
                        content=decoded_data[0] if decoded_data else None,
                        filename=f"base64_image_{i}",
                        file_size=len(base64_image),
                        ip_address=client_info["ip_address"],
                        user_agent=client_info["user_agent"],
                        referer=client_info["referer"],
                        scan_timestamp=datetime.utcnow()
                    )
                    db.add(scan_record)
                    db.commit()
                    db.refresh(scan_record)
                    
                    results.append({
                        "index": i,
                        "success": True,
                        "decoded_data": decoded_data,
                        "scan_id": scan_record.id
                    })
                    
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": f"Processing error: {str(e)}"
                })
        
        return {
            "success": True,
            "total_images": len(images),
            "processed_images": len(results),
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")


@router.get("/health")
async def qr_health_check():
    """Health check for QR processing service."""
    return {"status": "healthy", "service": "qr_processor"}
