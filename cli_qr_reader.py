#!/usr/bin/env python3
"""
Command-line QR code reader
Usage: python cli_qr_reader.py <image_path>
"""

import sys
import os
from PIL import Image
import cv2
import numpy as np

def decode_qr_code(image_path):
    """Decode QR code from image file using OpenCV with improved detection."""
    try:
        # Check if file exists
        if not os.path.exists(image_path):
            print(f"Error: File '{image_path}' not found.")
            return False
        
        # Read the image
        image = cv2.imread(image_path)
        
        if image is None:
            print(f"Error: Could not read the image file '{image_path}'.")
            print("Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF")
            return False
        
        # Try multiple approaches for better detection
        qr_detector = cv2.QRCodeDetector()
        
        # First attempt: direct detection
        data, bbox, _ = qr_detector.detectAndDecode(image)
        
        if data:
            print(f"Found QR code in '{image_path}':")
            print("-" * 50)
            print(f"Content: {data}")
            detect_content_type(data)
            return True
        
        # Second attempt: convert to grayscale and try again
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = qr_detector.detectAndDecode(gray)
        
        if data:
            print(f"Found QR code in '{image_path}':")
            print("-" * 50)
            print(f"Content: {data}")
            detect_content_type(data)
            return True
        
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
            print(f"Found QR code in '{image_path}':")
            print("-" * 50)
            print(f"Content: {data}")
            detect_content_type(data)
            return True
        
        # Fourth attempt: more aggressive preprocessing for difficult QR codes
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Try adaptive thresholding
        adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        data, bbox, _ = qr_detector.detectAndDecode(adaptive_thresh)
        
        if data:
            print(f"Found QR code in '{image_path}':")
            print("-" * 50)
            print(f"Content: {data}")
            detect_content_type(data)
            return True
        
        # Fifth attempt: morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        data, bbox, _ = qr_detector.detectAndDecode(morph)
        
        if data:
            print(f"Found QR code in '{image_path}':")
            print("-" * 50)
            print(f"Content: {data}")
            detect_content_type(data)
            return True
        
        print("No QR code found in the image. Try using a clearer image with better contrast.")
        return False
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return False

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

def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python cli_qr_reader.py <image_path>")
        print("\nExample:")
        print("  python cli_qr_reader.py qr_code.png")
        print("  python cli_qr_reader.py /path/to/image.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = decode_qr_code(image_path)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()
