# Developer Guide - QR Code Reader Premium Platform

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [QR Code Processing](#qr-code-processing)
4. [QR Code Management](#qr-code-management)
5. [Analytics Integration](#analytics-integration)
6. [Subscription Management](#subscription-management)
7. [Rate Limiting](#rate-limiting)
8. [Error Handling](#error-handling)
9. [Best Practices](#best-practices)
10. [SDK Examples](#sdk-examples)
11. [Testing](#testing)
12. [Deployment](#deployment)

## Getting Started

### Prerequisites

- Python 3.8+ or Node.js 16+
- HTTP client library (requests, axios, etc.)
- Basic understanding of REST APIs
- QR code images for testing

### Quick Start

1. **Register for API access**
   ```bash
   curl -X POST "https://api.qrreader-premium.com/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "your@email.com", "password": "yourpassword"}'
   ```

2. **Login to get access token**
   ```bash
   curl -X POST "https://api.qrreader-premium.com/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "your@email.com", "password": "yourpassword"}'
   ```

3. **Decode your first QR code**
   ```bash
   curl -X POST "https://api.qrreader-premium.com/api/v1/qr/decode" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -F "file=@qr_code.png"
   ```

## Authentication

### JWT Token Management

The API uses JWT tokens for authentication. Tokens expire after 15 minutes for security.

```python
import requests
import time
from datetime import datetime, timedelta

class QRReaderClient:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.base_url = "https://api.qrreader-premium.com/api/v1"
    
    def login(self):
        """Login and get access token"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": self.email, "password": self.password}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.token_expires_at = datetime.now() + timedelta(minutes=15)
            return True
        return False
    
    def get_headers(self):
        """Get headers with valid token"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self.refresh_access_token()
        
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def refresh_access_token(self):
        """Refresh access token using refresh token"""
        if not self.refresh_token:
            return self.login()
        
        response = requests.post(
            f"{self.base_url}/auth/refresh",
            json={"refresh_token": self.refresh_token}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.access_token = data["access_token"]
            self.token_expires_at = datetime.now() + timedelta(minutes=15)
            return True
        else:
            return self.login()
```

### Token Security Best Practices

1. **Store tokens securely** - Never commit tokens to version control
2. **Use environment variables** for sensitive data
3. **Implement token refresh** logic to handle expiration
4. **Log out properly** by invalidating tokens

```python
import os
from dotenv import load_dotenv

load_dotenv()

# Store credentials in environment variables
EMAIL = os.getenv("QR_READER_EMAIL")
PASSWORD = os.getenv("QR_READER_PASSWORD")
```

## QR Code Processing

### Single QR Code Decoding

```python
def decode_qr_code(client, image_path):
    """Decode a single QR code from image file"""
    with open(image_path, 'rb') as f:
        files = {'file': f}
        headers = client.get_headers()
        
        response = requests.post(
            f"{client.base_url}/qr/decode",
            files=files,
            headers=headers
        )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Decode failed: {response.text}")

# Usage
client = QRReaderClient("your@email.com", "password")
client.login()

result = decode_qr_code(client, "qr_code.png")
print(f"Decoded data: {result['decoded_data']}")
```

### Batch QR Code Processing

```python
def batch_decode_qr_codes(client, image_paths):
    """Decode multiple QR codes in batch"""
    files = []
    for path in image_paths:
        files.append(('files', open(path, 'rb')))
    
    headers = client.get_headers()
    
    response = requests.post(
        f"{client.base_url}/qr/batch-decode",
        files=files,
        headers=headers
    )
    
    # Close file handles
    for _, file_handle in files:
        file_handle.close()
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Batch decode failed: {response.text}")

# Usage
image_paths = ["qr1.png", "qr2.png", "qr3.png"]
results = batch_decode_qr_codes(client, image_paths)

for result in results["results"]:
    if result["success"]:
        print(f"{result['filename']}: {result['decoded_data']}")
    else:
        print(f"{result['filename']}: Error - {result['error']}")
```

### Base64 Image Processing

```python
import base64

def decode_qr_from_base64(client, image_base64):
    """Decode QR code from base64 encoded image"""
    headers = client.get_headers()
    headers["Content-Type"] = "application/json"
    
    response = requests.post(
        f"{client.base_url}/qr/decode-base64",
        json={"image": image_base64},
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Base64 decode failed: {response.text}")

# Usage
with open("qr_code.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()
    
result = decode_qr_from_base64(client, image_data)
print(f"Decoded data: {result['decoded_data']}")
```

## QR Code Management

### Creating QR Codes

```python
def create_qr_code(client, name, data, qr_type="url", **kwargs):
    """Create a new QR code"""
    qr_data = {
        "name": name,
        "data": data,
        "qr_type": qr_type,
        "size": kwargs.get("size", 300),
        "border": kwargs.get("border", 4),
        "error_correction_level": kwargs.get("error_correction_level", "M"),
        "foreground_color": kwargs.get("foreground_color", "#000000"),
        "background_color": kwargs.get("background_color", "#FFFFFF")
    }
    
    headers = client.get_headers()
    headers["Content-Type"] = "application/json"
    
    response = requests.post(
        f"{client.base_url}/qr-codes/generate",
        json=qr_data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"QR code creation failed: {response.text}")

# Usage
qr_code = create_qr_code(
    client,
    name="My Website",
    data="https://example.com",
    qr_type="url",
    size=400,
    foreground_color="#2563eb"
)
print(f"Created QR code: {qr_code['short_url']}")
```

### Bulk QR Code Generation

```python
def bulk_create_qr_codes(client, qr_codes_data):
    """Create multiple QR codes in bulk"""
    headers = client.get_headers()
    headers["Content-Type"] = "application/json"
    
    response = requests.post(
        f"{client.base_url}/qr-codes/bulk-generate",
        json=qr_codes_data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Bulk creation failed: {response.text}")

# Usage
qr_codes_data = [
    {
        "name": "Website QR",
        "data": "https://example.com",
        "qr_type": "url"
    },
    {
        "name": "Email QR",
        "data": "mailto:contact@example.com",
        "qr_type": "email"
    },
    {
        "name": "Phone QR",
        "data": "tel:+1234567890",
        "qr_type": "phone"
    }
]

created_codes = bulk_create_qr_codes(client, qr_codes_data)
print(f"Created {len(created_codes)} QR codes")
```

### Managing QR Codes

```python
def list_qr_codes(client, page=1, limit=20, search=None):
    """List user's QR codes with pagination"""
    params = {"page": page, "limit": limit}
    if search:
        params["search"] = search
    
    headers = client.get_headers()
    
    response = requests.get(
        f"{client.base_url}/qr-codes",
        params=params,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"List QR codes failed: {response.text}")

def update_qr_code(client, qr_code_id, updates):
    """Update QR code properties"""
    headers = client.get_headers()
    headers["Content-Type"] = "application/json"
    
    response = requests.put(
        f"{client.base_url}/qr-codes/{qr_code_id}",
        json=updates,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Update failed: {response.text}")

def delete_qr_code(client, qr_code_id):
    """Delete a QR code"""
    headers = client.get_headers()
    
    response = requests.delete(
        f"{client.base_url}/qr-codes/{qr_code_id}",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Delete failed: {response.text}")

# Usage
qr_codes = list_qr_codes(client, page=1, limit=10)
for qr_code in qr_codes:
    print(f"ID: {qr_code['id']}, Name: {qr_code['name']}, Scans: {qr_code['scan_count']}")

# Update QR code
updated = update_qr_code(client, qr_code_id=1, updates={"name": "Updated Name"})

# Delete QR code
deleted = delete_qr_code(client, qr_code_id=1)
```

## Analytics Integration

### Dashboard Statistics

```python
def get_dashboard_stats(client, days=30):
    """Get dashboard statistics"""
    headers = client.get_headers()
    
    response = requests.get(
        f"{client.base_url}/analytics/dashboard",
        params={"days": days},
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Get stats failed: {response.text}")

def get_scan_history(client, page=1, limit=50, start_date=None, end_date=None):
    """Get scan history with date filtering"""
    params = {"page": page, "limit": limit}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    
    headers = client.get_headers()
    
    response = requests.get(
        f"{client.base_url}/analytics/scans",
        params=params,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Get scan history failed: {response.text}")

# Usage
stats = get_dashboard_stats(client, days=30)
print(f"Total scans: {stats['total_scans']}")
print(f"Today's scans: {stats['scans_today']}")

# Get scan history for last week
from datetime import datetime, timedelta
end_date = datetime.now()
start_date = end_date - timedelta(days=7)

history = get_scan_history(
    client,
    start_date=start_date.isoformat(),
    end_date=end_date.isoformat()
)
```

### Real-time Analytics

```python
import time
import json

def monitor_qr_scans(client, qr_code_id, callback=None):
    """Monitor QR code scans in real-time"""
    last_scan_count = 0
    
    while True:
        try:
            # Get current QR code info
            headers = client.get_headers()
            response = requests.get(
                f"{client.base_url}/qr-codes/{qr_code_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                qr_code = response.json()
                current_scan_count = qr_code["scan_count"]
                
                if current_scan_count > last_scan_count:
                    new_scans = current_scan_count - last_scan_count
                    print(f"New scans detected: {new_scans}")
                    
                    if callback:
                        callback(qr_code_id, new_scans)
                    
                    last_scan_count = current_scan_count
            
            time.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            print(f"Monitoring error: {e}")
            time.sleep(60)  # Wait longer on error

# Usage
def on_new_scan(qr_code_id, new_scans):
    print(f"QR Code {qr_code_id} has {new_scans} new scans!")

# Start monitoring
monitor_qr_scans(client, qr_code_id=1, callback=on_new_scan)
```

## Subscription Management

### Plan Management

```python
def get_subscription_plans(client):
    """Get available subscription plans"""
    response = requests.get(f"{client.base_url}/subscriptions/plans")
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Get plans failed: {response.text}")

def get_current_subscription(client):
    """Get current user subscription"""
    headers = client.get_headers()
    
    response = requests.get(
        f"{client.base_url}/subscriptions/current",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Get subscription failed: {response.text}")

def create_subscription(client, plan_id, billing_cycle="monthly", payment_method_id=None):
    """Create new subscription"""
    subscription_data = {
        "plan_id": plan_id,
        "billing_cycle": billing_cycle
    }
    
    if payment_method_id:
        subscription_data["payment_method_id"] = payment_method_id
    
    headers = client.get_headers()
    headers["Content-Type"] = "application/json"
    
    response = requests.post(
        f"{client.base_url}/subscriptions/create",
        json=subscription_data,
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Create subscription failed: {response.text}")

# Usage
plans = get_subscription_plans(client)
for plan in plans:
    print(f"Plan: {plan['name']}, Price: ${plan['price_monthly']/100}/month")

current_sub = get_current_subscription(client)
print(f"Current plan: {current_sub['plan_id']}")
```

## Rate Limiting

### Rate Limit Monitoring

```python
def get_rate_limit_usage(client):
    """Get current rate limit usage"""
    headers = client.get_headers()
    
    response = requests.get(
        f"{client.base_url}/rate-limits/usage",
        headers=headers
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Get rate limits failed: {response.text}")

def check_rate_limits_before_request(client):
    """Check rate limits before making requests"""
    usage = get_rate_limit_usage(client)
    
    current = usage["current_usage"]
    limits = usage["limits"]
    
    # Check if we're approaching limits
    if current["per_minute"] >= limits["per_minute"] * 0.9:
        print("Warning: Approaching per-minute rate limit")
        time.sleep(60)  # Wait for minute to reset
    
    if current["per_hour"] >= limits["per_hour"] * 0.9:
        print("Warning: Approaching per-hour rate limit")
        time.sleep(3600)  # Wait for hour to reset
    
    if current["per_day"] >= limits["per_day"] * 0.9:
        print("Warning: Approaching per-day rate limit")
        return False  # Stop making requests
    
    return True

# Usage
if check_rate_limits_before_request(client):
    # Make your API request
    result = decode_qr_code(client, "qr_code.png")
```

### Rate Limit Headers

```python
def make_request_with_rate_limit_check(client, method, url, **kwargs):
    """Make request with automatic rate limit handling"""
    headers = client.get_headers()
    kwargs["headers"] = headers
    
    response = requests.request(method, url, **kwargs)
    
    # Check rate limit headers
    if "X-RateLimit-Remaining" in response.headers:
        remaining = int(response.headers["X-RateLimit-Remaining"])
        limit = int(response.headers["X-RateLimit-Limit"])
        
        if remaining < limit * 0.1:  # Less than 10% remaining
            print(f"Rate limit warning: {remaining}/{limit} requests remaining")
    
    if response.status_code == 429:  # Too Many Requests
        retry_after = int(response.headers.get("Retry-After", 60))
        print(f"Rate limited. Retrying after {retry_after} seconds")
        time.sleep(retry_after)
        return make_request_with_rate_limit_check(client, method, url, **kwargs)
    
    return response
```

## Error Handling

### Comprehensive Error Handling

```python
import requests
from typing import Optional, Dict, Any

class QRReaderAPIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: int, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)

def handle_api_response(response: requests.Response) -> Dict[str, Any]:
    """Handle API response and raise appropriate exceptions"""
    if response.status_code == 200:
        return response.json()
    
    try:
        error_data = response.json()
        error_message = error_data.get("detail", "Unknown error")
        error_code = error_data.get("error_code")
    except:
        error_message = response.text or "Unknown error"
        error_code = None
    
    # Map status codes to specific error types
    if response.status_code == 400:
        raise QRReaderAPIError(f"Bad Request: {error_message}", 400, error_code)
    elif response.status_code == 401:
        raise QRReaderAPIError(f"Unauthorized: {error_message}", 401, error_code)
    elif response.status_code == 403:
        raise QRReaderAPIError(f"Forbidden: {error_message}", 403, error_code)
    elif response.status_code == 404:
        raise QRReaderAPIError(f"Not Found: {error_message}", 404, error_code)
    elif response.status_code == 422:
        raise QRReaderAPIError(f"Validation Error: {error_message}", 422, error_code)
    elif response.status_code == 429:
        raise QRReaderAPIError(f"Rate Limited: {error_message}", 429, error_code)
    elif response.status_code >= 500:
        raise QRReaderAPIError(f"Server Error: {error_message}", response.status_code, error_code)
    else:
        raise QRReaderAPIError(f"API Error: {error_message}", response.status_code, error_code)

# Usage with error handling
def safe_decode_qr_code(client, image_path):
    """Safely decode QR code with error handling"""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            headers = client.get_headers()
            
            response = requests.post(
                f"{client.base_url}/qr/decode",
                files=files,
                headers=headers
            )
        
        return handle_api_response(response)
    
    except QRReaderAPIError as e:
        print(f"API Error: {e.message} (Status: {e.status_code})")
        return None
    except FileNotFoundError:
        print(f"File not found: {image_path}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Best Practices

### 1. Connection Pooling

```python
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    """Create session with retry strategy"""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Use session for multiple requests
session = create_session_with_retries()
```

### 2. Async Processing

```python
import asyncio
import aiohttp
import aiofiles

async def async_decode_qr_codes(client, image_paths):
    """Decode multiple QR codes asynchronously"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        for image_path in image_paths:
            task = decode_single_qr_async(session, client, image_path)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

async def decode_single_qr_async(session, client, image_path):
    """Decode single QR code asynchronously"""
    async with aiofiles.open(image_path, 'rb') as f:
        data = await f.read()
        
        form_data = aiohttp.FormData()
        form_data.add_field('file', data, filename=image_path)
        
        headers = client.get_headers()
        
        async with session.post(
            f"{client.base_url}/qr/decode",
            data=form_data,
            headers=headers
        ) as response:
            return await response.json()

# Usage
results = asyncio.run(async_decode_qr_codes(client, image_paths))
```

### 3. Caching

```python
import hashlib
import json
from functools import wraps

def cache_api_response(cache_duration=300):  # 5 minutes
    """Cache API responses to reduce API calls"""
    def decorator(func):
        cache = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function arguments
            cache_key = hashlib.md5(
                json.dumps((args, kwargs), sort_keys=True).encode()
            ).hexdigest()
            
            # Check if cached result exists and is still valid
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if time.time() - timestamp < cache_duration:
                    return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = (result, time.time())
            
            return result
        
        return wrapper
    return decorator

# Usage
@cache_api_response(cache_duration=600)  # Cache for 10 minutes
def get_qr_code_info(client, qr_code_id):
    """Get QR code info with caching"""
    headers = client.get_headers()
    response = requests.get(
        f"{client.base_url}/qr-codes/{qr_code_id}",
        headers=headers
    )
    return handle_api_response(response)
```

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch
import requests

class TestQRReaderClient(unittest.TestCase):
    def setUp(self):
        self.client = QRReaderClient("test@example.com", "password")
    
    @patch('requests.post')
    def test_login_success(self, mock_post):
        """Test successful login"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_token",
            "refresh_token": "test_refresh",
            "user": {"id": 1, "email": "test@example.com"}
        }
        mock_post.return_value = mock_response
        
        result = self.client.login()
        self.assertTrue(result)
        self.assertEqual(self.client.access_token, "test_token")
    
    @patch('requests.post')
    def test_login_failure(self, mock_post):
        """Test login failure"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"detail": "Invalid credentials"}
        mock_post.return_value = mock_response
        
        result = self.client.login()
        self.assertFalse(result)
    
    @patch('requests.post')
    def test_decode_qr_code(self, mock_post):
        """Test QR code decoding"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "decoded_data": ["https://example.com"],
            "scan_id": 123
        }
        mock_post.return_value = mock_response
        
        result = decode_qr_code(self.client, "test.png")
        self.assertTrue(result["success"])
        self.assertEqual(result["decoded_data"], ["https://example.com"])

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests

```python
import pytest
import tempfile
import os
from PIL import Image
import qrcode

@pytest.fixture
def test_client():
    """Create test client"""
    client = QRReaderClient("test@example.com", "password")
    client.login()
    return client

@pytest.fixture
def test_qr_image():
    """Create test QR code image"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data("https://example.com")
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_file.name)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    os.unlink(temp_file.name)

def test_decode_real_qr_code(test_client, test_qr_image):
    """Test decoding real QR code"""
    result = decode_qr_code(test_client, test_qr_image)
    
    assert result["success"] == True
    assert "https://example.com" in result["decoded_data"]

def test_batch_decode_multiple_qr_codes(test_client):
    """Test batch decoding multiple QR codes"""
    # Create multiple test QR codes
    test_images = []
    for i in range(3):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f"https://example{i}.com")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_file.name)
        temp_file.close()
        test_images.append(temp_file.name)
    
    try:
        result = batch_decode_qr_codes(test_client, test_images)
        
        assert result["success"] == True
        assert result["total_files"] == 3
        assert result["processed_files"] == 3
        
        for i, qr_result in enumerate(result["results"]):
            assert qr_result["success"] == True
            assert f"https://example{i}.com" in qr_result["decoded_data"]
    
    finally:
        # Cleanup
        for temp_file in test_images:
            os.unlink(temp_file)
```

## Deployment

### Docker Configuration

```dockerfile
# Dockerfile for QR Reader API client
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV QR_READER_API_URL=https://api.qrreader-premium.com/api/v1

# Run application
CMD ["python", "main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  qr-reader-client:
    build: .
    environment:
      - QR_READER_EMAIL=${QR_READER_EMAIL}
      - QR_READER_PASSWORD=${QR_READER_PASSWORD}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

### Production Configuration

```python
# config.py
import os
from typing import Optional

class Config:
    # API Configuration
    API_BASE_URL: str = os.getenv("QR_READER_API_URL", "https://api.qrreader-premium.com/api/v1")
    API_TIMEOUT: int = int(os.getenv("QR_READER_API_TIMEOUT", "30"))
    
    # Authentication
    EMAIL: str = os.getenv("QR_READER_EMAIL")
    PASSWORD: str = os.getenv("QR_READER_PASSWORD")
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "50"))
    MAX_REQUESTS_PER_HOUR: int = int(os.getenv("MAX_REQUESTS_PER_HOUR", "500"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # Caching
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.EMAIL:
            raise ValueError("QR_READER_EMAIL is required")
        if not cls.PASSWORD:
            raise ValueError("QR_READER_PASSWORD is required")
```

### Monitoring and Logging

```python
import logging
import json
from datetime import datetime

def setup_logging(config):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.LOG_FILE) if config.LOG_FILE else logging.NullHandler()
        ]
    )

def log_api_request(method: str, url: str, status_code: int, response_time: float):
    """Log API request details"""
    logger = logging.getLogger("qr_reader_api")
    
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "method": method,
        "url": url,
        "status_code": status_code,
        "response_time_ms": response_time * 1000
    }
    
    logger.info(json.dumps(log_data))

# Usage in client
def make_logged_request(client, method, url, **kwargs):
    """Make request with logging"""
    start_time = time.time()
    
    try:
        response = requests.request(method, url, **kwargs)
        response_time = time.time() - start_time
        
        log_api_request(method, url, response.status_code, response_time)
        
        return response
    
    except Exception as e:
        response_time = time.time() - start_time
        log_api_request(method, url, 0, response_time)
        raise
```

This comprehensive developer guide provides everything needed to integrate with the QR Code Reader Premium Platform API effectively and efficiently.
