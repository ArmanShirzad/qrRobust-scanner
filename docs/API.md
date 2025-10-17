# API Reference

## Authentication

All API endpoints require authentication unless otherwise specified. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Base URL

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-app.vercel.app/api/v1`

## Endpoints

### Authentication

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true,
    "is_verified": false,
    "tier": "free"
  }
}
```

#### POST /auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

### QR Codes

#### POST /qr-codes/
Create a new QR code.

**Request Body:**
```json
{
  "destination_url": "https://example.com",
  "title": "My QR Code",
  "description": "QR code for my website",
  "error_correction_level": "M",
  "size": 10,
  "border": 4,
  "foreground_color": "#000000",
  "background_color": "#FFFFFF"
}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 1,
  "short_url": "abc123",
  "destination_url": "https://example.com",
  "title": "My QR Code",
  "description": "QR code for my website",
  "scan_count": 0,
  "created_at": "2024-12-19T10:00:00Z",
  "is_active": true
}
```

#### GET /qr-codes/my-codes
Get all QR codes for the authenticated user.

**Response:**
```json
[
  {
    "id": 1,
    "short_url": "abc123",
    "destination_url": "https://example.com",
    "title": "My QR Code",
    "scan_count": 5,
    "created_at": "2024-12-19T10:00:00Z"
  }
]
```

### Analytics

#### GET /analytics/dashboard
Get dashboard analytics for the authenticated user.

**Response:**
```json
{
  "total_scans": 150,
  "scans_today": 12,
  "unique_qr_codes": 5,
  "top_qr_codes": [
    {
      "content": "https://example.com",
      "scan_count": 45
    }
  ],
  "device_stats": [
    {
      "device_type": "mobile",
      "count": 80
    },
    {
      "device_type": "desktop",
      "count": 70
    }
  ]
}
```

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error type",
  "message": "Detailed error message",
  "details": "Additional error details (optional)"
}
```

### Common Error Codes

- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

## Rate Limiting

API requests are rate limited based on user subscription tier:

- **Free**: 60 requests/hour
- **Pro**: 1,000 requests/hour
- **Business**: 5,000 requests/hour
- **Enterprise**: Unlimited

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## SDKs and Libraries

### Python
```bash
pip install qr-reader-premium-sdk
```

```python
from qr_reader_premium import QRReaderClient

client = QRReaderClient(api_key="your-api-key")
qr_code = client.create_qr_code("https://example.com")
```

### JavaScript
```bash
npm install qr-reader-premium-sdk
```

```javascript
import { QRReaderClient } from 'qr-reader-premium-sdk';

const client = new QRReaderClient('your-api-key');
const qrCode = await client.createQRCode('https://example.com');
```

## Webhooks

Configure webhooks to receive real-time notifications about QR code scans and other events.

### Webhook Events

- `qr_code.scanned` - QR code was scanned
- `qr_code.created` - New QR code was created
- `qr_code.updated` - QR code was updated
- `user.subscribed` - User upgraded subscription

### Webhook Payload

```json
{
  "event": "qr_code.scanned",
  "timestamp": "2024-12-19T10:00:00Z",
  "data": {
    "qr_code_id": 1,
    "scan_timestamp": "2024-12-19T10:00:00Z",
    "ip_address": "192.168.1.1",
    "user_agent": "Mozilla/5.0...",
    "country": "US"
  }
}
```
