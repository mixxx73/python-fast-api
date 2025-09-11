import { jsx as _jsx, jsxs as _jsxs } from 'react/jsx-runtime';
import React from 'react';
import { useAuth } from '../auth/useAuth';
export const Profile = () => {
  const { client } = useAuth();
  const [user, setUser] = React.useState(null);
  const [error, setError] = React.useState(null);
  React.useEffect(() => {
    client
      .me()
      .then(setUser)
      .catch((e) => setError(e?.message || 'Failed to load profile'));
  }, [client]);
  if (error) return _jsx('div', { style: { color: 'red' }, children: error });
  if (!user) return _jsx('div', { children: 'Loading profile\u2026' });
  return _jsxs('section', {
    style: { marginTop: 16 },
    children: [
      _jsx('h2', { children: 'Your Profile' }),
      _jsxs('div', {
        style: { border: '1px solid #ddd', borderRadius: 8, padding: 12, maxWidth: 480 },
        children: [
          _jsxs('div', { children: [_jsx('strong', { children: 'Name:' }), ' ', user.name] }),
          _jsxs('div', { children: [_jsx('strong', { children: 'Email:' }), ' ', user.email] }),
          _jsxs('div', { children: [_jsx('strong', { children: 'User ID:' }), ' ', user.id] }),
        ],
      }),
    ],
  });
};
