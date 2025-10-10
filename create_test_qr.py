#!/usr/bin/env python3
"""
Generate test QR codes for debugging
"""

import qrcode
from PIL import Image
import os

def generate_test_qr():
    """Generate a simple test QR code."""
    
    # Create QR code with simple text
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data("Hello World!")
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    img.save("test_qr.png")
    print("✅ Generated test_qr.png with content: Hello World!")
    print("You can now test this with the web app or CLI:")
    print("  python cli_qr_reader.py test_qr.png")

if __name__ == '__main__':
    generate_test_qr()
