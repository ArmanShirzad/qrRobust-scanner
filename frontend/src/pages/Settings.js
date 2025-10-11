import React, { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Lock, 
  CreditCard, 
  Bell, 
  Shield,
  Download,
  Upload,
  Save
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { subscriptionsAPI, rateLimitsAPI } from '../services/api';
import toast from 'react-hot-toast';

const Settings = () => {
  const { user, changePassword } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [profileData, setProfileData] = useState({
    email: user?.email || '',
    tier: user?.tier || 'free'
  });
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [subscription, setSubscription] = useState(null);
  const [rateLimits, setRateLimits] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSubscriptionData();
    fetchRateLimits();
  }, []);

  const fetchSubscriptionData = async () => {
    try {
      const response = await subscriptionsAPI.getSubscription();
      setSubscription(response.data);
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
    }
  };

  const fetchRateLimits = async () => {
    try {
      const response = await rateLimitsAPI.getLimits();
      setRateLimits(response.data);
    } catch (error) {
      console.error('Failed to fetch rate limits:', error);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwordData.new_password.length < 8) {
      toast.error('Password must be at least 8 characters long');
      return;
    }

    setLoading(true);
    try {
      const result = await changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      
      if (result.success) {
        setPasswordData({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
      }
    } catch (error) {
      console.error('Password change error:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'security', name: 'Security', icon: Lock },
    { id: 'subscription', name: 'Subscription', icon: CreditCard },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'privacy', name: 'Privacy', icon: Shield },
  ];

  const getTierColor = (tier) => {
    const colors = {
      'free': 'bg-gray-100 text-gray-800',
      'pro': 'bg-blue-100 text-blue-800',
      'business': 'bg-purple-100 text-purple-800',
      'enterprise': 'bg-green-100 text-green-800'
    };
    return colors[tier] || colors['free'];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account settings and preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <div className="card">
            <nav className="space-y-1">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-700'
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="mr-3 h-5 w-5" />
                    {tab.name}
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Profile Information</h3>
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email Address
                  </label>
                  <div className="flex items-center space-x-3">
                    <Mail className="h-5 w-5 text-gray-400" />
                    <span className="text-gray-900">{profileData.email}</span>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getTierColor(profileData.tier)}`}>
                      {profileData.tier} Plan
                    </span>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Account Status
                  </label>
                  <div className="flex items-center space-x-3">
                    <div className="h-2 w-2 bg-green-400 rounded-full"></div>
                    <span className="text-gray-900">Active</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Member Since
                  </label>
                  <span className="text-gray-900">
                    {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Security Tab */}
          {activeTab === 'security' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Change Password</h3>
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Current Password
                  </label>
                  <input
                    type="password"
                    className="input-field"
                    value={passwordData.current_password}
                    onChange={(e) => setPasswordData(prev => ({
                      ...prev,
                      current_password: e.target.value
                    }))}
                    required
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    New Password
                  </label>
                  <input
                    type="password"
                    className="input-field"
                    value={passwordData.new_password}
                    onChange={(e) => setPasswordData(prev => ({
                      ...prev,
                      new_password: e.target.value
                    }))}
                    required
                    minLength={8}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confirm New Password
                  </label>
                  <input
                    type="password"
                    className="input-field"
                    value={passwordData.confirm_password}
                    onChange={(e) => setPasswordData(prev => ({
                      ...prev,
                      confirm_password: e.target.value
                    }))}
                    required
                    minLength={8}
                  />
                </div>
                
                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary flex items-center"
                >
                  {loading ? (
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  ) : (
                    <>
                      <Save className="h-5 w-5 mr-2" />
                      Update Password
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Subscription Tab */}
          {activeTab === 'subscription' && (
            <div className="space-y-6">
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Plan</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="flex items-center space-x-3">
                      <span className={`px-3 py-1 text-sm font-medium rounded-full ${getTierColor(profileData.tier)}`}>
                        {profileData.tier.toUpperCase()} Plan
                      </span>
                      <span className="text-gray-600">
                        {profileData.tier === 'free' ? 'Free' : `$${subscription?.price || 0}/month`}
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">
                      {profileData.tier === 'free' 
                        ? 'Basic features with limited scans'
                        : 'Full access to all features'
                      }
                    </p>
                  </div>
                  <button className="btn-primary">
                    {profileData.tier === 'free' ? 'Upgrade Plan' : 'Manage Subscription'}
                  </button>
                </div>
              </div>

              {rateLimits && (
                <div className="card">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Limits</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">
                        {rateLimits.limits.per_minute}
                      </div>
                      <div className="text-sm text-gray-500">Per Minute</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">
                        {rateLimits.limits.per_hour}
                      </div>
                      <div className="text-sm text-gray-500">Per Hour</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-gray-900">
                        {rateLimits.limits.per_day}
                      </div>
                      <div className="text-sm text-gray-500">Per Day</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Notification Preferences</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">Email Notifications</div>
                    <div className="text-sm text-gray-500">Receive updates via email</div>
                  </div>
                  <input type="checkbox" className="h-4 w-4 text-blue-600" defaultChecked />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">Scan Alerts</div>
                    <div className="text-sm text-gray-500">Get notified when QR codes are scanned</div>
                  </div>
                  <input type="checkbox" className="h-4 w-4 text-blue-600" defaultChecked />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">Weekly Reports</div>
                    <div className="text-sm text-gray-500">Receive weekly analytics summaries</div>
                  </div>
                  <input type="checkbox" className="h-4 w-4 text-blue-600" />
                </div>
              </div>
            </div>
          )}

          {/* Privacy Tab */}
          {activeTab === 'privacy' && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Privacy Settings</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">Analytics Tracking</div>
                    <div className="text-sm text-gray-500">Allow analytics data collection</div>
                  </div>
                  <input type="checkbox" className="h-4 w-4 text-blue-600" defaultChecked />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">Data Export</div>
                    <div className="text-sm text-gray-500">Allow data export for analysis</div>
                  </div>
                  <input type="checkbox" className="h-4 w-4 text-blue-600" defaultChecked />
                </div>
                
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm font-medium text-gray-900">Marketing Communications</div>
                    <div className="text-sm text-gray-500">Receive marketing emails and updates</div>
                  </div>
                  <input type="checkbox" className="h-4 w-4 text-blue-600" />
                </div>
              </div>
              
              <div className="mt-6 pt-6 border-t border-gray-200">
                <button className="btn-secondary flex items-center">
                  <Download className="h-5 w-5 mr-2" />
                  Download My Data
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Settings;
