#!/usr/bin/env python3
"""
QR code decoder using zxing-cpp library
"""

import sys
import os
from PIL import Image
import numpy as np

def decode_with_zxing(image_path):
    """Decode QR code using zxing-cpp."""
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
            for result in results:
                if result.format == zxingcpp.BarcodeFormat.QRCode:
                    return result.text
        
        return None
        
    except ImportError:
        print("zxing-cpp not available")
        return None
    except Exception as e:
        print(f"zxing-cpp error: {e}")
        return None

def decode_wifi_qr_zxing(image_path):
    """Decode WiFi QR code using zxing-cpp."""
    if not os.path.exists(image_path):
        print(f"Error: File '{image_path}' not found.")
        return False
    
    print(f"🔍 Attempting to decode WiFi QR code with zxing-cpp: {image_path}")
    print("=" * 70)
    
    # Try zxing-cpp detection
    data = decode_with_zxing(image_path)
    
    if data:
        print("✅ QR Code detected successfully with zxing-cpp!")
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
        print("❌ Unable to detect QR code with zxing-cpp")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python zxing_qr_decoder.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    success = decode_wifi_qr_zxing(image_path)
    sys.exit(0 if success else 1)
