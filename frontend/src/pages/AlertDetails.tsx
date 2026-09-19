/**
 * Alert Details Page
 * Detailed view of a single fraud alert
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { adminAPI, Alert } from '../api/admin';
import { transactionAPI } from '../api/transactions';
import { Transaction } from '../types/transaction';
import { RiskBadge } from '../components/RiskBadge';

export const AlertDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [alert, setAlert] = useState<Alert | null>(null);
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    const fetchAlert = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const alertData = await adminAPI.getAlert(parseInt(id));
        setAlert(alertData);

        // Fetch associated transaction
        if (alertData.transaction_id) {
          try {
            const txData = await transactionAPI.getTransaction(alertData.transaction_id);
            setTransaction(txData);
          } catch (err) {
            console.error('Failed to fetch transaction:', err);
          }
        }

        setError(null);
      } catch (err: any) {
        const message = err.response?.data?.detail || 'Failed to load alert';
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchAlert();
  }, [id]);

  const handleStatusChange = async (newStatus: 'OPEN' | 'REVIEWED' | 'RESOLVED') => {
    if (!alert) return;

    try {
      setUpdating(true);
      const updated = await adminAPI.updateAlertStatus(alert.id, newStatus);
      setAlert(updated);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update alert');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-4xl mx-auto flex items-center justify-center h-96">
          <div className="text-white">Loading alert details...</div>
        </div>
      </div>
    );
  }

  if (error || !alert) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/admin/alerts')}
            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Alerts
          </button>
          <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
            <p className="text-red-200">{error || 'Alert not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'OPEN':
        return 'bg-red-500/20 border-red-500/50 text-red-400';
      case 'REVIEWED':
        return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400';
      case 'RESOLVED':
        return 'bg-green-500/20 border-green-500/50 text-green-400';
      default:
        return 'bg-gray-500/20 border-gray-500/50 text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/admin/alerts')}
          className="flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-8"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Alerts
        </button>

        {/* Alert Header */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Alert #{alert.id}</h1>
              <p className="text-gray-400">
                Transaction #{alert.transaction_id} • {new Date(alert.created_at).toLocaleString()}
              </p>
            </div>
            <div className={`px-4 py-2 rounded-lg border font-medium ${getStatusColor(alert.status)}`}>
              {alert.status}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-400 mb-2">Fraud Probability</p>
              <p className="text-2xl font-bold text-white">
                {((alert.fraud_probability || 0) * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-2">Risk Level</p>
              {alert.risk_level && <RiskBadge level={alert.risk_level as any} size="md" />}
            </div>
            <div>
              <p className="text-sm text-gray-400 mb-2">Alert Type</p>
              <p className="text-xl font-bold text-white">High Risk</p>
            </div>
          </div>
        </div>

        {/* Associated Transaction */}
        {transaction && (
          <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8 mb-6">
            <h2 className="text-xl font-semibold text-white mb-6">Associated Transaction</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Transaction ID</span>
                  <span className="text-white font-medium">#{transaction.id}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Amount</span>
                  <span className="text-white font-medium">
                    ${transaction.amount?.toLocaleString('en-US', {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 2,
                    })}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Date</span>
                  <span className="text-white font-medium">
                    {new Date(transaction.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Prediction</span>
                  <span className="text-white font-medium capitalize">{transaction.prediction}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Risk Level</span>
                  <RiskBadge level={(transaction.risk_level as any) || 'LOW'} size="sm" />
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Model Version</span>
                  <span className="text-white font-medium">{transaction.model_version || 'N/A'}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Status Actions */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8">
          <h2 className="text-xl font-semibold text-white mb-6">Alert Management</h2>

          <div className="space-y-3">
            <p className="text-gray-300 mb-4">Change alert status:</p>

            <div className="flex flex-wrap gap-3">
              {alert.status !== 'REVIEWED' && (
                <button
                  onClick={() => handleStatusChange('REVIEWED')}
                  disabled={updating}
                  className="px-6 py-3 bg-yellow-600 hover:bg-yellow-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition"
                >
                  {updating ? 'Updating...' : 'Mark as Reviewed'}
                </button>
              )}

              {alert.status !== 'RESOLVED' && (
                <button
                  onClick={() => handleStatusChange('RESOLVED')}
                  disabled={updating}
                  className="px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition"
                >
                  {updating ? 'Updating...' : 'Mark as Resolved'}
                </button>
              )}

              {alert.status !== 'OPEN' && (
                <button
                  onClick={() => handleStatusChange('OPEN')}
                  disabled={updating}
                  className="px-6 py-3 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition"
                >
                  {updating ? 'Updating...' : 'Reopen'}
                </button>
              )}
            </div>
          </div>

          <div className="mt-6 p-4 bg-blue-500/20 border border-blue-500/50 rounded-lg">
            <p className="text-blue-200 text-sm">
              Alert status has been updated. Any changes are recorded in the audit log for compliance
              purposes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
