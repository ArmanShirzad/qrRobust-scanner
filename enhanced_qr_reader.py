#!/usr/bin/env python3
"""
Enhanced QR code reader that tries multiple detection methods
"""

import sys
import os
import cv2
import numpy as np
from PIL import Image

def try_opencv_detection(image_path):
    """Try OpenCV QR detection with multiple preprocessing methods."""
    try:
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        qr_detector = cv2.QRCodeDetector()
        
        # Try different preprocessing approaches
        approaches = [
            ("Original", image),
            ("Grayscale", cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)),
        ]
        
        # Add resizing if image is small
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        if height < 200 or width < 200:
            scale_factor = max(200/height, 200/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            resized = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            approaches.append(("Resized", resized))
        
        # Add thresholding approaches
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        approaches.append(("Threshold", thresh))
        
        # Add adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        approaches.append(("Adaptive Threshold", adaptive_thresh))
        
        for name, processed_image in approaches:
            data, bbox, _ = qr_detector.detectAndDecode(processed_image)
            if data:
                print(f"✅ OpenCV detection successful using {name} method")
                return data
        
        return None
    except Exception as e:
        print(f"OpenCV detection failed: {e}")
        return None

def try_pyzbar_detection(image_path):
    """Try pyzbar detection (if available)."""
    try:
        from pyzbar import pyzbar
        
        # Read image with PIL
        image = Image.open(image_path)
        
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Try detection
        qr_codes = pyzbar.decode(image)
        
        if qr_codes:
            data = qr_codes[0].data.decode('utf-8')
            print("✅ pyzbar detection successful")
            return data
        
        return None
    except ImportError:
        print("pyzbar not available (missing system dependencies)")
        return None
    except Exception as e:
        print(f"pyzbar detection failed: {e}")
        return None

def detect_content_type(data):
    """Detect and display the content type of the QR code data."""
    if data.startswith('http://') or data.startswith('https://'):
        print(f"Type: URL")
    elif data.startswith('mailto:'):
        print(f"Type: Email")
    elif data.startswith('tel:'):
        print(f"Type: Phone")
    elif data.startswith('WIFI:'):
        print(f"Type: WiFi Configuration")
        # Parse WiFi details
        wifi_parts = data[5:].split(';')  # Remove 'WIFI:' prefix
        wifi_info = {}
        for part in wifi_parts:
            if ':' in part:
                key, value = part.split(':', 1)
                wifi_info[key] = value
        
        if wifi_info:
            print("WiFi Details:")
            if 'S' in wifi_info:
                print(f"  Network Name (SSID): {wifi_info['S']}")
            if 'T' in wifi_info:
                print(f"  Security Type: {wifi_info['T']}")
            if 'P' in wifi_info:
                print(f"  Password: {wifi_info['P']}")
            if 'H' in wifi_info:
                print(f"  Hidden: {wifi_info['H']}")
    else:
        print(f"Type: Text")

def decode_qr_code(image_path):
    """Try multiple QR code detection methods."""
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return False
    
    print(f"Attempting to decode QR code from: {image_path}")
    print("=" * 60)
    
    # Try pyzbar first (often better with logos)
    data = try_pyzbar_detection(image_path)
    if data:
        print(f"Content: {data}")
        detect_content_type(data)
        return True
    
    # Try OpenCV methods
    data = try_opencv_detection(image_path)
    if data:
        print(f"Content: {data}")
        detect_content_type(data)
        return True
    
    print("❌ No QR code found with any detection method.")
    print("\nTroubleshooting tips:")
    print("- Ensure the image has good contrast")
    print("- Try a different QR code without logos")
    print("- Check if the QR code is damaged or blurry")
    return False

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python enhanced_qr_reader.py <image_path>")
        print("\nExample:")
        print("  python enhanced_qr_reader.py qr_code.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = decode_qr_code(image_path)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
