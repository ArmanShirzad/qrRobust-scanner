import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken
          });
          
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me'),
  changePassword: (passwordData) => api.post('/auth/change-password', passwordData),
};

// QR Code API
export const qrAPI = {
  decode: (formData) => api.post('/qr/decode', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  decodeBase64: (data) => api.post('/qr/decode-base64', data),
  generate: (qrData) => api.post('/qr-codes/generate', qrData),
  getQRCodes: (params) => api.get('/qr-codes', { params }),
  getQRCode: (id) => api.get(`/qr-codes/${id}`),
  updateQRCode: (id, data) => api.put(`/qr-codes/${id}`, data),
  deleteQRCode: (id) => api.delete(`/qr-codes/${id}`),
  getQRStats: (id) => api.get(`/qr-codes/${id}/stats`),
};

// QR Designer API
export const qrDesignerAPI = {
  design: (formData) => api.post('/qr-designer/design', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  designAndSave: (formData) => api.post('/qr-designer/design-and-save', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  getStyles: () => api.get('/qr-designer/styles'),
  getTemplates: () => api.get('/qr-designer/templates'),
  preview: (data) => api.post('/qr-designer/preview', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

// Analytics API
export const analyticsAPI = {
  getDashboardStats: (days = 30) => api.get('/analytics/dashboard', { params: { days } }),
  getScanHistory: (params) => api.get('/analytics/scans', { params }),
  getDetailedStats: (params) => api.get('/analytics/detailed', { params }),
};

// Subscriptions API
export const subscriptionsAPI = {
  getPlans: () => api.get('/subscriptions/plans'),
  getPlan: (planId) => api.get(`/subscriptions/plans/${planId}`),
  createSubscription: (data) => api.post('/subscriptions/create', data),
  getSubscription: () => api.get('/subscriptions/current'),
  updateSubscription: (data) => api.put('/subscriptions/update', data),
  cancelSubscription: () => api.post('/subscriptions/cancel'),
  getPaymentMethods: () => api.get('/subscriptions/payment-methods'),
  addPaymentMethod: (data) => api.post('/subscriptions/payment-methods', data),
  setDefaultPaymentMethod: (methodId) => api.post(`/subscriptions/payment-methods/${methodId}/default`),
  deletePaymentMethod: (methodId) => api.delete(`/subscriptions/payment-methods/${methodId}`),
};

// Rate Limits API
export const rateLimitsAPI = {
  getUsage: () => api.get('/rate-limits/usage'),
  getLimits: () => api.get('/rate-limits/limits'),
  getStatus: () => api.get('/rate-limits/status'),
  resetLimits: () => api.post('/rate-limits/reset'),
};

export default api;
