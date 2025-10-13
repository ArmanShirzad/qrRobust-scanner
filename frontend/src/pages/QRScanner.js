import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Camera, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { qrAPI } from '../services/api';
import toast from 'react-hot-toast';

const QRScanner = () => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [scanResult, setScanResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    setUploadedFile(file);
    setScanResult(null);
    setError(null);
  };

  const handleScan = async () => {
    if (!uploadedFile) {
      toast.error('Please select an image file first');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const formData = new FormData();
      formData.append('file', uploadedFile);
      
      const response = await qrAPI.decode(formData);
      
      // Transform the response to match expected format
      const scanData = {
        content: response.data.decoded_data?.[0] || 'No content found',
        qr_type: 'QR Code',
        metadata: {
          filename: response.data.filename,
          scan_id: response.data.scan_id,
          success: response.data.success
        }
      };
      
      setScanResult(scanData);
      toast.success('QR code scanned successfully!');
    } catch (error) {
      console.error('Failed to scan QR code:', error);
      setError(error.response?.data?.detail || 'Failed to scan QR code');
      toast.error('Failed to scan QR code');
    } finally {
      setLoading(false);
    }
  };

  const fileDropzone = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
    },
    onDrop,
    multiple: false
  });

  const getFilePreview = () => {
    if (!uploadedFile) return null;
    
    const url = URL.createObjectURL(uploadedFile);
    return (
      <div className="mt-4">
        <img
          src={url}
          alt="Uploaded file preview"
          className="max-w-full max-h-64 object-contain rounded-lg border border-gray-200"
        />
        <p className="text-sm text-gray-600 mt-2">
          File: {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
        </p>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">QR Code Scanner</h1>
        <p className="text-gray-600">Upload an image containing a QR code to decode its content</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Upload Section */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Image</h3>
          
          <div
            {...fileDropzone.getRootProps()}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 cursor-pointer transition-colors"
          >
            <input {...fileDropzone.getInputProps()} />
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg text-gray-600 mb-2">
              {uploadedFile ? 'File uploaded successfully!' : 'Click to select an image file'}
            </p>
            <p className="text-sm text-gray-500">
              or drag and drop your image here
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Supports PNG, JPG, JPEG, GIF, BMP
            </p>
          </div>

          {getFilePreview()}

          <button
            onClick={handleScan}
            disabled={loading || !uploadedFile}
            className="w-full mt-4 btn-primary flex items-center justify-center"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <>
                <Camera className="h-5 w-5 mr-2" />
                Scan QR Code
              </>
            )}
          </button>
        </div>

        {/* Results Section */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Scan Results</h3>
          
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                <div>
                  <h4 className="text-sm font-medium text-red-800">Scan Failed</h4>
                  <p className="text-sm text-red-600 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {scanResult ? (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center mb-3">
                <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                <h4 className="text-sm font-medium text-green-800">QR Code Detected</h4>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Content
                  </label>
                  <div className="bg-white border border-gray-200 rounded-lg p-3">
                    <p className="text-sm text-gray-900 break-all">{scanResult.content}</p>
                  </div>
                </div>

                {scanResult.qr_type && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Type
                    </label>
                    <span className="inline-block px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                      {scanResult.qr_type}
                    </span>
                  </div>
                )}

                {scanResult.metadata && Object.keys(scanResult.metadata).length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Metadata
                    </label>
                    <div className="bg-white border border-gray-200 rounded-lg p-3">
                      <pre className="text-xs text-gray-600 whitespace-pre-wrap">
                        {JSON.stringify(scanResult.metadata, null, 2)}
                      </pre>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p>Upload an image to see scan results</p>
            </div>
          )}
        </div>
      </div>

      {/* API Usage Info */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">API Usage</h3>
        <p className="text-sm text-gray-600 mb-3">
          You can also use this service programmatically by sending a POST request to <code className="bg-gray-100 px-2 py-1 rounded">/decode_base64</code> with a base64-encoded image.
        </p>
        <div className="bg-gray-50 rounded-lg p-4">
          <pre className="text-xs text-gray-700 overflow-x-auto">
{`POST /decode_base64
Content-Type: application/json

{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}`}
          </pre>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Response will contain the decoded text or an error message.
        </p>
      </div>
    </div>
  );
};

export default QRScanner;
