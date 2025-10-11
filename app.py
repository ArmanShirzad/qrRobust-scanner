from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
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

def decode_with_pyzbar(image_path):
    """Decode QR code using pyzbar library."""
    try:
        from pyzbar import pyzbar
        
        # Read image
        image = Image.open(image_path)
        
        # Convert to grayscale if needed
        if image.mode != 'L':
            image = image.convert('L')
        
        # Try to decode
        qr_codes = pyzbar.decode(image)
        
        if qr_codes:
            decoded_data = []
            for qr_code in qr_codes:
                decoded_data.append(qr_code.data.decode('utf-8'))
            return decoded_data
        
        return None
        
    except ImportError:
        return None
    except Exception as e:
        print(f"pyzbar error: {e}")
        return None

def decode_qr_code(image_path):
    """Decode QR code from image file using multiple detection methods."""
    try:
        # First try zxing-cpp (best for QR codes with logos)
        zxing_result = decode_with_zxing(image_path)
        if zxing_result:
            return zxing_result, None
        
        # Fallback to pyzbar
        pyzbar_result = decode_with_pyzbar(image_path)
        if pyzbar_result:
            return pyzbar_result, None
        
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
        
        # Fallback to pyzbar
        try:
            from pyzbar import pyzbar
            
            # Convert to grayscale if needed
            if image.mode != 'L':
                image_gray = image.convert('L')
            else:
                image_gray = image
            
            # Try to decode
            qr_codes = pyzbar.decode(image_gray)
            
            if qr_codes:
                decoded_data = []
                for qr_code in qr_codes:
                    decoded_data.append(qr_code.data.decode('utf-8'))
                return decoded_data, None
        except ImportError:
            pass
        except Exception as e:
            print(f"pyzbar error: {e}")
        
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
    # Railway deployment configuration
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)