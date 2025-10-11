from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
import cv2
import numpy as np
import io
import base64

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def decode_with_zxing(image_path):
    """Decode QR code using zxing-cpp library."""
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
            decoded_data = []
            for result in results:
                if result.format == zxingcpp.BarcodeFormat.QRCode:
                    decoded_data.append(result.text)
            return decoded_data if decoded_data else None
        
        return None
        
    except ImportError:
        return None
    except Exception as e:
        print(f"zxing-cpp error: {e}")
        return None

def decode_qr_code(image_path):
    """Decode QR code from image file using multiple detection methods."""
    try:
        # First try zxing-cpp (better for QR codes with logos)
        zxing_result = decode_with_zxing(image_path)
        if zxing_result:
            return zxing_result, None
        
        # Fallback to OpenCV methods
        # Read the image
        image = cv2.imread(image_path)
        
        if image is None:
            return None, "Could not read the image file"
        
        # Try multiple approaches for better detection
        qr_detector = cv2.QRCodeDetector()
        
        # First attempt: direct detection
        data, bbox, _ = qr_detector.detectAndDecode(image)
        
        if data:
            return [data], None
        
        # Second attempt: convert to grayscale and try again
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = qr_detector.detectAndDecode(gray)
        
        if data:
            return [data], None
        
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
            return [data], None
        
        return None, "No QR code found in the image. Try using a clearer image with better contrast."
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

def decode_qr_from_base64(base64_string):
    """Decode QR code from base64 encoded image using multiple detection methods."""
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        image_data = base64.b64decode(base64_string)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # First try zxing-cpp
        try:
            import zxingcpp
            
            # Convert to grayscale if needed
            if image.mode != 'L':
                image_gray = image.convert('L')
            else:
                image_gray = image
            
            # Convert PIL image to numpy array
            img_array = np.array(image_gray)
            
            # Try to decode
            results = zxingcpp.read_barcodes(img_array)
            
            if results:
                decoded_data = []
                for result in results:
                    if result.format == zxingcpp.BarcodeFormat.QRCode:
                        decoded_data.append(result.text)
                if decoded_data:
                    return decoded_data, None
        except ImportError:
            pass
        except Exception as e:
            print(f"zxing-cpp error: {e}")
        
        # Fallback to OpenCV methods
        # Convert to OpenCV format
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Try multiple approaches for better detection
        qr_detector = cv2.QRCodeDetector()
        
        # First attempt: direct detection
        data, bbox, _ = qr_detector.detectAndDecode(opencv_image)
        
        if data:
            return [data], None
        
        # Second attempt: convert to grayscale and try again
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        data, bbox, _ = qr_detector.detectAndDecode(gray)
        
        if data:
            return [data], None
        
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
            return [data], None
        
        return None, "No QR code found in the image. Try using a clearer image with better contrast."
        
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

@app.route('/')
def index():
    """Main page with upload form."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and QR code decoding."""
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('No file selected')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Decode QR code
        decoded_data, error = decode_qr_code(filepath)
        
        # Clean up uploaded file
        os.remove(filepath)
        
        if error:
            flash(f'Error: {error}')
            return redirect(url_for('index'))
        
        return render_template('result.html', 
                             decoded_data=decoded_data, 
                             filename=filename)
    else:
        flash('Invalid file type. Please upload an image file.')
        return redirect(url_for('index'))

@app.route('/decode_base64', methods=['POST'])
def decode_base64():
    """Handle base64 image decoding via API."""
    try:
        data = request.get_json()
        base64_image = data.get('image')
        
        if not base64_image:
            return jsonify({'error': 'No image data provided'}), 400
        
        decoded_data, error = decode_qr_from_base64(base64_image)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({'decoded_data': decoded_data})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
