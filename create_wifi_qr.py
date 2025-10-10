#!/usr/bin/env python3
"""
Create a clean WiFi QR code without logo
"""

import qrcode
from PIL import Image

def create_wifi_qr(ssid, password, security_type="WPA", hidden="false"):
    """
    Create a WiFi QR code without logo
    
    Args:
        ssid: Network name
        password: WiFi password
        security_type: WPA, WEP, or nopass
        hidden: true or false
    """
    
    # Format: WIFI:T:WPA;S:NetworkName;P:Password;H:false;
    wifi_string = f"WIFI:T:{security_type};S:{ssid};P:{password};H:{hidden};"
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(wifi_string)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save image
    filename = f"wifi_{ssid.replace(' ', '_')}.png"
    img.save(filename)
    
    print(f"✅ Created clean WiFi QR code: {filename}")
    print(f"WiFi String: {wifi_string}")
    print(f"You can now test this with: python cli_qr_reader.py {filename}")
    
    return filename

if __name__ == '__main__':
    # Example usage - replace with your actual WiFi details
    print("WiFi QR Code Generator")
    print("=" * 30)
    
    # You can modify these values
    ssid = "MyNetwork"
    password = "mypassword123"
    security_type = "WPA"  # WPA, WEP, or nopass
    hidden = "false"       # true or false
    
    create_wifi_qr(ssid, password, security_type, hidden)
