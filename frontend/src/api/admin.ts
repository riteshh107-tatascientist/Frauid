/**
 * Admin API Functions
 * Alert management and monitoring endpoints
 */

import { apiClient } from './client';

export interface Alert {
  id: number;
  transaction_id: number;
  fraud_probability?: number;
  risk_level?: string;
  status: 'OPEN' | 'REVIEWED' | 'RESOLVED';
  created_at: string;
  updated_at?: string;
}

export interface AlertListResponse {
  total?: number;
  alerts: Alert[];
}

export interface AlertUpdateRequest {
  new_status: 'OPEN' | 'REVIEWED' | 'RESOLVED';
}

export const adminAPI = {
  /**
   * Get list of fraud alerts with optional filtering
   */
  async listAlerts(params?: {
    status_filter?: string;
    skip?: number;
    limit?: number;
  }): Promise<AlertListResponse> {
    const response = await apiClient.get<AlertListResponse>('/admin/alerts', {
      params,
    });
    return response.data;
  },

  /**
   * Get a specific alert by ID (admin only)
   */
  async getAlert(id: number): Promise<Alert> {
    const response = await apiClient.get<Alert>(`/admin/alerts/${id}`);
    return response.data;
  },

  /**
   * Update alert status (admin only)
   */
  async updateAlertStatus(id: number, newStatus: 'OPEN' | 'REVIEWED' | 'RESOLVED'): Promise<Alert> {
    const response = await apiClient.patch<Alert>(`/admin/alerts/${id}/status`, {
      new_status: newStatus,
    });
    return response.data;
  },

  /**
   * Get admin monitoring summary
   */
  async getMonitoringSummary(): Promise<{
    open_alerts?: number;
    high_risk_alerts?: number;
    reviewed_alerts?: number;
    resolved_alerts?: number;
    recent_frauds?: number;
  }> {
    try {
      const response = await apiClient.get('/admin/monitoring/summary');
      return response.data;
    } catch (error) {
      // If endpoint doesn't exist, return empty object
      return {};
    }
  },
};
