/**
 * Transaction and Prediction Types
 * Based on Phase 3 backend schemas
 */

export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';
export type Prediction = 'fraud' | 'legitimate';

export interface Transaction {
  id: number;
  amount: number;
  prediction: Prediction;
  fraud_probability: number | null;
  risk_score: number | null;
  risk_level: RiskLevel | null;
  model_version: string | null;
  created_at: string;
}

export interface TransactionListResponse {
  total: number;
  page: number;
  page_size: number;
  items: Transaction[];
}

export interface PredictionRequest {
  Time: number;
  V1: number;
  V2: number;
  V3: number;
  V4: number;
  V5: number;
  V6: number;
  V7: number;
  V8: number;
  V9: number;
  V10: number;
  V11: number;
  V12: number;
  V13: number;
  V14: number;
  V15: number;
  V16: number;
  V17: number;
  V18: number;
  V19: number;
  V20: number;
  V21: number;
  V22: number;
  V23: number;
  V24: number;
  V25: number;
  V26: number;
  V27: number;
  V28: number;
  Amount: number;
}

export interface PredictionResponse {
  prediction: Prediction;
  fraud_probability: number;
  risk_score: number;
  risk_level: RiskLevel;
  model_version: string;
  explanation_available: boolean;
}
