/**
 * Centralized API Client for FraudGuard AI
 * 
 * Handles:
 * - Base URL configuration
 * - Authorization header injection
 * - Common error handling
 * - Token management
 * - 401 response handling
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;
  private tokenKey = 'access_token';
  private onTokenExpired: (() => void) | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Inject token into every request
    this.client.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle responses
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // Handle 401 Unauthorized
        if (error.response?.status === 401) {
          this.clearToken();
          if (this.onTokenExpired) {
            this.onTokenExpired();
          }
        }
        return Promise.reject(error);
      }
    );
  }

  public setTokenExpiredCallback(callback: () => void) {
    this.onTokenExpired = callback;
  }

  public getToken(): string | null {
    // Use sessionStorage for this prototype (no HttpOnly cookies)
    // In production, use more secure methods like HttpOnly cookies
    return sessionStorage.getItem(this.tokenKey);
  }

  public setToken(token: string) {
    sessionStorage.setItem(this.tokenKey, token);
  }

  public clearToken() {
    sessionStorage.removeItem(this.tokenKey);
  }

  public isAuthenticated(): boolean {
    return !!this.getToken();
  }

  // Public methods for API calls
  public get<T>(url: string, config?: any) {
    return this.client.get<T>(url, config);
  }

  public post<T>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config);
  }

  public patch<T>(url: string, data?: any, config?: any) {
    return this.client.patch<T>(url, data, config);
  }

  public put<T>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config);
  }

  public delete<T>(url: string, config?: any) {
    return this.client.delete<T>(url, config);
  }
}

export const apiClient = new APIClient();
