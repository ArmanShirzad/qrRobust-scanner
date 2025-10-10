#!/usr/bin/env python3
"""
Simple QR code generator for testing the QR reader app
Usage: python generate_test_qr.py
"""

import qrcode
from PIL import Image
import os

def generate_test_qr_codes():
    """Generate test QR codes with different content types."""
    
    # Test data
    test_data = [
        ("Hello World!", "test_text.png"),
        ("https://www.google.com", "test_url.png"),
        ("mailto:test@example.com", "test_email.png"),
        ("tel:+1234567890", "test_phone.png"),
        ("WIFI:T:WPA;S:MyNetwork;P:password123;H:false;", "test_wifi.png")
    ]
    
    print("Generating test QR codes...")
    
    for data, filename in test_data:
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image
        img.save(filename)
        print(f"✅ Generated {filename} with content: {data}")
    
    print("\nTest QR codes generated successfully!")
    print("You can now test the QR reader with these files:")
    for _, filename in test_data:
        print(f"  python cli_qr_reader.py {filename}")

if __name__ == '__main__':
    generate_test_qr_codes()
