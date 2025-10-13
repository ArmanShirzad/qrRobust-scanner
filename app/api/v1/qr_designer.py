"""QR Code Designer API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import os
import uuid
from datetime import datetime

from app.database import get_db
from app.models import User, QRCode
from app.utils.dependencies import get_current_user, get_optional_current_user
from app.services.qr_designer import qr_designer
from app.schemas.qr_codes import QRCodeCreate, QRCodeResponse, QRCodeUpdate

router = APIRouter()


@router.post("/design", response_model=Dict[str, Any])
async def design_qr_code(
    data: str = Form(...),
    size: int = Form(300),
    border: int = Form(4),
    error_correction: str = Form("M"),
    fill_color: str = Form("#000000"),
    back_color: str = Form("#FFFFFF"),
    module_drawer: str = Form("square"),
    color_mask: str = Form("solid"),
    logo_size: Optional[int] = Form(None),
    logo_position: str = Form("center"),
    corner_radius: int = Form(0),
    custom_styling: Optional[str] = Form(None),
    logo_file: Optional[UploadFile] = File(None),
    background_file: Optional[UploadFile] = File(None),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Design a custom QR code with advanced styling options.
    
    - **data**: QR code data/content
    - **size**: QR code size in pixels (100-2000)
    - **border**: Border size (0-20)
    - **error_correction**: Error correction level (L, M, Q, H)
    - **fill_color**: Foreground color (hex)
    - **back_color**: Background color (hex)
    - **module_drawer**: Module style (square, rounded, circle, gapped_square)
    - **color_mask**: Color effect (solid, radial_gradient, square_gradient, etc.)
    - **logo_size**: Logo size in pixels (20-200)
    - **logo_position**: Logo position (center, top-left, top-right, bottom-left, bottom-right)
    - **corner_radius**: Corner radius for rounded modules (0-10)
    - **custom_styling**: JSON string with custom styling options
    - **logo_file**: Logo image file
    - **background_file**: Background image file
    """
    
    try:
        # Validate and clean options
        options = {
            "data": data,
            "size": size,
            "border": border,
            "error_correction": error_correction,
            "fill_color": fill_color,
            "back_color": back_color,
            "module_drawer": module_drawer,
            "color_mask": color_mask,
            "logo_size": logo_size,
            "logo_position": logo_position,
            "corner_radius": corner_radius
        }
        
        # Parse custom styling if provided
        if custom_styling:
            import json
            try:
                options["custom_styling"] = json.loads(custom_styling)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid custom_styling JSON format"
                )
        
        # Handle logo file upload
        logo_path = None
        if logo_file:
            logo_path = await _save_uploaded_file(logo_file, "logos")
            options["logo_path"] = logo_path
        
        # Handle background file upload
        background_path = None
        if background_file:
            background_path = await _save_uploaded_file(background_file, "backgrounds")
            options["background_image"] = background_path
        
        # Validate options
        validated_options = qr_designer.validate_design_options(options)
        
        # Create QR code
        data = validated_options.pop("data")
        result = qr_designer.create_qr_code(data=data, **validated_options)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create QR code: {result['error']}"
            )
        
        # Clean up temporary files
        if logo_path and os.path.exists(logo_path):
            os.remove(logo_path)
        if background_path and os.path.exists(background_path):
            os.remove(background_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error designing QR code: {str(e)}"
        )


@router.get("/qr-code/{qr_id}/image")
async def get_qr_code_image(
    qr_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get QR code image for a saved QR code."""
    # Get QR code from database
    qr_code = db.query(QRCode).filter(
        QRCode.id == qr_id,
        QRCode.user_id == current_user.id
    ).first()
    
    if not qr_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="QR code not found"
        )
    
    # Generate QR code from stored parameters
    options = {
        "data": qr_code.destination_url,
        "size": qr_code.size,
        "border": qr_code.border,
        "error_correction": qr_code.error_correction_level,
        "fill_color": qr_code.foreground_color,
        "back_color": qr_code.background_color,
        "module_drawer": "square",
        "color_mask": "solid",
        "corner_radius": 0
    }
    
    # Validate and create QR code
    validated_options = qr_designer.validate_design_options(options)
    data = validated_options.pop("data")
    result = qr_designer.create_qr_code(data=data, **validated_options)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate QR code: {result['error']}"
        )
    
    return {
        "image_data": result["image_data"],
        "qr_code": {
            "id": qr_code.id,
            "title": qr_code.title,
            "destination_url": qr_code.destination_url,
            "size": qr_code.size
        }
    }


@router.post("/design-and-save")
async def design_and_save_qr_code(
    data: str = Form(...),
    name: str = Form(...),
    size: int = Form(300),
    border: int = Form(4),
    error_correction: str = Form("M"),
    fill_color: str = Form("#000000"),
    back_color: str = Form("#FFFFFF"),
    module_drawer: str = Form("square"),
    color_mask: str = Form("solid"),
    logo_size: Optional[int] = Form(None),
    logo_position: str = Form("center"),
    corner_radius: int = Form(0),
    custom_styling: Optional[str] = Form(None),
    logo_file: Optional[UploadFile] = File(None),
    background_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Design a custom QR code and save it to the user's collection.
    
    Same parameters as /design but saves the QR code to the database.
    """
    
    try:
        # Validate and clean options
        options = {
            "data": data,
            "size": size,
            "border": border,
            "error_correction": error_correction,
            "fill_color": fill_color,
            "back_color": back_color,
            "module_drawer": module_drawer,
            "color_mask": color_mask,
            "logo_size": logo_size,
            "logo_position": logo_position,
            "corner_radius": corner_radius
        }
        
        # Parse custom styling if provided
        if custom_styling:
            import json
            try:
                options["custom_styling"] = json.loads(custom_styling)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid custom_styling JSON format"
                )
        
        # Handle logo file upload
        logo_path = None
        if logo_file:
            logo_path = await _save_uploaded_file(logo_file, "logos")
            options["logo_path"] = logo_path
        
        # Handle background file upload
        background_path = None
        if background_file:
            background_path = await _save_uploaded_file(background_file, "backgrounds")
            options["background_image"] = background_path
        
        # Validate options
        validated_options = qr_designer.validate_design_options(options)
        
        # Create QR code
        data = validated_options.pop("data")
        result = qr_designer.create_qr_code(data=data, **validated_options)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create QR code: {result['error']}"
            )
        
        # Save to database
        qr_code = QRCode(
            user_id=current_user.id,
            title=name,
            destination_url=data,  # Store the QR data as destination_url
            short_url=f"qr-{uuid.uuid4().hex[:8]}",  # Generate a short URL
            size=validated_options["size"],
            border=validated_options["border"],
            error_correction_level=validated_options["error_correction"],
            foreground_color=validated_options["fill_color"],
            background_color=validated_options["back_color"],
            created_at=datetime.utcnow()
        )
        
        db.add(qr_code)
        db.commit()
        db.refresh(qr_code)
        
        # Clean up temporary files
        if logo_path and os.path.exists(logo_path):
            os.remove(logo_path)
        if background_path and os.path.exists(background_path):
            os.remove(background_path)
        
        # Return QR code with image data - minimal fields only
        return {
            "id": qr_code.id,
            "title": qr_code.title or "QR Code",
            "destination_url": qr_code.destination_url or "",
            "image_data": result["image_data"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error designing and saving QR code: {str(e)}"
        )


@router.get("/styles", response_model=Dict[str, Any])
async def get_available_styles():
    """Get all available styling options for QR code design."""
    return qr_designer.get_available_styles()


@router.get("/templates", response_model=Dict[str, Any])
def get_design_templates():
    """Get predefined design templates."""
    templates = {
        "minimal": {
            "name": "Minimal",
            "description": "Clean and simple design",
            "options": {
                "fill_color": "#000000",
                "back_color": "#FFFFFF",
                "module_drawer": "square",
                "color_mask": "solid",
                "border": 4,
                "corner_radius": 0
            }
        },
        "rounded": {
            "name": "Rounded",
            "description": "Modern rounded corners",
            "options": {
                "fill_color": "#2563eb",
                "back_color": "#FFFFFF",
                "module_drawer": "rounded",
                "color_mask": "solid",
                "border": 4,
                "corner_radius": 2
            }
        },
        "gradient_blue": {
            "name": "Blue Gradient",
            "description": "Beautiful blue gradient effect",
            "options": {
                "fill_color": "#1e3c72",
                "back_color": "#FFFFFF",
                "module_drawer": "square",
                "color_mask": "radial_gradient",
                "border": 4,
                "corner_radius": 0
            }
        },
        "gradient_green": {
            "name": "Green Gradient",
            "description": "Fresh green gradient",
            "options": {
                "fill_color": "#11998e",
                "back_color": "#FFFFFF",
                "module_drawer": "square",
                "color_mask": "radial_gradient",
                "border": 4,
                "corner_radius": 0
            }
        },
        "circles": {
            "name": "Circles",
            "description": "Circular module design",
            "options": {
                "fill_color": "#7c3aed",
                "back_color": "#FFFFFF",
                "module_drawer": "circle",
                "color_mask": "solid",
                "border": 4,
                "corner_radius": 0
            }
        },
        "gapped": {
            "name": "Gapped Squares",
            "description": "Squares with gaps",
            "options": {
                "fill_color": "#dc2626",
                "back_color": "#FFFFFF",
                "module_drawer": "gapped_square",
                "color_mask": "solid",
                "border": 4,
                "corner_radius": 0
            }
        },
        "dark_mode": {
            "name": "Dark Mode",
            "description": "Dark theme design",
            "options": {
                "fill_color": "#ffffff",
                "back_color": "#1a1a1a",
                "module_drawer": "square",
                "color_mask": "solid",
                "border": 4,
                "corner_radius": 0
            }
        },
        "premium": {
            "name": "Premium",
            "description": "Premium design with shadow and border",
            "options": {
                "fill_color": "#1f2937",
                "back_color": "#FFFFFF",
                "module_drawer": "rounded",
                "color_mask": "solid",
                "border": 4,
                "corner_radius": 1,
                "custom_styling": {
                    "border_width": 8,
                    "border_color": "#f3f4f6",
                    "shadow": True,
                    "shadow_offset": 8,
                    "shadow_color": "#000000",
                    "shadow_opacity": 0.2
                }
            }
        }
    }
    
    return {"templates": templates}


@router.post("/preview", response_model=Dict[str, Any])
async def preview_qr_design(
    data: str = Form(...),
    template: str = Form("minimal"),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Preview a QR code design using a predefined template.
    
    - **data**: QR code data/content
    - **template**: Template name (minimal, rounded, gradient_blue, etc.)
    """
    
    try:
        # Get template
        templates_response = get_design_templates()
        templates = templates_response["templates"]
        
        if template not in templates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Template '{template}' not found"
            )
        
        template_options = templates[template]["options"]
        
        # Create QR code with template options
        result = qr_designer.create_qr_code(data=data, **template_options)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to create preview: {result['error']}"
            )
        
        return {
            "success": True,
            "template": template,
            "template_name": templates[template]["name"],
            "template_description": templates[template]["description"],
            "image_data": result["image_data"],
            "metadata": result["metadata"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating preview: {str(e)}"
        )


async def _save_uploaded_file(file: UploadFile, subfolder: str) -> str:
    """Save uploaded file to temporary directory."""
    # Create subfolder if it doesn't exist
    upload_dir = f"uploads/{subfolder}"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'bin'
    filename = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return file_path
