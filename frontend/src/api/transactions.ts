/**
 * Transaction API Functions
 * Uses the centralized API client for transaction management
 */

import { apiClient } from './client';
import { Transaction, TransactionListResponse } from '../types/transaction';

export const transactionAPI = {
  /**
   * Get paginated list of user transactions with optional filters
   */
  async listTransactions(params?: {
    page?: number;
    page_size?: number;
    risk_level?: string;
    prediction?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<TransactionListResponse> {
    const response = await apiClient.get<TransactionListResponse>('/transactions', {
      params,
    });
    return response.data;
  },

  /**
   * Get a single transaction by ID (with ownership check)
   */
  async getTransaction(id: number): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/transactions/${id}`);
    return response.data;
  },
};
