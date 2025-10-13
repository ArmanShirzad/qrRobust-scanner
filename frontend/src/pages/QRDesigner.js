import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { 
  Palette, 
  Upload, 
  Download, 
  Eye,
  Settings,
  Image,
  Square,
  Circle,
  Zap
} from 'lucide-react';
import { qrDesignerAPI } from '../services/api';
import { useQR } from '../contexts/QRContext';
import toast from 'react-hot-toast';

const QRDesigner = () => {
  const navigate = useNavigate();
  const { designAndSaveQRCode } = useQR();
  const [designData, setDesignData] = useState({
    data: '',
    size: 300,
    border: 4,
    error_correction: 'M',
    fill_color: '#000000',
    back_color: '#FFFFFF',
    module_drawer: 'square',
    color_mask: 'solid',
    logo_size: 60,
    logo_position: 'center',
    corner_radius: 0,
    custom_styling: null,
  });
  
  const [logoFile, setLogoFile] = useState(null);
  const [backgroundFile, setBackgroundFile] = useState(null);
  const [previewImage, setPreviewImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('basic');



  const handleInputChange = (field, value) => {
    setDesignData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Removed auto-preview on typing to avoid excessive requests
  };


  const generatePreview = async () => {
    if (!designData.data) {
      toast.error('Please enter QR code data');
      return;
    }

    try {
      setLoading(true);
      console.log('Generating preview with data:', designData);
      
      const formData = new FormData();
      formData.append('data', designData.data);
      formData.append('size', designData.size);
      formData.append('border', designData.border);
      formData.append('error_correction', designData.error_correction);
      formData.append('fill_color', designData.fill_color);
      formData.append('back_color', designData.back_color);
      formData.append('module_drawer', designData.module_drawer);
      formData.append('color_mask', designData.color_mask);
      formData.append('corner_radius', designData.corner_radius);
      formData.append('logo_size', designData.logo_size);
      formData.append('logo_position', designData.logo_position);

      if (logoFile) {
        formData.append('logo_file', logoFile);
      }
      if (backgroundFile) {
        formData.append('background_file', backgroundFile);
      }

      console.log('Sending request to API...');
      const response = await qrDesignerAPI.design(formData);
      console.log('API response:', response.data);
      
      if (response.data.success && response.data.image_data) {
        setPreviewImage(response.data.image_data);
        toast.success('Preview generated successfully!');
      } else {
        console.error('API returned unsuccessful response:', response.data);
        toast.error('Failed to generate preview - API error');
      }
    } catch (error) {
      console.error('Failed to generate preview:', error);
      toast.error('Failed to generate preview');
    } finally {
      setLoading(false);
    }
  };

  const designQRCode = async () => {
    if (!designData.data) {
      toast.error('Please enter QR code data');
      return;
    }

    try {
      setLoading(true);
      
      // Create FormData with all required fields including name
      const formData = new FormData();
      formData.append('data', designData.data);
      formData.append('name', `QR Code ${new Date().toISOString().slice(0, 19)}`); // Auto-generate name
      formData.append('size', designData.size);
      formData.append('border', designData.border);
      formData.append('error_correction', designData.error_correction);
      formData.append('fill_color', designData.fill_color);
      formData.append('back_color', designData.back_color);
      formData.append('module_drawer', designData.module_drawer);
      formData.append('color_mask', designData.color_mask);
      formData.append('corner_radius', designData.corner_radius);
      formData.append('logo_size', designData.logo_size);
      formData.append('logo_position', designData.logo_position);

      if (logoFile) {
        formData.append('logo_file', logoFile);
      }
      if (backgroundFile) {
        formData.append('background_file', backgroundFile);
      }

      const response = await designAndSaveQRCode(formData);
      setPreviewImage(response.image_data);
      toast.success('QR code designed and saved successfully!');
    } catch (error) {
      console.error('Failed to design QR code:', error);
      toast.error('Failed to design QR code');
    } finally {
      setLoading(false);
    }
  };

  const downloadQRCode = () => {
    if (previewImage) {
      const link = document.createElement('a');
      link.href = `data:image/png;base64,${previewImage}`;
      link.download = 'qr-code.png';
      link.click();
    }
  };

  const logoDropzone = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif']
    },
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setLogoFile(acceptedFiles[0]);
      }
    }
  });

  const backgroundDropzone = useDropzone({
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.gif']
    },
    onDrop: (acceptedFiles) => {
      if (acceptedFiles.length > 0) {
        setBackgroundFile(acceptedFiles[0]);
      }
    }
  });

  const tabs = [
    { id: 'basic', name: 'Basic', icon: Settings },
    { id: 'colors', name: 'Colors', icon: Palette },
    { id: 'style', name: 'Style', icon: Square },
    { id: 'advanced', name: 'Advanced', icon: Zap },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">QR Code Designer</h1>
        <p className="text-gray-600">Create custom QR codes with logos, colors, and styling</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Design Panel */}
        <div className="lg:col-span-1 space-y-6">
          {/* QR Data Input */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">QR Code Data</h3>
            <textarea
              className="input-field h-24 resize-none"
              placeholder="Enter URL, text, or data for your QR code..."
              value={designData.data}
              onChange={(e) => handleInputChange('data', e.target.value)}
            />
          </div>


          {/* Design Options */}
          <div className="card">
            <div className="flex space-x-1 mb-4">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-1 flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="h-4 w-4 mr-1" />
                    {tab.name}
                  </button>
                );
              })}
            </div>

            {/* Basic Tab */}
            {activeTab === 'basic' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Size (pixels)
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    value={designData.size}
                    onChange={(e) => handleInputChange('size', parseInt(e.target.value))}
                    min="100"
                    max="2000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Border
                  </label>
                  <input
                    type="number"
                    className="input-field"
                    value={designData.border}
                    onChange={(e) => handleInputChange('border', parseInt(e.target.value))}
                    min="0"
                    max="20"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Error Correction
                  </label>
                  <select
                    className="input-field"
                    value={designData.error_correction}
                    onChange={(e) => handleInputChange('error_correction', e.target.value)}
                  >
                    <option value="L">Low (7%)</option>
                    <option value="M">Medium (15%)</option>
                    <option value="Q">Quartile (25%)</option>
                    <option value="H">High (30%)</option>
                  </select>
                </div>
              </div>
            )}

            {/* Colors Tab */}
            {activeTab === 'colors' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fill Color
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="color"
                      className="w-12 h-10 border border-gray-300 rounded"
                      value={designData.fill_color}
                      onChange={(e) => handleInputChange('fill_color', e.target.value)}
                    />
                    <input
                      type="text"
                      className="input-field flex-1"
                      value={designData.fill_color}
                      onChange={(e) => handleInputChange('fill_color', e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Background Color
                  </label>
                  <div className="flex space-x-2">
                    <input
                      type="color"
                      className="w-12 h-10 border border-gray-300 rounded"
                      value={designData.back_color}
                      onChange={(e) => handleInputChange('back_color', e.target.value)}
                    />
                    <input
                      type="text"
                      className="input-field flex-1"
                      value={designData.back_color}
                      onChange={(e) => handleInputChange('back_color', e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Color Effect
                  </label>
                  <select
                    className="input-field"
                    value={designData.color_mask}
                    onChange={(e) => handleInputChange('color_mask', e.target.value)}
                  >
                    <option value="solid">Solid</option>
                    <option value="radial_gradient">Radial Gradient</option>
                    <option value="square_gradient">Square Gradient</option>
                    <option value="horizontal_gradient">Horizontal Gradient</option>
                    <option value="vertical_gradient">Vertical Gradient</option>
                  </select>
                </div>
              </div>
            )}

            {/* Style Tab */}
            {activeTab === 'style' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Module Style
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { value: 'square', label: 'Square', icon: Square },
                      { value: 'rounded', label: 'Rounded', icon: Square },
                      { value: 'circle', label: 'Circle', icon: Circle },
                      { value: 'gapped_square', label: 'Gapped', icon: Square },
                    ].map((style) => {
                      const Icon = style.icon;
                      return (
                        <button
                          key={style.value}
                          onClick={() => handleInputChange('module_drawer', style.value)}
                          className={`p-2 border rounded-lg flex items-center justify-center ${
                            designData.module_drawer === style.value
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <Icon className="h-4 w-4 mr-1" />
                          <span className="text-xs">{style.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Corner Radius
                  </label>
                  <input
                    type="range"
                    className="w-full"
                    min="0"
                    max="10"
                    value={designData.corner_radius}
                    onChange={(e) => handleInputChange('corner_radius', parseInt(e.target.value))}
                  />
                  <div className="text-xs text-gray-500 text-center">
                    {designData.corner_radius}
                  </div>
                </div>
              </div>
            )}

            {/* Advanced Tab */}
            {activeTab === 'advanced' && (
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Logo Upload
                  </label>
                  <div
                    {...logoDropzone.getRootProps()}
                    className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-gray-400 cursor-pointer"
                  >
                    <input {...logoDropzone.getInputProps()} />
                    <Upload className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      {logoFile ? logoFile.name : 'Drop logo here or click to upload'}
                    </p>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Background Upload
                  </label>
                  <div
                    {...backgroundDropzone.getRootProps()}
                    className="border-2 border-dashed border-gray-300 rounded-lg p-4 text-center hover:border-gray-400 cursor-pointer"
                  >
                    <input {...backgroundDropzone.getInputProps()} />
                    <Image className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600">
                      {backgroundFile ? backgroundFile.name : 'Drop background here or click to upload'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="card">
            <div className="space-y-3">
              <button
                onClick={generatePreview}
                disabled={loading || !designData.data}
                className="w-full btn-primary flex items-center justify-center"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                ) : (
                  <>
                    <Palette className="h-5 w-5 mr-2" />
                    Generate Preview
                  </>
                )}
              </button>
              
              <button
                onClick={designQRCode}
                disabled={loading || !designData.data}
                className="w-full btn-secondary flex items-center justify-center"
              >
                {loading ? (
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>
                ) : (
                  <>
                    <Settings className="h-5 w-5 mr-2" />
                    Design & Save
                  </>
                )}
              </button>
              
              {previewImage && (
                <button
                  onClick={downloadQRCode}
                  className="w-full btn-secondary flex items-center justify-center"
                >
                  <Download className="h-5 w-5 mr-2" />
                  Download
                </button>
              )}
              
              <button
                onClick={() => navigate('/qr-management')}
                className="w-full btn-outline flex items-center justify-center"
              >
                <Eye className="h-5 w-5 mr-2" />
                View in Management
              </button>
            </div>
          </div>
        </div>

        {/* Preview Panel */}
        <div className="lg:col-span-2">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Preview</h3>
            <div className="flex items-center justify-center h-96 bg-gray-50 rounded-lg">
              {previewImage ? (
                <img
                  src={`data:image/png;base64,${previewImage}`}
                  alt="QR Code Preview"
                  className="max-w-full max-h-full object-contain"
                />
              ) : (
                <div className="text-center text-gray-500">
                  <Eye className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Enter data and click "Design QR Code" to see preview</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QRDesigner;
