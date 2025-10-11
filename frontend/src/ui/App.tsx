import React from 'react';

import { Login } from './auth/Login';
import { Signup } from './auth/Signup';
import { useAuth } from './auth/useAuth';
import { Home } from './home/Home';

export const App: React.FC = () => {
  const { token, initializing } = useAuth();
  const [authView, setAuthView] = React.useState<'login' | 'signup'>('login');

  if (initializing) {
    return <div style={{ padding: 20 }}>Loading…</div>;
  }

  if (token) {
    return <Home />;
  }

  return authView === 'login' ? (
    <Login onSwitchToSignup={() => setAuthView('signup')} />
  ) : (
    <Signup onSwitchToLogin={() => setAuthView('login')} />
  );
};
