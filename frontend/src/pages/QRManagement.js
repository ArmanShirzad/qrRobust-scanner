import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  QrCode, 
  Search, 
  Edit, 
  Trash2, 
  Eye,
  Plus,
  MoreVertical,
  Download
} from 'lucide-react';
import { useQR } from '../contexts/QRContext';
import { qrDesignerAPI } from '../services/api';
import toast from 'react-hot-toast';

const QRManagement = () => {
  const navigate = useNavigate();
  const { qrCodes, loading, fetchQRCodes, deleteQRCode } = useQR();
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [qrImages, setQrImages] = useState({});
  const [loadingImages, setLoadingImages] = useState({});
  const isRequesting = useRef(false);

  const fetchQRCodesCallback = useCallback(() => {
    if (!isRequesting.current) {
      isRequesting.current = true;
      fetchQRCodes({
        search: searchTerm,
        type: filterType,
        sort_by: sortBy,
        sort_order: sortOrder
      }).finally(() => {
        isRequesting.current = false;
      });
    }
  }, [fetchQRCodes, searchTerm, filterType, sortBy, sortOrder]);

  useEffect(() => {
    fetchQRCodesCallback();
  }, [fetchQRCodesCallback]);

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this QR code?')) {
      try {
        await deleteQRCode(id);
      } catch (error) {
        console.error('Failed to delete QR code:', error);
      }
    }
  };

  const fetchQRCodeImage = async (qrId) => {
    if (qrImages[qrId] || loadingImages[qrId]) return;
    
    setLoadingImages(prev => ({ ...prev, [qrId]: true }));
    try {
      const response = await qrDesignerAPI.getQRCodeImage(qrId);
      setQrImages(prev => ({ ...prev, [qrId]: response.data.image_data }));
    } catch (error) {
      console.error('Failed to fetch QR code image:', error);
      toast.error('Failed to load QR code image');
    } finally {
      setLoadingImages(prev => ({ ...prev, [qrId]: false }));
    }
  };

  const handleView = (qr) => {
    // Navigate to QR code details page or open modal
    navigate(`/qr-codes/${qr.id}`);
  };

  const handleEdit = (qr) => {
    // Navigate to QR designer with pre-filled data
    navigate('/qr-designer', { state: { editQR: qr } });
  };

  const handleDownload = async (qr) => {
    try {
      if (!qrImages[qr.id]) {
        await fetchQRCodeImage(qr.id);
      }
      
      const imageData = qrImages[qr.id];
      if (imageData) {
        const link = document.createElement('a');
        link.href = `data:image/png;base64,${imageData}`;
        link.download = `${qr.title || 'qr-code'}.png`;
        link.click();
        toast.success('QR code downloaded!');
      }
    } catch (error) {
      console.error('Failed to download QR code:', error);
      toast.error('Failed to download QR code');
    }
  };

  const handleQRClick = (qr) => {
    // Show QR code in larger view or copy to clipboard
    if (qr.destination_url) {
      navigator.clipboard.writeText(qr.destination_url);
      toast.success('URL copied to clipboard!');
    }
  };

  const filteredQRCodes = qrCodes.filter(qr => {
    const matchesSearch = qr.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         qr.destination_url?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || qr.qr_type === filterType;
    return matchesSearch && matchesFilter;
  });

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getQRTypeColor = (type) => {
    const colors = {
      'url': 'bg-blue-100 text-blue-800',
      'text': 'bg-green-100 text-green-800',
      'email': 'bg-purple-100 text-purple-800',
      'phone': 'bg-orange-100 text-orange-800',
      'wifi': 'bg-pink-100 text-pink-800',
      'custom': 'bg-gray-100 text-gray-800'
    };
    return colors[type] || colors['custom'];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">QR Code Management</h1>
          <p className="text-gray-600">Manage and organize your QR codes</p>
        </div>
        <button 
          onClick={() => navigate('/qr-designer')}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Create QR Code
        </button>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search QR codes..."
                className="input-field pl-10"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <div className="flex gap-2">
            <select
              className="input-field"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">All Types</option>
              <option value="url">URL</option>
              <option value="text">Text</option>
              <option value="email">Email</option>
              <option value="phone">Phone</option>
              <option value="wifi">WiFi</option>
              <option value="custom">Custom</option>
            </select>
            <select
              className="input-field"
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field);
                setSortOrder(order);
              }}
            >
              <option value="created_at-desc">Newest First</option>
              <option value="created_at-asc">Oldest First</option>
              <option value="name-asc">Name A-Z</option>
              <option value="name-desc">Name Z-A</option>
              <option value="scan_count-desc">Most Scanned</option>
              <option value="scan_count-asc">Least Scanned</option>
            </select>
          </div>
        </div>
      </div>

      {/* QR Codes Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredQRCodes.map((qr) => (
            <div key={qr.id} className="card hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {qr.title || `QR Code ${qr.id}`}
                  </h3>
                  <p className="text-sm text-gray-600 truncate">
                    {qr.destination_url}
                  </p>
                </div>
                <div className="flex items-center space-x-1">
                  <span className={`px-2 py-1 text-xs font-medium rounded-full ${getQRTypeColor(qr.qr_type)}`}>
                    {qr.qr_type}
                  </span>
                  <div className="relative">
                    <button 
                      className="p-1 text-gray-400 hover:text-gray-600"
                      onClick={() => {
                        // Toggle dropdown menu
                        const menu = document.getElementById(`menu-${qr.id}`);
                        if (menu) {
                          menu.classList.toggle('hidden');
                        }
                      }}
                    >
                      <MoreVertical className="h-4 w-4" />
                    </button>
                    <div 
                      id={`menu-${qr.id}`}
                      className="hidden absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg z-10 border"
                    >
                      <div className="py-1">
                        <button
                          onClick={() => handleDownload(qr)}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <Download className="h-4 w-4 inline mr-2" />
                          Download
                        </button>
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(qr.destination_url);
                            toast.success('URL copied to clipboard!');
                          }}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          Copy URL
                        </button>
                        <button
                          onClick={() => handleView(qr)}
                          className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                        >
                          <Eye className="h-4 w-4 inline mr-2" />
                          View Details
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* QR Code Preview */}
              <div className="flex justify-center mb-4">
                <div 
                  className="w-32 h-32 bg-gray-100 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-200 transition-colors"
                  onClick={() => handleQRClick(qr)}
                >
                  {loadingImages[qr.id] ? (
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  ) : qrImages[qr.id] ? (
                    <img
                      src={`data:image/png;base64,${qrImages[qr.id]}`}
                      alt="QR Code"
                      className="w-full h-full object-contain"
                    />
                  ) : (
                    <div className="text-center">
                      <QrCode className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          fetchQRCodeImage(qr.id);
                        }}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        Load Preview
                      </button>
                    </div>
                  )}
                </div>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">{qr.scan_count || 0}</div>
                  <div className="text-xs text-gray-500">Scans</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-900">
                    {qr.last_scan ? new Date(qr.last_scan).toLocaleDateString() : 'Never'}
                  </div>
                  <div className="text-xs text-gray-500">Last Scan</div>
                </div>
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <button 
                  onClick={() => handleView(qr)}
                  className="flex-1 btn-secondary text-sm flex items-center justify-center"
                >
                  <Eye className="h-4 w-4 mr-1" />
                  View
                </button>
                <button 
                  onClick={() => handleEdit(qr)}
                  className="flex-1 btn-secondary text-sm flex items-center justify-center"
                >
                  <Edit className="h-4 w-4 mr-1" />
                  Edit
                </button>
                <button 
                  onClick={() => handleDownload(qr)}
                  className="px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                  title="Download QR Code"
                >
                  <Download className="h-4 w-4" />
                </button>
                <button 
                  onClick={() => handleDelete(qr.id)}
                  className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>

              {/* Metadata */}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="text-xs text-gray-500">
                  Created: {formatDate(qr.created_at)}
                </div>
                {qr.size && (
                  <div className="text-xs text-gray-500">
                    Size: {qr.size}x{qr.size}px
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Empty State */}
      {!loading && filteredQRCodes.length === 0 && (
        <div className="text-center py-12">
          <QrCode className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No QR codes found</h3>
          <p className="text-gray-500 mb-4">
            {searchTerm || filterType !== 'all' 
              ? 'Try adjusting your search or filters'
              : 'Create your first QR code to get started'
            }
          </p>
          <button 
            onClick={() => navigate('/qr-designer')}
            className="btn-primary"
          >
            <Plus className="h-5 w-5 mr-2" />
            Create QR Code
          </button>
        </div>
      )}
    </div>
  );
};

export default QRManagement;
