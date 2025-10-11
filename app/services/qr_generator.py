"""QR Code generation and management service."""

import qrcode
from qrcode.image.pil import PilImage
from PIL import Image, ImageDraw
import io
import base64
import secrets
import string
from typing import Optional, Tuple
from urllib.parse import urlparse
import os

from app.core.config import settings


class QRCodeGenerator:
    """Service for generating QR codes with custom styling."""
    
    @staticmethod
    def generate_short_url() -> str:
        """Generate a short URL identifier."""
        # Generate a random 8-character string
        chars = string.ascii_letters + string.digits
        short_id = ''.join(secrets.choice(chars) for _ in range(8))
        return f"https://qr.example.com/{short_id}"  # TODO: Use actual domain
    
    @staticmethod
    def generate_qr_code(
        data: str,
        size: int = 10,
        border: int = 4,
        error_correction: str = "M",
        foreground_color: str = "#000000",
        background_color: str = "#FFFFFF",
        logo_path: Optional[str] = None
    ) -> Tuple[bytes, str]:
        """Generate a QR code image with custom styling."""
        
        # Map error correction levels
        error_levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H
        }
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_M),
            box_size=size,
            border=border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(
            fill_color=foreground_color,
            back_color=background_color,
            image_factory=PilImage
        )
        
        # Add logo if provided
        if logo_path and os.path.exists(logo_path):
            img = QRCodeGenerator._add_logo(img, logo_path)
        
        # Convert to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_bytes = img_buffer.getvalue()
        
        return img_bytes, data
    
    @staticmethod
    def _add_logo(qr_img: Image.Image, logo_path: str) -> Image.Image:
        """Add a logo to the center of the QR code."""
        try:
            logo = Image.open(logo_path)
            
            # Calculate logo size (should be about 1/5 of QR code size)
            qr_width, qr_height = qr_img.size
            logo_size = min(qr_width, qr_height) // 5
            
            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Create a white background for the logo
            logo_bg = Image.new('RGB', (logo_size + 20, logo_size + 20), 'white')
            logo_bg.paste(logo, (10, 10))
            
            # Calculate position to center the logo
            logo_x = (qr_width - logo_bg.width) // 2
            logo_y = (qr_height - logo_bg.height) // 2
            
            # Paste logo onto QR code
            qr_img.paste(logo_bg, (logo_x, logo_y))
            
            return qr_img
            
        except Exception as e:
            print(f"Error adding logo: {e}")
            return qr_img
    
    @staticmethod
    def generate_qr_base64(
        data: str,
        size: int = 10,
        border: int = 4,
        error_correction: str = "M",
        foreground_color: str = "#000000",
        background_color: str = "#FFFFFF",
        logo_path: Optional[str] = None
    ) -> str:
        """Generate QR code and return as base64 string."""
        img_bytes, _ = QRCodeGenerator.generate_qr_code(
            data, size, border, error_correction, 
            foreground_color, background_color, logo_path
        )
        
        return base64.b64encode(img_bytes).decode('utf-8')
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if a string is a valid URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    @staticmethod
    def validate_qr_data(data: str) -> Tuple[bool, str]:
        """Validate QR code data."""
        if not data or len(data.strip()) == 0:
            return False, "QR code data cannot be empty"
        
        if len(data) > 2953:  # Maximum QR code capacity for version 40
            return False, "QR code data is too long (maximum 2953 characters)"
        
        return True, "Valid"
    
    @staticmethod
    def get_qr_info(data: str) -> dict:
        """Get information about QR code data."""
        is_url = QRCodeGenerator.validate_url(data)
        
        info = {
            "length": len(data),
            "is_url": is_url,
            "estimated_version": QRCodeGenerator._estimate_qr_version(len(data)),
            "max_capacity": 2953
        }
        
        if is_url:
            parsed = urlparse(data)
            info.update({
                "domain": parsed.netloc,
                "scheme": parsed.scheme,
                "path": parsed.path
            })
        
        return info
    
    @staticmethod
    def _estimate_qr_version(data_length: int) -> int:
        """Estimate QR code version based on data length."""
        # Rough estimation - actual version depends on error correction level
        if data_length <= 25:
            return 1
        elif data_length <= 47:
            return 2
        elif data_length <= 77:
            return 3
        elif data_length <= 114:
            return 4
        elif data_length <= 154:
            return 5
        elif data_length <= 195:
            return 6
        elif data_length <= 224:
            return 7
        elif data_length <= 279:
            return 8
        elif data_length <= 335:
            return 9
        elif data_length <= 395:
            return 10
        else:
            return min(40, (data_length // 40) + 1)
