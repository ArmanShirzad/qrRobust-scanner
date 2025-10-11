"""QR Code processing utilities."""

import io
import base64
from typing import List, Optional, Tuple
import cv2
import numpy as np
from PIL import Image


def decode_with_zxing(image_path: str) -> Optional[List[str]]:
    """Decode QR code using zxing-cpp library."""
    try:
        import zxingcpp
        
        # Read image
        image = Image.open(image_path)
        
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Convert PIL image to numpy array
        img_array = np.array(image)
        
        # Try to decode
        results = zxingcpp.read_barcodes(img_array)
        
        if results:
            decoded_data = []
            for result in results:
                if result.format == zxingcpp.BarcodeFormat.QRCode:
                    decoded_data.append(result.text)
            return decoded_data if decoded_data else None
        
        return None
        
    except ImportError:
        return None
    except Exception as e:
        print(f"zxing-cpp error: {e}")
        return None


def decode_qr_code(image_path: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """Decode QR code from image file using multiple detection methods."""
    try:
        # First try zxing-cpp (better for QR codes with logos)
        zxing_result = decode_with_zxing(image_path)
        if zxing_result:
            return zxing_result, None
        
        # Fallback to OpenCV methods
        # Read the image
        image = cv2.imread(image_path)
        
        if image is None:
            return None, "Could not read the image file"
        
        # Try multiple approaches for better detection
        qr_detector = cv2.QRCodeDetector()
        
        # First attempt: direct detection
        data, bbox, _ = qr_detector.detectAndDecode(image)
        
        if data:
            return [data], None
        
        # Second attempt: convert to grayscale and try again
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = qr_detector.detectAndDecode(gray)
        
        if data:
            return [data], None
        
        # Third attempt: apply some preprocessing
        # Resize image if it's too small
        height, width = gray.shape
        if height < 200 or width < 200:
            scale_factor = max(200/height, 200/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply threshold to improve contrast
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        data, bbox, _ = qr_detector.detectAndDecode(thresh)
        
        if data:
            return [data], None
        
        return None, "No QR code found in the image. Try using a clearer image with better contrast."
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"


def decode_qr_from_base64(base64_string: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """Decode QR code from base64 encoded image using multiple detection methods."""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        image_data = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # First try zxing-cpp
        try:
            import zxingcpp
            
            # Convert to grayscale if needed
            if image.mode != 'L':
                image_gray = image.convert('L')
            else:
                image_gray = image
            
            # Convert PIL image to numpy array
            img_array = np.array(image_gray)
            
            # Try to decode
            results = zxingcpp.read_barcodes(img_array)
            
            if results:
                decoded_data = []
                for result in results:
                    if result.format == zxingcpp.BarcodeFormat.QRCode:
                        decoded_data.append(result.text)
                if decoded_data:
                    return decoded_data, None
        except ImportError:
            pass
        except Exception as e:
            print(f"zxing-cpp error: {e}")
        
        # Fallback to OpenCV methods
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Try multiple approaches for better detection
        qr_detector = cv2.QRCodeDetector()
        
        # First attempt: direct detection
        data, bbox, _ = qr_detector.detectAndDecode(opencv_image)
        
        if data:
            return [data], None
        
        # Second attempt: convert to grayscale and try again
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = qr_detector.detectAndDecode(gray)
        
        if data:
            return [data], None
        
        # Third attempt: apply some preprocessing
        # Resize image if it's too small
        height, width = gray.shape
        if height < 200 or width < 200:
            scale_factor = max(200/height, 200/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply threshold to improve contrast
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        data, bbox, _ = qr_detector.detectAndDecode(thresh)
        
        if data:
            return [data], None
        
        return None, "No QR code found in the image. Try using a clearer image with better contrast."
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"


def batch_decode_qr_codes(image_paths: List[str]) -> List[Tuple[Optional[List[str]], Optional[str]]]:
    """Decode multiple QR codes from a list of image paths."""
    results = []
    for image_path in image_paths:
        result = decode_qr_code(image_path)
        results.append(result)
    return results


def batch_decode_qr_from_base64(base64_images: List[str]) -> List[Tuple[Optional[List[str]], Optional[str]]]:
    """Decode multiple QR codes from a list of base64 encoded images."""
    results = []
    for base64_image in base64_images:
        result = decode_qr_from_base64(base64_image)
        results.append(result)
    return results


def get_qr_code_info(data: str) -> dict:
    """Extract information about QR code data."""
    info = {
        "data": data,
        "length": len(data),
        "type": "unknown",
        "is_url": False,
        "is_email": False,
        "is_phone": False,
        "is_wifi": False,
        "is_geo": False,
        "is_sms": False,
        "is_vcard": False
    }
    
    # Check for URL
    if data.startswith(('http://', 'https://', 'www.')):
        info["type"] = "url"
        info["is_url"] = True
    
    # Check for email
    elif '@' in data and '.' in data.split('@')[1]:
        info["type"] = "email"
        info["is_email"] = True
    
    # Check for phone number
    elif data.startswith('tel:'):
        info["type"] = "phone"
        info["is_phone"] = True
    
    # Check for WiFi
    elif data.startswith('WIFI:'):
        info["type"] = "wifi"
        info["is_wifi"] = True
    
    # Check for SMS
    elif data.startswith('sms:'):
        info["type"] = "sms"
        info["is_sms"] = True
    
    # Check for vCard
    elif data.startswith('BEGIN:VCARD'):
        info["type"] = "vcard"
        info["is_vcard"] = True
    
    # Check for geographic coordinates
    elif 'geo:' in data.lower() or 'latitude' in data.lower():
        info["type"] = "geo"
        info["is_geo"] = True
    
    else:
        info["type"] = "text"
    
    return info
