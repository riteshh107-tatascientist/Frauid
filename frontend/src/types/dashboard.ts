/**
 * Dashboard Types
 * Based on Phase 3 dashboard API responses
 */

export interface DashboardSummary {
  total_transactions: number;
  fraud_transactions: number;
  legitimate_transactions: number;
  high_risk_transactions: number;
  medium_risk_transactions: number;
  low_risk_transactions: number;
  fraud_percentage: number;
}

export interface RiskTrend {
  date: string;
  transactions: number;
  fraud: number;
  fraud_percentage: number;
}

export interface ModelInfo {
  model_name: string;
  model_version: string;
  threshold: number;
  features: string[];
  feature_count: number;
  metrics: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1?: number;
    roc_auc?: number;
    pr_auc?: number;
  };
  dataset?: {
    name?: string;
    total_samples?: number;
    fraud_percentage?: number;
  };
}

export interface AlertStatus {
  id: number;
  user_id: number;
  transaction_id: number;
  status: 'OPEN' | 'REVIEWED' | 'RESOLVED';
  risk_score: number;
  reason?: string;
  created_at: string;
  updated_at: string;
}
