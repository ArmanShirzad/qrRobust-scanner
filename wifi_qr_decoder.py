#!/usr/bin/env python3
"""
Specialized QR code reader for WiFi QR codes with logos
"""

import cv2
import numpy as np
from PIL import Image
import os

def preprocess_for_logo_qr(image_path):
    """Preprocess image specifically for QR codes with logos in center."""
    try:
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Get image dimensions
        height, width = gray.shape
        
        # Resize if too small
        if height < 500 or width < 500:
            scale_factor = max(500/height, 500/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Try to detect and mask the center logo area
        # This is a heuristic approach for WiFi QR codes
        center_x, center_y = gray.shape[1] // 2, gray.shape[0] // 2
        
        # Create a mask to potentially ignore the center area
        mask = np.ones(gray.shape, dtype=np.uint8) * 255
        
        # Estimate logo size (usually 15-25% of QR code)
        logo_size = min(gray.shape) // 6
        
        # Create circular mask for center area
        cv2.circle(mask, (center_x, center_y), logo_size, 0, -1)
        
        # Apply mask
        masked_image = cv2.bitwise_and(gray, mask)
        
        return masked_image
        
    except Exception as e:
        print(f"Preprocessing error: {e}")
        return None

def try_multiple_detection_methods(image_path):
    """Try multiple detection methods for difficult QR codes."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        qr_detector = cv2.QRCodeDetector()
        
        # Method 1: Original image
        data, bbox, _ = qr_detector.detectAndDecode(image)
        if data:
            return data
        
        # Method 2: Grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = qr_detector.detectAndDecode(gray)
        if data:
            return data
        
        # Method 3: Preprocessed for logo
        processed = preprocess_for_logo_qr(image_path)
        if processed is not None:
            data, bbox, _ = qr_detector.detectAndDecode(processed)
            if data:
                return data
        
        # Method 4: Different thresholding approaches
        thresholds = [
            cv2.THRESH_BINARY,
            cv2.THRESH_BINARY_INV,
            cv2.THRESH_TRUNC,
            cv2.THRESH_TOZERO,
            cv2.THRESH_TOZERO_INV
        ]
        
        for thresh_type in thresholds:
            _, thresh = cv2.threshold(gray, 127, 255, thresh_type)
            data, bbox, _ = qr_detector.detectAndDecode(thresh)
            if data:
                return data
        
        # Method 5: Adaptive thresholding with different parameters
        for block_size in [11, 15, 19]:
            for c in [2, 5, 10]:
                adaptive_thresh = cv2.adaptiveThreshold(
                    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, c
                )
                data, bbox, _ = qr_detector.detectAndDecode(adaptive_thresh)
                if data:
                    return data
        
        # Method 6: Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        data, bbox, _ = qr_detector.detectAndDecode(morph)
        if data:
            return data
        
        # Method 7: Edge detection
        edges = cv2.Canny(gray, 50, 150)
        data, bbox, _ = qr_detector.detectAndDecode(edges)
        if data:
            return data
        
        return None
        
    except Exception as e:
        print(f"Detection error: {e}")
        return None

def decode_wifi_qr(image_path):
    """Decode WiFi QR code with specialized methods."""
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return False
    
    print(f"🔍 Attempting to decode WiFi QR code: {image_path}")
    print("=" * 60)
    
    # Try multiple detection methods
    data = try_multiple_detection_methods(image_path)
    
    if data:
        print("✅ QR Code detected successfully!")
        print(f"Content: {data}")
        
        # Parse WiFi information
        if data.startswith('WIFI:'):
            print("Type: WiFi Configuration")
            wifi_parts = data[5:].split(';')  # Remove 'WIFI:' prefix
            wifi_info = {}
            for part in wifi_parts:
                if ':' in part:
                    key, value = part.split(':', 1)
                    wifi_info[key] = value
            
            if wifi_info:
                print("\n📶 WiFi Details:")
                if 'S' in wifi_info:
                    print(f"  Network Name (SSID): {wifi_info['S']}")
                if 'T' in wifi_info:
                    print(f"  Security Type: {wifi_info['T']}")
                if 'P' in wifi_info:
                    print(f"  Password: {wifi_info['P']}")
                if 'H' in wifi_info:
                    print(f"  Hidden: {wifi_info['H']}")
        else:
            print(f"Type: {data[:20]}...")
        
        return True
    else:
        print("❌ Unable to detect QR code")
        print("\nPossible reasons:")
        print("- Logo in center is interfering with detection")
        print("- Image quality or contrast issues")
        print("- QR code is damaged or corrupted")
        print("\nSuggestions:")
        print("- Try using a mobile camera app")
        print("- Use online QR code readers")
        print("- Create a clean QR code without logo")
        return False

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python wifi_qr_decoder.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = decode_wifi_qr(image_path)
    sys.exit(0 if success else 1)
