from flask import Flask, render_template, request, jsonify, flash, redirect, url_for, send_from_directory
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

def context_crop(image, box):
    """Crop image with context and return as base64."""
    try:
        # box is (left, top, right, bottom)
        crop = image.crop(box)
        
        # Resize if too small to be visible
        if crop.width < 100 or crop.height < 100:
            scale = max(100/crop.width, 100/crop.height)
            new_size = (int(crop.width * scale), int(crop.height * scale))
            crop = crop.resize(new_size, Image.Resampling.LANCZOS)
            
        buffered = io.BytesIO()
        crop.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error creating crop: {e}")
        return None

def decode_with_zxing(image_path):
    """Decode QR code using zxing-cpp library."""
    try:
        import zxingcpp
        
        # Read image
        image = Image.open(image_path)
        
        # Convert to grayscale if needed
        if image.mode != 'L':
            gray_image = image.convert('L')
        else:
            gray_image = image
        
        # Convert PIL image to numpy array
        img_array = np.array(gray_image)
        
        # Try to decode
        results = zxingcpp.read_barcodes(img_array)
        
        if results:
            decoded_items = []
            for result in results:
                if result.format == zxingcpp.BarcodeFormat.QRCode:
                    # Calculate bounding box from position
                    # result.position is usually an object with top_left, top_right, etc. or a simplified string
                    # We'll try to get coordinates regardless of the specific zxing-cpp version structure
                    try:
                        pts = [(p.x, p.y) for p in [result.position.top_left, result.position.top_right, result.position.bottom_right, result.position.bottom_left]]
                        min_x = min(p[0] for p in pts)
                        max_x = max(p[0] for p in pts)
                        min_y = min(p[1] for p in pts)
                        max_y = max(p[1] for p in pts)
                        box = (min_x, min_y, max_x, max_y)
                        crop_b64 = context_crop(image, box)
                    except:
                        crop_b64 = None

                    decoded_items.append({
                        'text': result.text,
                        'crop': crop_b64,
                        'confidence': 'High (ZXing)'
                    })
            return decoded_items if decoded_items else None
        
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
            gray_image = image.convert('L')
        else:
            gray_image = image
        
        # Try to decode
        qr_codes = pyzbar.decode(gray_image)
        
        if qr_codes:
            decoded_items = []
            for qr_code in qr_codes:
                # pyzbar returns rect
                rect = qr_code.rect
                box = (rect.left, rect.top, rect.left + rect.width, rect.top + rect.height)
                crop_b64 = context_crop(image, box)
                
                decoded_items.append({
                    'text': qr_code.data.decode('utf-8'),
                    'crop': crop_b64,
                    'confidence': 'High (PyZbar)'
                })
            return decoded_items
        
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
        
        # Save temp file to reuse existing valid logic or refactor
        # Ideally we should refactor decode functions to take image object, but file path is required to match current signatures
        # For memory efficiency, let's adapt the inner logic instead of saving files
        
        # First try zxing-cpp
        try:
            import zxingcpp
            
            if image.mode != 'L':
                image_gray = image.convert('L')
            else:
                image_gray = image
            
            img_array = np.array(image_gray)
            results = zxingcpp.read_barcodes(img_array)
            
            if results:
                decoded_items = []
                for result in results:
                    if result.format == zxingcpp.BarcodeFormat.QRCode:
                        try:
                            pts = [(p.x, p.y) for p in [result.position.top_left, result.position.top_right, result.position.bottom_right, result.position.bottom_left]]
                            min_x = min(p[0] for p in pts)
                            max_x = max(p[0] for p in pts)
                            min_y = min(p[1] for p in pts)
                            max_y = max(p[1] for p in pts)
                            box = (min_x, min_y, max_x, max_y)
                            crop_b64 = context_crop(image, box)
                        except:
                            crop_b64 = None
                            
                        decoded_items.append({
                            'text': result.text,
                            'crop': crop_b64,
                            'confidence': 'High (ZXing)'
                        })
                if decoded_items:
                    return decoded_items, None
        except ImportError:
            pass
        except Exception as e:
            print(f"zxing-cpp error: {e}")
        
        # Fallback to pyzbar
        try:
            from pyzbar import pyzbar
            
            if image.mode != 'L':
                image_gray = image.convert('L')
            else:
                image_gray = image
            
            qr_codes = pyzbar.decode(image_gray)
            
            if qr_codes:
                decoded_items = []
                for qr_code in qr_codes:
                    rect = qr_code.rect
                    box = (rect.left, rect.top, rect.left + rect.width, rect.top + rect.height)
                    crop_b64 = context_crop(image, box)
                    
                    decoded_items.append({
                        'text': qr_code.data.decode('utf-8'),
                        'crop': crop_b64,
                        'confidence': 'High (PyZbar)'
                    })
                return decoded_items, None
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

@app.route('/robots.txt')
def robots():
    """Serve robots.txt."""
    return send_from_directory(app.static_folder if app.static_folder else '.', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    """Serve sitemap.xml."""
    return send_from_directory(app.static_folder if app.static_folder else '.', 'sitemap.xml')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon.ico."""
    return send_from_directory(app.static_folder if app.static_folder else 'static',
                             'favicon.png', mimetype='image/vnd.microsoft.icon')

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
    port = int(os.environ.get('PORT', 5000))
    # Default to production mode (debug=False) unless explicitly set to 'development'
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)