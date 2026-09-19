/**
 * SHAP Explanation Component
 * Displays model feature contributions using SHAP values
 */

import React from 'react';
import { AlertCircle } from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface FeatureContribution {
  feature: string;
  feature_value: number;
  shap_value: number;
  direction: 'toward_fraud' | 'toward_legitimate';
  impact: 'high' | 'medium' | 'low';
  abs_contribution: number;
}

interface SHAPExplanationProps {
  topFeatures: FeatureContribution[];
  baseValue: number;
  fraudProbability: number;
  featureCount: number;
  modelVersion: string;
  explainerType: string;
  shapNote: string;
}

export const SHAPExplanation: React.FC<SHAPExplanationProps> = ({
  topFeatures,
  baseValue,
  fraudProbability,
  featureCount,
  modelVersion,
  explainerType,
  shapNote,
}) => {
  if (!topFeatures || topFeatures.length === 0) {
    return (
      <div className="p-6 bg-yellow-500/20 border border-yellow-500/50 rounded-lg">
        <p className="text-yellow-200">No features available for explanation</p>
      </div>
    );
  }

  // Prepare chart data
  const chartData = topFeatures.map((feature) => ({
    name: feature.feature,
    value: feature.shap_value,
    abs_value: feature.abs_contribution,
    direction: feature.direction,
  }));

  // Get color based on direction
  const getFeatureColor = (direction: string) => {
    return direction === 'toward_fraud' ? '#ef4444' : '#10b981';
  };

  return (
    <div className="space-y-6">
      {/* SHAP Chart */}
      <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Feature Contributions (SHAP)</h3>
        <p className="text-gray-400 text-sm mb-4">
          Shows how each feature contributed to the fraud prediction
        </p>

        <ResponsiveContainer width="100%" height={400}>
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
            <XAxis type="number" stroke="#9ca3af" />
            <YAxis dataKey="name" type="category" stroke="#9ca3af" width={190} />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(17, 24, 39, 0.95)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '0.5rem',
              }}
              labelStyle={{ color: '#fff' }}
              formatter={(value: any) => value.toFixed(4)}
            />
            <Bar dataKey="value" fill="#3b82f6" radius={[0, 8, 8, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getFeatureColor(entry.direction)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>

        <div className="mt-4 flex gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500 rounded" />
            <span className="text-gray-300">Toward Fraud</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500 rounded" />
            <span className="text-gray-300">Toward Legitimate</span>
          </div>
        </div>
      </div>

      {/* Top Features Table */}
      <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Top Contributing Features</h3>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10">
                <th className="px-4 py-3 text-left font-semibold text-gray-300">Feature</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-300">Value</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-300">SHAP Value</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-300">Direction</th>
                <th className="px-4 py-3 text-left font-semibold text-gray-300">Impact</th>
              </tr>
            </thead>
            <tbody>
              {topFeatures.map((feature, idx) => (
                <tr key={idx} className="border-b border-white/5 hover:bg-white/5 transition">
                  <td className="px-4 py-3 text-white font-mono">{feature.feature}</td>
                  <td className="px-4 py-3 text-right text-gray-300">
                    {feature.feature_value.toFixed(4)}
                  </td>
                  <td className="px-4 py-3 text-right font-mono">
                    <span
                      className={
                        feature.shap_value > 0 ? 'text-red-400' : 'text-green-400'
                      }
                    >
                      {feature.shap_value > 0 ? '+' : ''}
                      {feature.shap_value.toFixed(4)}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        feature.direction === 'toward_fraud'
                          ? 'bg-red-500/20 text-red-300'
                          : 'bg-green-500/20 text-green-300'
                      }`}
                    >
                      {feature.direction === 'toward_fraud' ? 'Fraud' : 'Legit'}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`px-2 py-1 rounded text-xs font-medium ${
                        feature.impact === 'high'
                          ? 'bg-red-500/20 text-red-300'
                          : feature.impact === 'medium'
                          ? 'bg-yellow-500/20 text-yellow-300'
                          : 'bg-green-500/20 text-green-300'
                      }`}
                    >
                      {feature.impact.charAt(0).toUpperCase() + feature.impact.slice(1)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* SHAP Metadata */}
      <div className="backdrop-blur-md bg-white/10 rounded-xl border border-white/20 p-6 space-y-4">
        <h3 className="text-lg font-semibold text-white">Explanation Details</h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex justify-between py-2 border-b border-white/10">
            <span className="text-gray-400">Base Value</span>
            <span className="text-white font-mono">{baseValue.toFixed(6)}</span>
          </div>

          <div className="flex justify-between py-2 border-b border-white/10">
            <span className="text-gray-400">Model Output</span>
            <span className="text-white font-mono">{fraudProbability.toFixed(4)}</span>
          </div>

          <div className="flex justify-between py-2 border-b border-white/10">
            <span className="text-gray-400">Features Analyzed</span>
            <span className="text-white font-mono">{featureCount}</span>
          </div>

          <div className="flex justify-between py-2 border-b border-white/10">
            <span className="text-gray-400">Model Version</span>
            <span className="text-white font-mono">{modelVersion}</span>
          </div>

          <div className="flex justify-between py-2 border-b border-white/10">
            <span className="text-gray-400">Explainer Type</span>
            <span className="text-white font-mono">{explainerType}</span>
          </div>
        </div>
      </div>

      {/* Important Notes */}
      <div className="backdrop-blur-md bg-blue-500/20 border border-blue-500/50 rounded-xl p-6 space-y-3">
        <div className="flex gap-3">
          <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="font-semibold text-blue-200 mb-2">Important</h4>
            <p className="text-blue-100 text-sm mb-3">
              {shapNote}
            </p>
            <p className="text-blue-100 text-sm">
              SHAP shows how individual model features influenced this prediction. It does not prove
              that a transaction is fraudulent. Use predictions as one factor in your fraud detection
              workflow.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
