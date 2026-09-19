/**
 * Transaction Details Page
 * Detailed view of a single transaction with prediction and risk information
 */

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Zap } from 'lucide-react';
import { transactionAPI } from '../api/transactions';
import { Transaction } from '../types/transaction';
import { RiskBadge } from '../components/RiskBadge';
import { SHAPExplanation } from '../components/SHAPExplanation';

export const TransactionDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [transaction, setTransaction] = useState<Transaction | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [explanation, setExplanation] = useState<any | null>(null);
  const [explanationLoading, setExplanationLoading] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);
  const [explanationError, setExplanationError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTransaction = async () => {
      if (!id) return;

      try {
        setLoading(true);
        const data = await transactionAPI.getTransaction(parseInt(id));
        setTransaction(data);
        setError(null);
      } catch (err: any) {
        const message = err.response?.data?.detail || 'Failed to load transaction';
        setError(message);

        // Handle 404 or 403 (IDOR protection)
        if (err.response?.status === 404 || err.response?.status === 403) {
          setTimeout(() => navigate('/transactions'), 2000);
        }
      } finally {
        setLoading(false);
      }
    };

    fetchTransaction();
  }, [id, navigate]);

  const handleFetchExplanation = async () => {
    if (!id) return;
    
    try {
      setExplanationLoading(true);
      setExplanationError(null);
      
      const response = await fetch(`/api/transactions/${id}/explanation`, {
        headers: {
          'Authorization': `Bearer ${sessionStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Transaction not found');
        } else if (response.status === 503) {
          throw new Error('Explanation service temporarily unavailable');
        } else {
          throw new Error('Failed to generate explanation');
        }
      }
      
      const data = await response.json();
      setExplanation(data);
      setShowExplanation(true);
    } catch (err: any) {
      setExplanationError(err.message || 'Failed to generate explanation');
    } finally {
      setExplanationLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-4xl mx-auto flex items-center justify-center h-96">
          <div className="text-white">Loading transaction details...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/transactions')}
            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Transactions
          </button>
          <div className="p-4 bg-red-500/20 border border-red-500/50 rounded-lg">
            <p className="text-red-200">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!transaction) {
    return (
      <div className="min-h-screen bg-gray-950 p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/transactions')}
            className="flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-6"
          >
            <ArrowLeft className="w-5 h-5" />
            Back to Transactions
          </button>
          <p className="text-gray-400">Transaction not found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 p-8">
      <div className="max-w-4xl mx-auto">
        <button
          onClick={() => navigate('/transactions')}
          className="flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-8"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Transactions
        </button>

        {/* Transaction Info */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">Transaction #{transaction.id}</h1>
              <p className="text-gray-400">
                {new Date(transaction.created_at).toLocaleString()}
              </p>
            </div>
            <RiskBadge level={(transaction.risk_level as any) || 'LOW'} size="lg" />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Transaction Details */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white mb-4">Transaction Details</h2>

              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-gray-400">Amount</span>
                <span className="text-white font-medium">
                  ${transaction.amount?.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2,
                  })}
                </span>
              </div>

              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-gray-400">Prediction</span>
                <span className="text-white font-medium capitalize">{transaction.prediction}</span>
              </div>

              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-gray-400">Date</span>
                <span className="text-white font-medium">
                  {new Date(transaction.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>

            {/* AI Prediction */}
            <div className="space-y-4">
              <h2 className="text-lg font-semibold text-white mb-4">AI Prediction</h2>

              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-gray-400">Fraud Probability</span>
                <span className="text-white font-medium">
                  {((transaction.fraud_probability || 0) * 100).toFixed(2)}%
                </span>
              </div>

              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-gray-400">Risk Score</span>
                <span className="text-white font-medium">
                  {(transaction.risk_score || 0).toFixed(2)}
                </span>
              </div>

              <div className="flex justify-between items-center py-2 border-b border-white/10">
                <span className="text-gray-400">Risk Level</span>
                <RiskBadge level={(transaction.risk_level as any) || 'LOW'} size="sm" />
              </div>

              <div className="flex justify-between items-center py-2">
                <span className="text-gray-400">Model Version</span>
                <span className="text-white font-medium">{transaction.model_version || 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Risk Analysis */}
        <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-8">
          <h2 className="text-lg font-semibold text-white mb-4">Risk Analysis</h2>

          {transaction.fraud_probability !== undefined && (
            <div className="mb-4">
              <div className="flex justify-between items-center mb-2">
                <span className="text-gray-300">Fraud Probability</span>
                <span className="text-white font-medium">
                  {((transaction.fraud_probability || 0) * 100).toFixed(2)}%
                </span>
              </div>
              <div className="w-full bg-gray-900 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full transition-all ${
                    transaction.fraud_probability < 0.3
                      ? 'bg-green-500'
                      : transaction.fraud_probability < 0.7
                      ? 'bg-yellow-500'
                      : 'bg-red-500'
                  }`}
                  style={{ width: `${(transaction.fraud_probability || 0) * 100}%` }}
                />
              </div>
            </div>
          )}

          <div className="mt-6 p-4 bg-blue-500/20 border border-blue-500/50 rounded-lg mb-6">
            <p className="text-blue-200 text-sm">
              This transaction has been analyzed using our AI fraud detection model. The prediction is
              based on multiple features extracted from the transaction data.
            </p>
          </div>

          {/* Explanation Button */}
          <button
            onClick={handleFetchExplanation}
            disabled={explanationLoading}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg font-medium transition"
          >
            <Zap className="w-4 h-4" />
            {explanationLoading ? 'Generating Explanation...' : 'Why this prediction?'}
          </button>
        </div>

        {/* SHAP Explanation Section */}
        {showExplanation && explanation && (
          <div className="mt-8">
            <div className="flex items-center gap-2 mb-6">
              <Zap className="w-5 h-5 text-yellow-400" />
              <h2 className="text-xl font-semibold text-white">AI Prediction Explanation</h2>
            </div>
            <SHAPExplanation
              topFeatures={explanation.top_features}
              baseValue={explanation.base_value}
              fraudProbability={explanation.fraud_probability}
              featureCount={explanation.feature_count}
              modelVersion={explanation.model_version}
              explainerType={explanation.explainer_type}
              shapNote={explanation.shap_note}
            />
          </div>
        )}

        {/* Explanation Error */}
        {explanationError && (
          <div className="mt-8 p-6 bg-red-500/20 border border-red-500/50 rounded-xl">
            <p className="text-red-200">{explanationError}</p>
          </div>
        )}
      </div>
    </div>
  );
};
