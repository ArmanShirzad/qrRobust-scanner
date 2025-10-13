import React, { useState, useEffect, useCallback } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { Download } from 'lucide-react';
import { analyticsAPI } from '../services/api';
import toast from 'react-hot-toast';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [timeRange, setTimeRange] = useState(30);

  const fetchAnalytics = useCallback(async () => {
    try {
      setLoading(true);
      const response = await analyticsAPI.getDashboardStats(timeRange);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
      toast.error('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  }, [timeRange]);

  const handleExportData = async () => {
    try {
      setLoading(true);
      const response = await analyticsAPI.getDetailedStats({
        days: timeRange,
        format: 'csv'
      });
      
      // Create and download CSV file
      const blob = new Blob([response.data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `analytics-export-${new Date().toISOString().split('T')[0]}.csv`;
      link.click();
      window.URL.revokeObjectURL(url);
      
      toast.success('Analytics data exported successfully!');
    } catch (error) {
      console.error('Failed to export analytics:', error);
      toast.error('Failed to export analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange, fetchAnalytics]);

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Detailed insights into your QR code performance</p>
        </div>
        <div className="flex space-x-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(parseInt(e.target.value))}
            className="input-field"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last year</option>
          </select>
          <button 
            onClick={handleExportData}
            disabled={loading}
            className="btn-secondary flex items-center"
          >
            <Download className="h-4 w-4 mr-2" />
            Export
          </button>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scan Trends */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Scan Trends</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={analytics?.scan_trends || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="scans" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Device Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Device Types</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={analytics?.device_stats || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(analytics?.device_stats || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Browser Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Browser Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.browser_stats || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="browser" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#10B981" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Geographic Distribution */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Countries</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={analytics?.country_stats || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="country" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#F59E0B" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Detailed Stats Table */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Detailed Statistics</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Metric
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Value
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Change
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Total Scans
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {analytics?.total_scans || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                  +12%
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Unique Visitors
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {analytics?.unique_visitors || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                  +8%
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Mobile Scans
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {analytics?.mobile_scans || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600">
                  +15%
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  Desktop Scans
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {analytics?.desktop_scans || 0}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-red-600">
                  -3%
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
