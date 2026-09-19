/**
 * Authentication Context
 * Manages user state and authentication throughout the application
 */

import React, { createContext, useEffect, useState, useCallback } from 'react';
import { authAPI } from '../api/auth';
import { apiClient } from '../api/client';
import { User, AuthContextType } from '../types/auth';

export const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize authentication on app load
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check if we have a token
        const token = apiClient.getToken();
        
        if (token) {
          // Try to fetch current user
          const currentUser = await authAPI.getCurrentUser();
          setUser(currentUser);
        }
      } catch (err) {
        // Token is invalid or expired
        apiClient.clearToken();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();

    // Set up token expiration callback
    apiClient.setTokenExpiredCallback(() => {
      setUser(null);
      setError('Your session has expired. Please login again.');
    });
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authAPI.login({ email, password });
      apiClient.setToken(response.access_token);
      setUser(response.user);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const register = useCallback(async (username: string, email: string, password: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await authAPI.register({ username, email, password });
      apiClient.setToken(response.access_token);
      setUser(response.user);
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Registration failed. Please try again.';
      setError(message);
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(() => {
    authAPI.logout();
    setUser(null);
    setError(null);
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await authAPI.getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      apiClient.clearToken();
      setUser(null);
    }
  }, []);

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
