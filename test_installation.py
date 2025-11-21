#!/usr/bin/env python3
"""
Test script to verify QR code reader installation
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported."""
    try:
        import flask
        print("✅ Flask imported successfully")
    except ImportError:
        print("❌ Flask not found. Run: pip install Flask")
        return False
    
    try:
        from pyzbar import pyzbar
        print("✅ pyzbar imported successfully")
    except ImportError:
        print("❌ pyzbar not found. Run: pip install pyzbar")
        return False

    try:
        import zxingcpp
        print("✅ zxing-cpp imported successfully")
    except ImportError:
        print("❌ zxing-cpp not found. Run: pip install zxing-cpp")
        return False
    
    try:
        from PIL import Image
        print("✅ Pillow imported successfully")
    except ImportError:
        print("❌ Pillow not found. Run: pip install Pillow")
        return False
    
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
    except ImportError:
        print("❌ NumPy not found. Run: pip install numpy")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist."""
    required_files = [
        'app.py',
        'cli_qr_reader.py',
        'requirements.txt',
        'templates/index.html',
        'templates/result.html',
        'README.md'
    ]
    
    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Main test function."""
    print("QR Code Reader - Installation Test")
    print("=" * 40)
    
    print("\nTesting imports...")
    imports_ok = test_imports()
    
    print("\nTesting file structure...")
    files_ok = test_file_structure()
    
    print("\n" + "=" * 40)
    if imports_ok and files_ok:
        print("🎉 All tests passed! Installation is complete.")
        print("\nTo start the web app, run:")
        print("  python app.py")
        print("\nTo use the CLI tool, run:")
        print("  python cli_qr_reader.py <image_path>")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
