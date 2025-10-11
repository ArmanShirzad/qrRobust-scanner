# SDK Examples and Code Samples

## Python SDK

### Complete Python Client

```python
# qr_reader_sdk.py
import requests
import time
import base64
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

class QRReaderSDK:
    """Complete Python SDK for QR Code Reader Premium Platform"""
    
    def __init__(self, email: str, password: str, base_url: str = None):
        self.email = email
        self.password = password
        self.base_url = base_url or "https://api.qrreader-premium.com/api/v1"
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.session = requests.Session()
        
        # Setup retry strategy
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with valid token"""
        if not self.access_token or datetime.now() >= self.token_expires_at:
            self._refresh_token()
        
        return {"Authorization": f"Bearer {self.access_token}"}
    
    def _refresh_token(self) -> bool:
        """Refresh access token"""
        if not self.refresh_token:
            return self.login()
        
        try:
            response = self.session.post(
                f"{self.base_url}/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.token_expires_at = datetime.now() + timedelta(minutes=15)
                return True
        except Exception as e:
            self.logger.error(f"Token refresh failed: {e}")
        
        return self.login()
    
    def login(self) -> bool:
        """Login and get access token"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": self.email, "password": self.password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                self.token_expires_at = datetime.now() + timedelta(minutes=15)
                self.logger.info("Login successful")
                return True
            else:
                self.logger.error(f"Login failed: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def register(self, email: str, password: str) -> bool:
        """Register new user"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/register",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                self.logger.info("Registration successful")
                return True
            else:
                self.logger.error(f"Registration failed: {response.text}")
                return False
        except Exception as e:
            self.logger.error(f"Registration error: {e}")
            return False
    
    def decode_qr_code(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Decode QR code from image file"""
        try:
            with open(image_path, 'rb') as f:
                files = {'file': f}
                headers = self._get_headers()
                
                response = self.session.post(
                    f"{self.base_url}/qr/decode",
                    files=files,
                    headers=headers
                )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Decode failed: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Decode error: {e}")
            return None
    
    def decode_qr_base64(self, image_base64: str) -> Optional[Dict[str, Any]]:
        """Decode QR code from base64 image"""
        try:
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            
            response = self.session.post(
                f"{self.base_url}/qr/decode-base64",
                json={"image": image_base64},
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Base64 decode failed: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Base64 decode error: {e}")
            return None
    
    def batch_decode_qr_codes(self, image_paths: List[str]) -> Optional[Dict[str, Any]]:
        """Decode multiple QR codes in batch"""
        try:
            files = []
            for path in image_paths:
                files.append(('files', open(path, 'rb')))
            
            headers = self._get_headers()
            
            response = self.session.post(
                f"{self.base_url}/qr/batch-decode",
                files=files,
                headers=headers
            )
            
            # Close file handles
            for _, file_handle in files:
                file_handle.close()
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Batch decode failed: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Batch decode error: {e}")
            return None
    
    def create_qr_code(self, name: str, data: str, qr_type: str = "url", **kwargs) -> Optional[Dict[str, Any]]:
        """Create a new QR code"""
        try:
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
            
            headers = self._get_headers()
            headers["Content-Type"] = "application/json"
            
            response = self.session.post(
                f"{self.base_url}/qr-codes/generate",
                json=qr_data,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"QR code creation failed: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"QR code creation error: {e}")
            return None
    
    def list_qr_codes(self, page: int = 1, limit: int = 20, search: str = None) -> Optional[Dict[str, Any]]:
        """List user's QR codes"""
        try:
            params = {"page": page, "limit": limit}
            if search:
                params["search"] = search
            
            headers = self._get_headers()
            
            response = self.session.get(
                f"{self.base_url}/qr-codes",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"List QR codes failed: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"List QR codes error: {e}")
            return None
    
    def get_dashboard_stats(self, days: int = 30) -> Optional[Dict[str, Any]]:
        """Get dashboard statistics"""
        try:
            headers = self._get_headers()
            
            response = self.session.get(
                f"{self.base_url}/analytics/dashboard",
                params={"days": days},
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Get stats failed: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Get stats error: {e}")
            return None
    
    def get_rate_limit_usage(self) -> Optional[Dict[str, Any]]:
        """Get rate limit usage"""
        try:
            headers = self._get_headers()
            
            response = self.session.get(
                f"{self.base_url}/rate-limits/usage",
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.logger.error(f"Get rate limits failed: {response.text}")
                return None
        except Exception as e:
            self.logger.error(f"Get rate limits error: {e}")
            return None

# Usage example
if __name__ == "__main__":
    # Initialize SDK
    sdk = QRReaderSDK("your@email.com", "yourpassword")
    
    # Login
    if sdk.login():
        print("Login successful!")
        
        # Decode QR code
        result = sdk.decode_qr_code("qr_code.png")
        if result:
            print(f"Decoded data: {result['decoded_data']}")
        
        # Create QR code
        qr_code = sdk.create_qr_code(
            name="My Website",
            data="https://example.com",
            qr_type="url",
            size=400
        )
        if qr_code:
            print(f"Created QR code: {qr_code['short_url']}")
        
        # Get dashboard stats
        stats = sdk.get_dashboard_stats()
        if stats:
            print(f"Total scans: {stats['total_scans']}")
```

### Async Python Client

```python
# async_qr_reader_sdk.py
import aiohttp
import asyncio
import aiofiles
from typing import Optional, List, Dict, Any
import logging

class AsyncQRReaderSDK:
    """Async Python SDK for QR Code Reader Premium Platform"""
    
    def __init__(self, email: str, password: str, base_url: str = None):
        self.email = email
        self.password = password
        self.base_url = base_url or "https://api.qrreader-premium.com/api/v1"
        self.access_token = None
        self.refresh_token = None
        self.session = None
        self.logger = logging.getLogger(__name__)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        await self.login()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def login(self) -> bool:
        """Login and get access token"""
        try:
            async with self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": self.email, "password": self.password}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.access_token = data["access_token"]
                    self.refresh_token = data["refresh_token"]
                    self.logger.info("Login successful")
                    return True
                else:
                    self.logger.error(f"Login failed: {await response.text()}")
                    return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with token"""
        return {"Authorization": f"Bearer {self.access_token}"}
    
    async def decode_qr_code(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Decode QR code from image file"""
        try:
            async with aiofiles.open(image_path, 'rb') as f:
                data = await f.read()
                
                form_data = aiohttp.FormData()
                form_data.add_field('file', data, filename=image_path)
                
                headers = self._get_headers()
                
                async with self.session.post(
                    f"{self.base_url}/qr/decode",
                    data=form_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        self.logger.error(f"Decode failed: {await response.text()}")
                        return None
        except Exception as e:
            self.logger.error(f"Decode error: {e}")
            return None
    
    async def batch_decode_qr_codes(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Decode multiple QR codes concurrently"""
        tasks = []
        for image_path in image_paths:
            task = self.decode_qr_code(image_path)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results

# Usage example
async def main():
    async with AsyncQRReaderSDK("your@email.com", "yourpassword") as sdk:
        # Decode single QR code
        result = await sdk.decode_qr_code("qr_code.png")
        if result:
            print(f"Decoded data: {result['decoded_data']}")
        
        # Decode multiple QR codes concurrently
        image_paths = ["qr1.png", "qr2.png", "qr3.png"]
        results = await sdk.batch_decode_qr_codes(image_paths)
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and result.get("success"):
                print(f"QR {i+1}: {result['decoded_data']}")
            else:
                print(f"QR {i+1}: Failed to decode")

if __name__ == "__main__":
    asyncio.run(main())
```

## JavaScript/Node.js SDK

### Complete Node.js Client

```javascript
// qr-reader-sdk.js
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

class QRReaderSDK {
    constructor(email, password, baseUrl = 'https://api.qrreader-premium.com/api/v1') {
        this.email = email;
        this.password = password;
        this.baseUrl = baseUrl;
        this.accessToken = null;
        this.refreshToken = null;
        this.tokenExpiresAt = null;
        
        // Create axios instance with retry logic
        this.client = axios.create({
            baseURL: this.baseUrl,
            timeout: 30000,
        });
        
        // Add request interceptor for token refresh
        this.client.interceptors.request.use(
            async (config) => {
                if (this.accessToken && new Date() < this.tokenExpiresAt) {
                    config.headers.Authorization = `Bearer ${this.accessToken}`;
                } else {
                    await this.refreshToken();
                    if (this.accessToken) {
                        config.headers.Authorization = `Bearer ${this.accessToken}`;
                    }
                }
                return config;
            },
            (error) => Promise.reject(error)
        );
        
        // Add response interceptor for error handling
        this.client.interceptors.response.use(
            (response) => response,
            async (error) => {
                if (error.response?.status === 401) {
                    await this.refreshToken();
                    // Retry the original request
                    return this.client.request(error.config);
                }
                return Promise.reject(error);
            }
        );
    }
    
    async login() {
        try {
            const response = await this.client.post('/auth/login', {
                email: this.email,
                password: this.password
            });
            
            if (response.status === 200) {
                const data = response.data;
                this.accessToken = data.access_token;
                this.refreshToken = data.refresh_token;
                this.tokenExpiresAt = new Date(Date.now() + 15 * 60 * 1000); // 15 minutes
                console.log('Login successful');
                return true;
            }
            return false;
        } catch (error) {
            console.error('Login error:', error.message);
            return false;
        }
    }
    
    async refreshToken() {
        if (!this.refreshToken) {
            return this.login();
        }
        
        try {
            const response = await this.client.post('/auth/refresh', {
                refresh_token: this.refreshToken
            });
            
            if (response.status === 200) {
                const data = response.data;
                this.accessToken = data.access_token;
                this.tokenExpiresAt = new Date(Date.now() + 15 * 60 * 1000);
                return true;
            }
        } catch (error) {
            console.error('Token refresh failed:', error.message);
        }
        
        return this.login();
    }
    
    async decodeQRCode(imagePath) {
        try {
            const formData = new FormData();
            formData.append('file', fs.createReadStream(imagePath));
            
            const response = await this.client.post('/qr/decode', formData, {
                headers: {
                    ...formData.getHeaders(),
                },
            });
            
            return response.data;
        } catch (error) {
            console.error('Decode error:', error.message);
            return null;
        }
    }
    
    async decodeQRBase64(imageBase64) {
        try {
            const response = await this.client.post('/qr/decode-base64', {
                image: imageBase64
            });
            
            return response.data;
        } catch (error) {
            console.error('Base64 decode error:', error.message);
            return null;
        }
    }
    
    async batchDecodeQRCodes(imagePaths) {
        try {
            const formData = new FormData();
            imagePaths.forEach(imagePath => {
                formData.append('files', fs.createReadStream(imagePath));
            });
            
            const response = await this.client.post('/qr/batch-decode', formData, {
                headers: {
                    ...formData.getHeaders(),
                },
            });
            
            return response.data;
        } catch (error) {
            console.error('Batch decode error:', error.message);
            return null;
        }
    }
    
    async createQRCode(name, data, qrType = 'url', options = {}) {
        try {
            const qrData = {
                name,
                data,
                qr_type: qrType,
                size: options.size || 300,
                border: options.border || 4,
                error_correction_level: options.errorCorrectionLevel || 'M',
                foreground_color: options.foregroundColor || '#000000',
                background_color: options.backgroundColor || '#FFFFFF'
            };
            
            const response = await this.client.post('/qr-codes/generate', qrData);
            return response.data;
        } catch (error) {
            console.error('Create QR code error:', error.message);
            return null;
        }
    }
    
    async listQRCodes(page = 1, limit = 20, search = null) {
        try {
            const params = { page, limit };
            if (search) params.search = search;
            
            const response = await this.client.get('/qr-codes', { params });
            return response.data;
        } catch (error) {
            console.error('List QR codes error:', error.message);
            return null;
        }
    }
    
    async getDashboardStats(days = 30) {
        try {
            const response = await this.client.get('/analytics/dashboard', {
                params: { days }
            });
            return response.data;
        } catch (error) {
            console.error('Get dashboard stats error:', error.message);
            return null;
        }
    }
    
    async getRateLimitUsage() {
        try {
            const response = await this.client.get('/rate-limits/usage');
            return response.data;
        } catch (error) {
            console.error('Get rate limit usage error:', error.message);
            return null;
        }
    }
}

// Usage example
async function main() {
    const sdk = new QRReaderSDK('your@email.com', 'yourpassword');
    
    // Login
    if (await sdk.login()) {
        console.log('Login successful!');
        
        // Decode QR code
        const result = await sdk.decodeQRCode('qr_code.png');
        if (result) {
            console.log('Decoded data:', result.decoded_data);
        }
        
        // Create QR code
        const qrCode = await sdk.createQRCode(
            'My Website',
            'https://example.com',
            'url',
            { size: 400, foregroundColor: '#2563eb' }
        );
        if (qrCode) {
            console.log('Created QR code:', qrCode.short_url);
        }
        
        // Get dashboard stats
        const stats = await sdk.getDashboardStats();
        if (stats) {
            console.log('Total scans:', stats.total_scans);
        }
    }
}

// Export for use in other modules
module.exports = QRReaderSDK;

// Run example if this file is executed directly
if (require.main === module) {
    main().catch(console.error);
}
```

### React Hook for QR Reader API

```javascript
// useQRReader.js
import { useState, useEffect, useCallback } from 'react';
import QRReaderSDK from './qr-reader-sdk';

export const useQRReader = (email, password) => {
    const [sdk, setSdk] = useState(null);
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        const initializeSDK = async () => {
            const qrSDK = new QRReaderSDK(email, password);
            const loginSuccess = await qrSDK.login();
            
            if (loginSuccess) {
                setSdk(qrSDK);
                setIsLoggedIn(true);
            } else {
                setError('Login failed');
            }
        };
        
        if (email && password) {
            initializeSDK();
        }
    }, [email, password]);
    
    const decodeQRCode = useCallback(async (imageFile) => {
        if (!sdk) return null;
        
        setLoading(true);
        setError(null);
        
        try {
            const result = await sdk.decodeQRCode(imageFile);
            return result;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, [sdk]);
    
    const createQRCode = useCallback(async (name, data, options = {}) => {
        if (!sdk) return null;
        
        setLoading(true);
        setError(null);
        
        try {
            const result = await sdk.createQRCode(name, data, 'url', options);
            return result;
        } catch (err) {
            setError(err.message);
            return null;
        } finally {
            setLoading(false);
        }
    }, [sdk]);
    
    const getDashboardStats = useCallback(async (days = 30) => {
        if (!sdk) return null;
        
        try {
            const stats = await sdk.getDashboardStats(days);
            return stats;
        } catch (err) {
            setError(err.message);
            return null;
        }
    }, [sdk]);
    
    return {
        sdk,
        isLoggedIn,
        loading,
        error,
        decodeQRCode,
        createQRCode,
        getDashboardStats
    };
};

// React component example
import React, { useState } from 'react';
import { useQRReader } from './useQRReader';

const QRReaderComponent = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [selectedFile, setSelectedFile] = useState(null);
    const [result, setResult] = useState(null);
    
    const { isLoggedIn, loading, error, decodeQRCode } = useQRReader(email, password);
    
    const handleFileSelect = (event) => {
        setSelectedFile(event.target.files[0]);
    };
    
    const handleDecode = async () => {
        if (!selectedFile) return;
        
        const result = await decodeQRCode(selectedFile);
        setResult(result);
    };
    
    if (!isLoggedIn) {
        return (
            <div>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
            </div>
        );
    }
    
    return (
        <div>
            <h2>QR Code Reader</h2>
            
            <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
            />
            
            <button onClick={handleDecode} disabled={loading || !selectedFile}>
                {loading ? 'Decoding...' : 'Decode QR Code'}
            </button>
            
            {error && <div style={{color: 'red'}}>Error: {error}</div>}
            
            {result && (
                <div>
                    <h3>Result:</h3>
                    <pre>{JSON.stringify(result, null, 2)}</pre>
                </div>
            )}
        </div>
    );
};

export default QRReaderComponent;
```

## Go SDK

```go
// qr_reader_sdk.go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "mime/multipart"
    "net/http"
    "os"
    "time"
)

type QRReaderSDK struct {
    Email        string
    Password     string
    BaseURL      string
    AccessToken  string
    RefreshToken string
    Client       *http.Client
}

type LoginResponse struct {
    AccessToken  string `json:"access_token"`
    RefreshToken string `json:"refresh_token"`
    TokenType    string `json:"token_type"`
    User         User   `json:"user"`
}

type User struct {
    ID    int    `json:"id"`
    Email string `json:"email"`
    Tier  string `json:"tier"`
}

type DecodeResponse struct {
    Success     bool     `json:"success"`
    DecodedData []string `json:"decoded_data"`
    Filename    string   `json:"filename"`
    ScanID      int      `json:"scan_id"`
}

type QRCode struct {
    ID                   int    `json:"id"`
    Name                 string `json:"name"`
    Data                 string `json:"data"`
    QRType               string `json:"qr_type"`
    Size                 int    `json:"size"`
    Border               int    `json:"border"`
    ShortURL             string `json:"short_url"`
    ScanCount            int    `json:"scan_count"`
    CreatedAt            string `json:"created_at"`
}

func NewQRReaderSDK(email, password string) *QRReaderSDK {
    return &QRReaderSDK{
        Email:    email,
        Password: password,
        BaseURL:  "https://api.qrreader-premium.com/api/v1",
        Client:   &http.Client{Timeout: 30 * time.Second},
    }
}

func (sdk *QRReaderSDK) Login() error {
    loginData := map[string]string{
        "email":    sdk.Email,
        "password": sdk.Password,
    }
    
    jsonData, err := json.Marshal(loginData)
    if err != nil {
        return err
    }
    
    resp, err := sdk.Client.Post(
        sdk.BaseURL+"/auth/login",
        "application/json",
        bytes.NewBuffer(jsonData),
    )
    if err != nil {
        return err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return fmt.Errorf("login failed with status: %d", resp.StatusCode)
    }
    
    var loginResp LoginResponse
    if err := json.NewDecoder(resp.Body).Decode(&loginResp); err != nil {
        return err
    }
    
    sdk.AccessToken = loginResp.AccessToken
    sdk.RefreshToken = loginResp.RefreshToken
    
    return nil
}

func (sdk *QRReaderSDK) DecodeQRCode(imagePath string) (*DecodeResponse, error) {
    file, err := os.Open(imagePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()
    
    var buf bytes.Buffer
    writer := multipart.NewWriter(&buf)
    
    part, err := writer.CreateFormFile("file", imagePath)
    if err != nil {
        return nil, err
    }
    
    _, err = io.Copy(part, file)
    if err != nil {
        return nil, err
    }
    
    writer.Close()
    
    req, err := http.NewRequest("POST", sdk.BaseURL+"/qr/decode", &buf)
    if err != nil {
        return nil, err
    }
    
    req.Header.Set("Content-Type", writer.FormDataContentType())
    req.Header.Set("Authorization", "Bearer "+sdk.AccessToken)
    
    resp, err := sdk.Client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("decode failed with status: %d", resp.StatusCode)
    }
    
    var decodeResp DecodeResponse
    if err := json.NewDecoder(resp.Body).Decode(&decodeResp); err != nil {
        return nil, err
    }
    
    return &decodeResp, nil
}

func (sdk *QRReaderSDK) CreateQRCode(name, data string, options map[string]interface{}) (*QRCode, error) {
    qrData := map[string]interface{}{
        "name":                    name,
        "data":                    data,
        "qr_type":                 "url",
        "size":                    300,
        "border":                  4,
        "error_correction_level":  "M",
        "foreground_color":        "#000000",
        "background_color":        "#FFFFFF",
    }
    
    // Apply options
    for key, value := range options {
        qrData[key] = value
    }
    
    jsonData, err := json.Marshal(qrData)
    if err != nil {
        return nil, err
    }
    
    req, err := http.NewRequest("POST", sdk.BaseURL+"/qr-codes/generate", bytes.NewBuffer(jsonData))
    if err != nil {
        return nil, err
    }
    
    req.Header.Set("Content-Type", "application/json")
    req.Header.Set("Authorization", "Bearer "+sdk.AccessToken)
    
    resp, err := sdk.Client.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    
    if resp.StatusCode != http.StatusOK {
        return nil, fmt.Errorf("create QR code failed with status: %d", resp.StatusCode)
    }
    
    var qrCode QRCode
    if err := json.NewDecoder(resp.Body).Decode(&qrCode); err != nil {
        return nil, err
    }
    
    return &qrCode, nil
}

// Usage example
func main() {
    sdk := NewQRReaderSDK("your@email.com", "yourpassword")
    
    if err := sdk.Login(); err != nil {
        fmt.Printf("Login failed: %v\n", err)
        return
    }
    
    fmt.Println("Login successful!")
    
    // Decode QR code
    result, err := sdk.DecodeQRCode("qr_code.png")
    if err != nil {
        fmt.Printf("Decode failed: %v\n", err)
        return
    }
    
    fmt.Printf("Decoded data: %v\n", result.DecodedData)
    
    // Create QR code
    options := map[string]interface{}{
        "size":           400,
        "foreground_color": "#2563eb",
    }
    
    qrCode, err := sdk.CreateQRCode("My Website", "https://example.com", options)
    if err != nil {
        fmt.Printf("Create QR code failed: %v\n", err)
        return
    }
    
    fmt.Printf("Created QR code: %s\n", qrCode.ShortURL)
}
```

## PHP SDK

```php
<?php
// qr_reader_sdk.php

class QRReaderSDK {
    private $email;
    private $password;
    private $baseUrl;
    private $accessToken;
    private $refreshToken;
    private $tokenExpiresAt;
    
    public function __construct($email, $password, $baseUrl = 'https://api.qrreader-premium.com/api/v1') {
        $this->email = $email;
        $this->password = $password;
        $this->baseUrl = $baseUrl;
    }
    
    public function login() {
        $data = [
            'email' => $this->email,
            'password' => $this->password
        ];
        
        $response = $this->makeRequest('POST', '/auth/login', $data);
        
        if ($response && isset($response['access_token'])) {
            $this->accessToken = $response['access_token'];
            $this->refreshToken = $response['refresh_token'];
            $this->tokenExpiresAt = time() + (15 * 60); // 15 minutes
            return true;
        }
        
        return false;
    }
    
    public function decodeQRCode($imagePath) {
        if (!file_exists($imagePath)) {
            throw new Exception("Image file not found: $imagePath");
        }
        
        $postData = [
            'file' => new CURLFile($imagePath)
        ];
        
        $response = $this->makeRequest('POST', '/qr/decode', $postData, true);
        return $response;
    }
    
    public function createQRCode($name, $data, $options = []) {
        $qrData = array_merge([
            'name' => $name,
            'data' => $data,
            'qr_type' => 'url',
            'size' => 300,
            'border' => 4,
            'error_correction_level' => 'M',
            'foreground_color' => '#000000',
            'background_color' => '#FFFFFF'
        ], $options);
        
        $response = $this->makeRequest('POST', '/qr-codes/generate', $qrData);
        return $response;
    }
    
    public function getDashboardStats($days = 30) {
        $params = ['days' => $days];
        $response = $this->makeRequest('GET', '/analytics/dashboard', null, false, $params);
        return $response;
    }
    
    private function makeRequest($method, $endpoint, $data = null, $isMultipart = false, $params = []) {
        $url = $this->baseUrl . $endpoint;
        
        if (!empty($params)) {
            $url .= '?' . http_build_query($params);
        }
        
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 30);
        
        $headers = [];
        
        if ($this->accessToken) {
            $headers[] = 'Authorization: Bearer ' . $this->accessToken;
        }
        
        if ($method === 'POST') {
            curl_setopt($ch, CURLOPT_POST, true);
            
            if ($isMultipart) {
                curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
            } else {
                curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
                $headers[] = 'Content-Type: application/json';
            }
        }
        
        curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode >= 200 && $httpCode < 300) {
            return json_decode($response, true);
        }
        
        throw new Exception("API request failed with status: $httpCode");
    }
}

// Usage example
try {
    $sdk = new QRReaderSDK('your@email.com', 'yourpassword');
    
    if ($sdk->login()) {
        echo "Login successful!\n";
        
        // Decode QR code
        $result = $sdk->decodeQRCode('qr_code.png');
        echo "Decoded data: " . implode(', ', $result['decoded_data']) . "\n";
        
        // Create QR code
        $qrCode = $sdk->createQRCode('My Website', 'https://example.com', [
            'size' => 400,
            'foreground_color' => '#2563eb'
        ]);
        echo "Created QR code: " . $qrCode['short_url'] . "\n";
        
        // Get dashboard stats
        $stats = $sdk->getDashboardStats();
        echo "Total scans: " . $stats['total_scans'] . "\n";
    }
} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
}
?>
```

These SDK examples provide complete implementations for the most popular programming languages, making it easy for developers to integrate with the QR Code Reader Premium Platform API.
