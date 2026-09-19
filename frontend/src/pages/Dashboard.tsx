/**
 * Dashboard Page
 * Displays fraud detection statistics from real backend APIs
 */

import React, { useEffect, useState } from 'react';
import { DashboardSummary, RiskTrend } from '../types/dashboard';
import { apiClient } from '../api/client';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [trends, setTrends] = useState<RiskTrend[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch dashboard summary
        const summaryResponse = await apiClient.get<DashboardSummary>('/dashboard/summary');
        setSummary(summaryResponse.data);

        // Fetch risk trends
        const trendsResponse = await apiClient.get<RiskTrend[]>('/dashboard/risk-trends');
        setTrends(trendsResponse.data);

        setError(null);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-950">
        <div className="text-white">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
            <p className="text-red-200">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>

        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {/* Total Transactions */}
            <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition">
              <p className="text-gray-300 text-sm font-medium">Total Transactions</p>
              <p className="text-4xl font-bold text-white mt-2">{summary.total_transactions.toLocaleString()}</p>
              <p className="text-gray-400 text-xs mt-2">All processed transactions</p>
            </div>

            {/* Fraud Transactions */}
            <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition">
              <p className="text-gray-300 text-sm font-medium">Fraud Detected</p>
              <p className="text-4xl font-bold text-red-400 mt-2">{summary.fraud_transactions.toLocaleString()}</p>
              <p className="text-gray-400 text-xs mt-2">{summary.fraud_percentage.toFixed(2)}% fraud rate</p>
            </div>

            {/* High Risk Transactions */}
            <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition">
              <p className="text-gray-300 text-sm font-medium">High Risk</p>
              <p className="text-4xl font-bold text-orange-400 mt-2">{summary.high_risk_transactions.toLocaleString()}</p>
              <p className="text-gray-400 text-xs mt-2">Require immediate review</p>
            </div>

            {/* Medium Risk */}
            <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition">
              <p className="text-gray-300 text-sm font-medium">Medium Risk</p>
              <p className="text-4xl font-bold text-yellow-400 mt-2">{summary.medium_risk_transactions.toLocaleString()}</p>
              <p className="text-gray-400 text-xs mt-2">Monitor closely</p>
            </div>

            {/* Low Risk */}
            <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition">
              <p className="text-gray-300 text-sm font-medium">Low Risk</p>
              <p className="text-4xl font-bold text-green-400 mt-2">{summary.low_risk_transactions.toLocaleString()}</p>
              <p className="text-gray-400 text-xs mt-2">Legitimate transactions</p>
            </div>

            {/* Legitimate */}
            <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 hover:bg-white/20 transition">
              <p className="text-gray-300 text-sm font-medium">Legitimate</p>
              <p className="text-4xl font-bold text-green-500 mt-2">{summary.legitimate_transactions.toLocaleString()}</p>
              <p className="text-gray-400 text-xs mt-2">{((summary.legitimate_transactions / summary.total_transactions) * 100).toFixed(2)}% of total</p>
            </div>
          </div>
        )}

        {/* Recent Trends */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6">
          <h2 className="text-xl font-bold text-white mb-4">Recent Trends (Last 30 Days)</h2>
          
          {trends.length === 0 ? (
            <p className="text-gray-400">No trend data available</p>
          ) : (
            <div className="space-y-3">
              {trends.slice(-7).map((trend) => (
                <div key={trend.date} className="flex items-center justify-between p-3 bg-white/5 rounded-lg border border-white/10">
                  <div>
                    <p className="text-white font-medium">{new Date(trend.date).toLocaleDateString()}</p>
                    <p className="text-gray-400 text-sm">{trend.transactions} transactions • {trend.fraud} fraud</p>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-semibold">{trend.fraud_percentage.toFixed(2)}%</p>
                    <p className="text-gray-400 text-sm">fraud rate</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
