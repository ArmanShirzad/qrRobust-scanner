# QR Code Scanner V1

A Flask-based web application for reading QR codes from images and PDFs.

## Features

- **Image Upload**: Support for PNG, JPG, JPEG, GIF, BMP, and TIFF formats
- **QR Code Detection**: Automatically detects and decodes QR codes
- **Web Interface**: Beautiful, responsive web interface with drag-and-drop support
- **Command Line**: Simple CLI tool for quick QR code decoding
- **Smart Detection**: Automatically detects URLs, emails, phone numbers, and WiFi configurations
- **Copy to Clipboard**: Easy copying of decoded content
- **API Endpoint**: RESTful API for programmatic access

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ArmanShirzad/qrRobust-scanner.git
cd qrRobust-scanner
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Web Application
1. Start the server:
```bash
python app.py
```

2. Open your browser and go to `http://localhost:5000`

3. Upload an image containing a QR code by:
   - Clicking the upload area and selecting a file
   - Dragging and dropping an image onto the upload area

4. View the decoded content on the results page

### Command Line Interface
```bash
python cli_qr_reader.py <image_path>
```

### API Usage
Send a POST request to `/decode_base64` with a base64-encoded image:

```bash
curl -X POST http://localhost:5000/decode_base64 \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."}'
```

## Deploy to Heroku

1. **Install Heroku CLI** and login:
   ```bash
   heroku login
   ```

2. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

3. **Add required buildpacks**:
   ```bash
   heroku buildpacks:add --index 1 heroku-community/apt
   heroku buildpacks:add --index 2 heroku/python
   ```

4. **Deploy**:
   ```bash
   git push heroku main
   ```

## Dependencies

- Flask: Web framework
- Pillow: Image processing
- Pyzbar: QR code decoding (requires libzbar0)
- NumPy: Numerical computing

## Testing Installation

```bash
python test_installation.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Pyzbar](https://github.com/NaturalHistoryMuseum/pyzbar) for QR code decoding
