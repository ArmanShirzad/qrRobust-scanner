import React, { createContext, useContext, useState } from 'react';
import { qrAPI, qrDesignerAPI } from '../services/api';
import toast from 'react-hot-toast';

const QRContext = createContext();

export const useQR = () => {
  const context = useContext(QRContext);
  if (!context) {
    throw new Error('useQR must be used within a QRProvider');
  }
  return context;
};

export const QRProvider = ({ children }) => {
  const [qrCodes, setQrCodes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analytics, setAnalytics] = useState(null);

  const fetchQRCodes = async (params = {}) => {
    try {
      setLoading(true);
      const response = await qrAPI.getQRCodes(params);
      setQrCodes(response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch QR codes:', error);
      toast.error('Failed to fetch QR codes');
      return [];
    } finally {
      setLoading(false);
    }
  };

  const generateQRCode = async (qrData) => {
    try {
      const response = await qrAPI.generate(qrData);
      toast.success('QR code generated successfully');
      await fetchQRCodes(); // Refresh the list
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to generate QR code';
      toast.error(message);
      throw error;
    }
  };

  const updateQRCode = async (id, data) => {
    try {
      const response = await qrAPI.updateQRCode(id, data);
      toast.success('QR code updated successfully');
      await fetchQRCodes(); // Refresh the list
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to update QR code';
      toast.error(message);
      throw error;
    }
  };

  const deleteQRCode = async (id) => {
    try {
      await qrAPI.deleteQRCode(id);
      toast.success('QR code deleted successfully');
      await fetchQRCodes(); // Refresh the list
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to delete QR code';
      toast.error(message);
      throw error;
    }
  };

  const getQRStats = async (id) => {
    try {
      const response = await qrAPI.getQRStats(id);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch QR stats:', error);
      return null;
    }
  };

  const decodeQRCode = async (file) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await qrAPI.decode(formData);
      toast.success('QR code decoded successfully');
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to decode QR code';
      toast.error(message);
      throw error;
    }
  };

  const decodeQRCodeBase64 = async (base64Data) => {
    try {
      const response = await qrAPI.decodeBase64({ data: base64Data });
      toast.success('QR code decoded successfully');
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to decode QR code';
      toast.error(message);
      throw error;
    }
  };

  const designQRCode = async (designData) => {
    try {
      const formData = new FormData();
      Object.keys(designData).forEach(key => {
        if (designData[key] !== null && designData[key] !== undefined) {
          if (key === 'custom_styling' && typeof designData[key] === 'object') {
            formData.append(key, JSON.stringify(designData[key]));
          } else {
            formData.append(key, designData[key]);
          }
        }
      });

      const response = await qrDesignerAPI.design(formData);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to design QR code';
      toast.error(message);
      throw error;
    }
  };

  const designAndSaveQRCode = async (formData) => {
    try {
      const response = await qrDesignerAPI.designAndSave(formData);
      toast.success('QR code designed and saved successfully');
      await fetchQRCodes(); // Refresh the list
      return response.data;
    } catch (error) {
      let message = 'Failed to design and save QR code';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          // Handle Pydantic validation errors
          message = detail.map(err => `${err.loc?.join('.')}: ${err.msg}`).join(', ');
        } else if (typeof detail === 'string') {
          message = detail;
        }
      } else if (error.message) {
        message = error.message;
      }
      
      toast.error(message);
      throw error;
    }
  };

  const previewQRCode = async (data, template) => {
    try {
      const formData = new FormData();
      formData.append('data', data);
      formData.append('template', template);

      const response = await qrDesignerAPI.preview(formData);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.detail || 'Failed to preview QR code';
      toast.error(message);
      throw error;
    }
  };

  const value = {
    qrCodes,
    loading,
    analytics,
    setAnalytics,
    fetchQRCodes,
    generateQRCode,
    updateQRCode,
    deleteQRCode,
    getQRStats,
    decodeQRCode,
    decodeQRCodeBase64,
    designQRCode,
    designAndSaveQRCode,
    previewQRCode,
  };

  return (
    <QRContext.Provider value={value}>
      {children}
    </QRContext.Provider>
  );
};
