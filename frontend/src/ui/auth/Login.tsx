import React from 'react';

import { useAuth } from './useAuth';

export const Login: React.FC<{ onSwitchToSignup?: () => void }> = ({ onSwitchToSignup }) => {
  const { client, setToken } = useAuth();
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [fieldErrors, setFieldErrors] = React.useState<{ email?: string; password?: string }>({});

  const validate = () => {
    const errs: { email?: string; password?: string } = {};
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      errs.email = 'Enter a valid email';
    }
    if (password.length === 0) {
      errs.password = 'Password is required';
    }
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const token = await client.login({ email, password });
      setToken(token.access_token);
    } catch (err: any) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20, maxWidth: 400 }}>
      <h1>Sign in</h1>
      <form onSubmit={onSubmit} noValidate>
        <div style={{ marginBottom: 8 }}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              style={{ display: 'block', width: '100%', padding: 8 }}
            />
          </label>
          {fieldErrors.email && (
            <div style={{ color: 'red', fontSize: 12 }}>{fieldErrors.email}</div>
          )}
        </div>
        <div style={{ marginBottom: 8 }}>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{ display: 'block', width: '100%', padding: 8 }}
            />
          </label>
          {fieldErrors.password && (
            <div style={{ color: 'red', fontSize: 12 }}>{fieldErrors.password}</div>
          )}
        </div>
        {error && <div style={{ color: 'red', marginBottom: 8 }}>{error}</div>}
        <button type="submit" disabled={loading}>
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
      <p style={{ color: '#666' }}>
        Don’t have an account?{' '}
        <button
          type="button"
          onClick={onSwitchToSignup}
          style={{
            background: 'none',
            border: 'none',
            color: '#2563eb',
            cursor: 'pointer',
            padding: 0,
          }}
        >
          Sign up
        </button>
      </p>
    </div>
  );
};
