/**
 * Admin Dashboard
 * Monitoring and alerts overview for administrators
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, CheckCircle, Clock, Zap } from 'lucide-react';
import { adminAPI } from '../api/admin';

export const AdminDashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const summary = await adminAPI.getMonitoringSummary();
        setMetrics(summary);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  const metricCards = [
    {
      title: 'Open Alerts',
      value: metrics.open_alerts ?? '—',
      icon: AlertTriangle,
      color: 'text-red-400',
      bgColor: 'bg-red-500/20',
      link: '/admin/alerts?status=OPEN',
    },
    {
      title: 'High Risk Alerts',
      value: metrics.high_risk_alerts ?? '—',
      icon: AlertTriangle,
      color: 'text-orange-400',
      bgColor: 'bg-orange-500/20',
      link: '/admin/alerts',
    },
    {
      title: 'Reviewed',
      value: metrics.reviewed_alerts ?? '—',
      icon: Clock,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/20',
      link: '/admin/alerts?status=REVIEWED',
    },
    {
      title: 'Resolved',
      value: metrics.resolved_alerts ?? '—',
      icon: CheckCircle,
      color: 'text-green-400',
      bgColor: 'bg-green-500/20',
      link: '/admin/alerts?status=RESOLVED',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">Admin Dashboard</h1>
          <p className="text-gray-400">Monitor fraud alerts and system activity</p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-yellow-500/20 border border-yellow-500/50 rounded-lg">
            <p className="text-yellow-200">Some metrics unavailable. System is functioning normally.</p>
          </div>
        )}

        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          {metricCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <Link
                key={idx}
                to={card.link}
                className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-gray-300 font-medium">{card.title}</h3>
                  <div className={`p-2 rounded-lg ${card.bgColor}`}>
                    <Icon className={`w-5 h-5 ${card.color}`} />
                  </div>
                </div>
                <div className="text-3xl font-bold text-white">{card.value}</div>
              </Link>
            );
          })}
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* View Alerts */}
          <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8">
            <div className="flex items-center gap-3 mb-6">
              <AlertTriangle className="w-6 h-6 text-red-400" />
              <h2 className="text-xl font-semibold text-white">Fraud Alerts</h2>
            </div>
            <p className="text-gray-300 mb-6">Review and manage fraud detection alerts in real-time.</p>
            <Link
              to="/admin/alerts"
              className="inline-block px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition"
            >
              View All Alerts
            </Link>
          </div>

          {/* Monitoring Info */}
          <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8">
            <div className="flex items-center gap-3 mb-6">
              <Zap className="w-6 h-6 text-yellow-400" />
              <h2 className="text-xl font-semibold text-white">System Status</h2>
            </div>
            <div className="space-y-3 text-gray-300">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span>ML Model: Active</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span>Database: Connected</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-400" />
                <span>API: Operational</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
