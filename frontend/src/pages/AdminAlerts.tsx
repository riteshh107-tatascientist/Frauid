/**
 * Admin Alerts Page
 * Displays and manages fraud alerts with filtering and status updates
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { RefreshCw, ChevronLeft, ChevronRight } from 'lucide-react';
import { adminAPI, Alert, AlertListResponse } from '../api/admin';
import { RiskBadge } from '../components/RiskBadge';

export const AdminAlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [skip, setSkip] = useState(0);
  const [limit] = useState(20);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchAlerts = async (skipValue: number) => {
    try {
      setLoading(true);
      setError(null);

      const response = await adminAPI.listAlerts({
        status_filter: statusFilter || undefined,
        skip: skipValue,
        limit,
      });

      setAlerts(response.alerts || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts(skip);
  }, [skip, statusFilter]);

  const handleStatusChange = async (alertId: number, newStatus: 'OPEN' | 'REVIEWED' | 'RESOLVED') => {
    try {
      await adminAPI.updateAlertStatus(alertId, newStatus);
      setSuccessMessage(`Alert marked as ${newStatus.toLowerCase()}`);
      setTimeout(() => setSuccessMessage(null), 3000);
      fetchAlerts(skip);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update alert');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OPEN':
        return 'text-red-400 bg-red-500/20 border-red-500/50';
      case 'REVIEWED':
        return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50';
      case 'RESOLVED':
        return 'text-green-400 bg-green-500/20 border-green-500/50';
      default:
        return 'text-gray-400 bg-gray-500/20 border-gray-500/50';
    }
  };

  if (loading && alerts.length === 0) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-6xl mx-auto flex items-center justify-center h-96">
          <div className="text-white">Loading alerts...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-white">Fraud Alerts</h1>
          <button
            onClick={() => fetchAlerts(skip)}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition"
            disabled={loading}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {successMessage && (
          <div className="mb-6 p-4 bg-green-500/20 border border-green-500/50 rounded-lg">
            <p className="text-green-200">{successMessage}</p>
          </div>
        )}

        {/* Filters */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Filters</h2>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => {
                setStatusFilter(e.target.value);
                setSkip(0);
              }}
              className="w-full md:w-48 px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-500"
            >
              <option value="">All Statuses</option>
              <option value="OPEN">Open</option>
              <option value="REVIEWED">Reviewed</option>
              <option value="RESOLVED">Resolved</option>
            </select>
          </div>
        </div>

        {/* Alerts List */}
        <div className="space-y-4">
          {alerts.length === 0 ? (
            <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8 text-center">
              <p className="text-gray-400">No alerts found</p>
            </div>
          ) : (
            alerts.map((alert) => (
              <div
                key={alert.id}
                className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition"
              >
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Alert #{alert.id}</h3>
                    <p className="text-sm text-gray-400">
                      Transaction #{alert.transaction_id} • {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {alert.risk_level && <RiskBadge level={alert.risk_level as any} size="md" />}
                    <div className={`px-3 py-1 rounded-lg border text-sm font-medium ${getStatusColor(alert.status)}`}>
                      {alert.status}
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div>
                    <p className="text-xs text-gray-400 mb-1">Fraud Probability</p>
                    <p className="text-lg font-semibold text-white">
                      {((alert.fraud_probability || 0) * 100).toFixed(2)}%
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 mb-1">Risk Level</p>
                    <p className="text-white font-semibold">{alert.risk_level || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 mb-1">Status</p>
                    <p className="text-white font-semibold">{alert.status}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 mb-1">Created</p>
                    <p className="text-white font-semibold">{new Date(alert.created_at).toLocaleDateString()}</p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-3">
                  <Link
                    to={`/admin/alerts/${alert.id}`}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
                  >
                    View Details
                  </Link>

                  {alert.status !== 'REVIEWED' && (
                    <button
                      onClick={() => handleStatusChange(alert.id, 'REVIEWED')}
                      className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium transition"
                    >
                      Mark Reviewed
                    </button>
                  )}

                  {alert.status !== 'RESOLVED' && (
                    <button
                      onClick={() => handleStatusChange(alert.id, 'RESOLVED')}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition"
                    >
                      Mark Resolved
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {alerts.length > 0 && (
          <div className="flex items-center justify-between mt-6 px-6 py-4 backdrop-blur-md bg-white/10 rounded-xl border border-white/20">
            <div className="text-sm text-gray-400">Showing {alerts.length} alerts</div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSkip(Math.max(0, skip - limit))}
                disabled={skip === 0}
                className="p-2 hover:bg-white/10 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <ChevronLeft className="w-5 h-5 text-gray-300" />
              </button>
              <button
                onClick={() => setSkip(skip + limit)}
                disabled={alerts.length < limit}
                className="p-2 hover:bg-white/10 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <ChevronRight className="w-5 h-5 text-gray-300" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
