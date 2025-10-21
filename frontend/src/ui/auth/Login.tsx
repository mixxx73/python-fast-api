import React, { useState, useCallback, FormEvent, ChangeEvent } from 'react';

import { handleApiError } from '../../utils/errorHandler';
import {
  validateEmail,
  validatePassword,
  ValidationErrors,
} from '../../utils/validation';
import { useAuth } from './useAuth';

interface LoginProps {
  onSwitchToSignup?: () => void;
}

export const Login: React.FC<LoginProps> = ({ onSwitchToSignup }) => {
  const { client, setToken } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<ValidationErrors>({});

  const validate = useCallback((): boolean => {
    const errors: ValidationErrors = {};

    errors.email = validateEmail(email);
    errors.password = validatePassword(password, { minLength: 1, requireUppercase: false, requireLowercase: false, requireNumber: false });

    setFieldErrors(errors);
    return Object.values(errors).every((e) => !e);
  }, [email, password]);

  const handleEmailChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
    if (fieldErrors.email) {
      setFieldErrors((prev) => ({ ...prev, email: undefined }));
    }
  };

  const handlePasswordChange = (e: ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    if (fieldErrors.password) {
      setFieldErrors((prev) => ({ ...prev, password: undefined }));
    }
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    if (!validate()) {
      return;
    }

    setLoading(true);
    setError(null);
    setFieldErrors({});

    try {
      const response = await client.login({ email, password });
      setToken(response.access_token);
    } catch (err: any) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20, maxWidth: 400, margin: '0 auto' }}>
      <h1 style={{ marginBottom: 24 }}>Sign in</h1>

      <form onSubmit={handleSubmit} noValidate>
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="login-email" style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
            Email <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="login-email"
            type="email"
            value={email}
            onChange={handleEmailChange}
            required
            autoComplete="email"
            aria-invalid={!!fieldErrors.email}
            aria-describedby={fieldErrors.email ? 'email-error' : undefined}
            style={{
              display: 'block',
              width: '100%',
              padding: 8,
              border: fieldErrors.email ? '1px solid #dc2626' : '1px solid #d1d5db',
              borderRadius: 4,
              fontSize: 14,
            }}
          />
          {fieldErrors.email && (
            <div id="email-error" role="alert" style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>
              {fieldErrors.email}
            </div>
          )}
        </div>

        <div style={{ marginBottom: 16 }}>
          <label htmlFor="login-password" style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
            Password <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="login-password"
            type="password"
            value={password}
            onChange={handlePasswordChange}
            required
            autoComplete="current-password"
            aria-invalid={!!fieldErrors.password}
            aria-describedby={fieldErrors.password ? 'password-error' : undefined}
            style={{
              display: 'block',
              width: '100%',
              padding: 8,
              border: fieldErrors.password ? '1px solid #dc2626' : '1px solid #d1d5db',
              borderRadius: 4,
              fontSize: 14,
            }}
          />
          {fieldErrors.password && (
            <div id="password-error" role="alert" style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>
              {fieldErrors.password}
            </div>
          )}
        </div>

        {error && (
          <div
            role="alert"
            style={{
              color: '#dc2626',
              backgroundColor: '#fee2e2',
              padding: 12,
              borderRadius: 4,
              marginBottom: 16,
            }}
          >
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          style={{
            width: '100%',
            padding: 10,
            backgroundColor: loading ? '#9ca3af' : '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: 4,
            fontSize: 16,
            fontWeight: 500,
            cursor: loading ? 'not-allowed' : 'pointer',
          }}
        >
          {loading ? 'Signing in…' : 'Sign in'}
        </button>
      </form>

      <p style={{ marginTop: 16, textAlign: 'center', color: '#6b7280' }}>
        Don't have an account?{' '}
        <button
          type="button"
          onClick={onSwitchToSignup}
          style={{
            background: 'none',
            border: 'none',
            color: '#2563eb',
            cursor: 'pointer',
            padding: 0,
            textDecoration: 'underline',
            fontSize: 'inherit',
          }}
        >
          Sign up
        </button>
      </p>
    </div>
  );
};