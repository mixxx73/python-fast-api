import { jsx as _jsx } from 'react/jsx-runtime';
import React from 'react';
import { useAuth } from './auth/useAuth';
import { Login } from './auth/Login';
import { Signup } from './auth/Signup';
import { Home } from './home/Home';
export const App = () => {
  const { token, initializing } = useAuth();
  const [authView, setAuthView] = React.useState('login');
  if (initializing) {
    return _jsx('div', { style: { padding: 20 }, children: 'Loading\u2026' });
  }
  if (token) return _jsx(Home, {});
  return authView === 'login'
    ? _jsx(Login, { onSwitchToSignup: () => setAuthView('signup') })
    : _jsx(Signup, { onSwitchToLogin: () => setAuthView('login') });
};
