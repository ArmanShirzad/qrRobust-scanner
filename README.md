# QR Code Reader - Portfolio Version

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![OpenCV](https://img.shields.io/badge/opencv-4.0+-red.svg)](https://opencv.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Railway](https://img.shields.io/badge/deployed%20on-Railway-0B0D0E.svg)](https://railway.app/)

A Flask-based web application for reading QR codes from images and PDFs.

## Features
- Upload and decode QR codes from images (PNG, JPG, JPEG, GIF, BMP, TIFF)
- Batch processing of multiple QR codes
- PDF QR code extraction
- WiFi QR code generation
- RESTful API endpoints
- Clean, responsive web interface

## Live Demo
Visit the deployed version at: [Your Railway App URL]

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/qr-reader.git
   cd qr-reader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:5000`

## API Endpoints

- `POST /api/decode` - Decode QR code from uploaded image
- `POST /api/batch` - Process multiple QR codes
- `GET /api/docs` - API documentation

## Technologies Used
- **Backend**: Flask, Python
- **QR Processing**: zxing-cpp, qrcode
- **Image Processing**: PIL (Pillow)
- **PDF Processing**: PyPDF2
- **Frontend**: HTML, CSS, JavaScript
- **Deployment**: Railway

## Project Structure
```
├── app.py              # Main Flask application
├── templates/          # HTML templates
├── static/            # CSS and JavaScript files
├── uploads/           # Uploaded files directory
├── requirements.txt   # Python dependencies
└── railway.json      # Railway deployment config
```

## Contributing
This is a portfolio project. For development features, see the `feature/update` branch.

## License
MIT License - feel free to use this code for your own projects!