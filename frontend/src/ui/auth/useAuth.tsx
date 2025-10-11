import { ExpenseClient } from '@client/index';
import React from 'react';

const CLIENT_BASE = '/api';
const TOKEN_KEY = 'expense_token';

type AuthContext = {
  client: ExpenseClient;
  token: string | null;
  setToken: (t: string | null) => void;
  initializing: boolean;
};

const Ctx = React.createContext<AuthContext | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setTokenState] = React.useState<string | null>(null);
  const [initializing, setInitializing] = React.useState(true);
  const clientRef = React.useRef(new ExpenseClient({ baseUrl: CLIENT_BASE }));

  const setToken = (t: string | null) => {
    setTokenState(t);
    if (t) {
      localStorage.setItem(TOKEN_KEY, t);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
    clientRef.current.setToken(t);
  };

  React.useEffect(() => {
    const t = localStorage.getItem(TOKEN_KEY);
    if (t) {
      clientRef.current.setToken(t);
      setTokenState(t);
    }
    setInitializing(false);
  }, []);

  const value: AuthContext = {
    client: clientRef.current,
    token,
    setToken,
    initializing,
  };

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
};

export const useAuth = () => {
  const ctx = React.useContext(Ctx);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
