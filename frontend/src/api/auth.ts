/**
 * Authentication API Functions
 * Uses the centralized API client
 */

import { apiClient } from './client';
import { User, TokenResponse, LoginRequest, RegisterRequest } from '../types/auth';

export const authAPI = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/register', data);
    return response.data;
  },

  /**
   * Login user with credentials
   */
  async login(data: LoginRequest): Promise<TokenResponse> {
    const response = await apiClient.post<TokenResponse>('/auth/login', data);
    return response.data;
  },

  /**
   * Get current authenticated user
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Logout user (frontend only, token is cleared)
   */
  logout(): void {
    apiClient.clearToken();
  },
};
