# QR Code Reader App

A simple and elegant QR code reader application that can decode QR codes from uploaded images. Available as both a web application and a command-line tool.

## 🚀 Features

- 🖼️ **Image Upload**: Support for PNG, JPG, JPEG, GIF, BMP, and TIFF formats
- 🔍 **QR Code Detection**: Automatically detects and decodes QR codes in images using OpenCV
- 🌐 **Web Interface**: Beautiful, responsive web interface with drag-and-drop support
- 💻 **Command Line**: Simple CLI tool for quick QR code decoding
- 🔗 **Smart Detection**: Automatically detects URLs, emails, phone numbers, and WiFi configurations
- 📋 **Copy to Clipboard**: Easy copying of decoded content
- 🚀 **API Endpoint**: RESTful API for programmatic access

## 📦 Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## 🎯 Usage

### Web Application

1. Start the web server:
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

Examples:
```bash
python cli_qr_reader.py qr_code.png
python cli_qr_reader.py /path/to/image.jpg
```

### API Usage

Send a POST request to `/decode_base64` with a base64-encoded image:

```bash
curl -X POST http://localhost:5000/decode_base64 \
  -H "Content-Type: application/json" \
  -d '{"image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."}'
```

Response:
```json
{
  "decoded_data": ["https://example.com", "Hello World"]
}
```

## 🖼️ Supported Image Formats

- PNG
- JPG/JPEG
- GIF
- BMP
- TIFF

## 🔧 Dependencies

- Flask: Web framework
- Pillow: Image processing
- OpenCV (contrib): Computer vision with QR code detection
- NumPy: Numerical computing

## 🧪 Testing Installation

Run the test script to verify everything is working:

```bash
python test_installation.py
```

## ⚠️ Error Handling

The application includes comprehensive error handling for:
- Invalid file formats
- Corrupted images
- Missing QR codes
- Network errors (API)
- File size limits (16MB max)

## 🚀 Deployment

### Railway (Recommended - Free)

Railway offers a generous free tier perfect for this QR code reader app.

#### Quick Deploy to Railway:

1. **Push your code to GitHub:**
```bash
git add .
git commit -m "Add Railway deployment support"
git push origin main
```

2. **Deploy to Railway:**
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will auto-detect Python and deploy!

3. **Your app will be live at:** `https://your-app-name.railway.app`

#### Railway Features:
- 🆓 **Free $5/month credit** (enough for small apps)
- 🔒 **Automatic HTTPS**
- 🔧 **Environment variables support**
- 🚀 **Auto-deploy on git push**
- 📊 **Built-in monitoring**

#### Optional Environment Variables:
Set these in your Railway dashboard for production:
- `FLASK_ENV=production` (for production mode)
- `SECRET_KEY=your-secret-key` (for Flask sessions)

### Other Deployment Options

#### Heroku
```bash
# Run the deployment script
bash deploy.sh
```

#### Local Development
```bash
python app.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenCV](https://opencv.org/) for QR code detection
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Railway](https://railway.app/) for hosting

## 📊 Repository Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/qr-reader?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/qr-reader?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/qr-reader)
![GitHub license](https://img.shields.io/github/license/yourusername/qr-reader)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)