/**
 * Transactions Page
 * Displays user's transaction history with filtering, sorting, and pagination
 */

import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ChevronLeft, ChevronRight, RefreshCw } from 'lucide-react';
import { transactionAPI } from '../api/transactions';
import { Transaction, TransactionListResponse } from '../types/transaction';
import { RiskBadge } from '../components/RiskBadge';

export const TransactionsPage: React.FC = () => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [riskLevelFilter, setRiskLevelFilter] = useState<string>('');
  const [predictionFilter, setPredictionFilter] = useState<string>('');

  const fetchTransactions = async (pageNum: number) => {
    try {
      setLoading(true);
      setError(null);

      const response = await transactionAPI.listTransactions({
        page: pageNum,
        page_size: pageSize,
        risk_level: riskLevelFilter || undefined,
        prediction: predictionFilter || undefined,
      });

      setTransactions(response.items || []);

      if (response.total && response.page_size) {
        setTotalPages(Math.ceil(response.total / response.page_size));
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load transactions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions(page);
  }, [page, pageSize, riskLevelFilter, predictionFilter]);

  const handleFilterChange = () => {
    setPage(1); // Reset to first page when filters change
  };

  const handleRefresh = () => {
    fetchTransactions(page);
  };

  if (loading && transactions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-6xl mx-auto">
          <div className="flex items-center justify-center h-96">
            <div className="text-white">Loading transactions...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-white">Transaction History</h1>
          <button
            onClick={handleRefresh}
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

        {/* Filters */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 mb-6">
          <h2 className="text-lg font-semibold text-white mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Risk Level Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Risk Level</label>
              <select
                value={riskLevelFilter}
                onChange={(e) => {
                  setRiskLevelFilter(e.target.value);
                  handleFilterChange();
                }}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All</option>
                <option value="LOW">Low</option>
                <option value="MEDIUM">Medium</option>
                <option value="HIGH">High</option>
              </select>
            </div>

            {/* Prediction Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Prediction</label>
              <select
                value={predictionFilter}
                onChange={(e) => {
                  setPredictionFilter(e.target.value);
                  handleFilterChange();
                }}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-blue-500"
              >
                <option value="">All</option>
                <option value="fraud">Fraud</option>
                <option value="legitimate">Legitimate</option>
              </select>
            </div>
          </div>
        </div>

        {/* Transaction Table */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 overflow-hidden">
          {transactions.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-400">No transactions found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10 bg-white/5">
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">ID</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Date</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Amount</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Prediction</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Probability</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Risk Level</th>
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-300">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx) => (
                    <tr key={tx.id} className="border-b border-white/5 hover:bg-white/5 transition">
                      <td className="px-6 py-4 text-sm text-gray-300">#{tx.id}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {new Date(tx.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 text-sm font-medium text-white">
                        ${tx.amount?.toLocaleString('en-US', {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300 capitalize">{tx.prediction}</td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {((tx.fraud_probability || 0) * 100).toFixed(2)}%
                      </td>
                      <td className="px-6 py-4">
                        <RiskBadge level={(tx.risk_level as any) || 'LOW'} size="sm" />
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <Link
                          to={`/transactions/${tx.id}`}
                          className="text-blue-400 hover:text-blue-300 font-medium"
                        >
                          View
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Pagination */}
          {transactions.length > 0 && (
            <div className="flex items-center justify-between px-6 py-4 border-t border-white/10 bg-white/5">
              <div className="text-sm text-gray-400">
                Page {page} of {totalPages}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setPage(Math.max(1, page - 1))}
                  disabled={page === 1}
                  className="p-2 hover:bg-white/10 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <ChevronLeft className="w-5 h-5 text-gray-300" />
                </button>
                <button
                  onClick={() => setPage(Math.min(totalPages, page + 1))}
                  disabled={page >= totalPages}
                  className="p-2 hover:bg-white/10 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition"
                >
                  <ChevronRight className="w-5 h-5 text-gray-300" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
