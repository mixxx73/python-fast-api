import { ExpenseClient } from '@client/index';
import React, { createContext, useContext, useRef, useState, useEffect, useCallback } from 'react';

const CLIENT_BASE = '/api';
const TOKEN_KEY = 'expense_token';

interface AuthContextValue {
  client: ExpenseClient;
  token: string | null;
  setToken: (token: string | null) => void;
  logout: () => void;
  isAuthenticated: boolean;
  initializing: boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setTokenState] = useState<string | null>(null);
  const [initializing, setInitializing] = useState(true);
  const clientRef = useRef(new ExpenseClient({ baseUrl: CLIENT_BASE }));

  const setToken = useCallback((newToken: string | null) => {
    setTokenState(newToken);

    try {
      if (newToken) {
        localStorage.setItem(TOKEN_KEY, newToken);
        clientRef.current.setToken(newToken);
      } else {
        localStorage.removeItem(TOKEN_KEY);
        clientRef.current.setToken(null);
      }
    } catch (error) {
      console.error('Failed to persist token:', error);
    }
  }, []);

  const logout = useCallback(() => {
    setToken(null);
  }, [setToken]);

  useEffect(() => {
    try {
      const storedToken = localStorage.getItem(TOKEN_KEY);
      if (storedToken) {
        clientRef.current.setToken(storedToken);
        setTokenState(storedToken);
      }
    } catch (error) {
      console.error('Failed to retrieve token:', error);
    } finally {
      setInitializing(false);
    }
  }, []);

  const value: AuthContextValue = {
    client: clientRef.current,
    token,
    setToken,
    logout,
    isAuthenticated: !!token,
    initializing,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextValue => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};