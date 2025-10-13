import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { QRProvider } from './contexts/QRContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import QRDesigner from './pages/QRDesigner';
import QRScanner from './pages/QRScanner';
import Analytics from './pages/Analytics';
import QRManagement from './pages/QRManagement';
import Settings from './pages/Settings';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <QRProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="qr-designer" element={<QRDesigner />} />
            <Route path="qr-scanner" element={<QRScanner />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="qr-management" element={<QRManagement />} />
            <Route path="settings" element={<Settings />} />
          </Route>
        </Routes>
      </QRProvider>
    </AuthProvider>
  );
}

export default App;
