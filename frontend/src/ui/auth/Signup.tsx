import React, { useState, useCallback, FormEvent, ChangeEvent } from 'react';

import { handleApiError } from '../../utils/errorHandler';
import {
  validateEmail,
  validateName,
  validatePassword,
  ValidationErrors,
} from '../../utils/validation';
import { useAuth } from './useAuth';

interface SignupProps {
  onSwitchToLogin?: () => void;
}

export const Signup: React.FC<SignupProps> = ({ onSwitchToLogin }) => {
  const { client, setToken } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<ValidationErrors>({});

  const validate = useCallback((): boolean => {
    const errors: ValidationErrors = {};

    errors.name = validateName(name);
    errors.email = validateEmail(email);
    errors.password = validatePassword(password);

    setFieldErrors(errors);
    return Object.values(errors).every((e) => !e);
  }, [name, email, password]);

  const handleNameChange = (e: ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value);
    if (fieldErrors.name) {
      setFieldErrors((prev) => ({ ...prev, name: undefined }));
    }
  };

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
      const response = await client.signup({ name, email, password });
      setToken(response.access_token);
    } catch (err: any) {
      setError(handleApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 20, maxWidth: 400, margin: '0 auto' }}>
      <h1 style={{ marginBottom: 24 }}>Create account</h1>

      <form onSubmit={handleSubmit} noValidate>
        <div style={{ marginBottom: 16 }}>
          <label htmlFor="signup-name" style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
            Name <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="signup-name"
            type="text"
            value={name}
            onChange={handleNameChange}
            required
            autoComplete="name"
            aria-invalid={!!fieldErrors.name}
            aria-describedby={fieldErrors.name ? 'name-error' : undefined}
            style={{
              display: 'block',
              width: '100%',
              padding: 8,
              border: fieldErrors.name ? '1px solid #dc2626' : '1px solid #d1d5db',
              borderRadius: 4,
              fontSize: 14,
            }}
          />
          {fieldErrors.name && (
            <div id="name-error" role="alert" style={{ color: '#dc2626', fontSize: 12, marginTop: 4 }}>
              {fieldErrors.name}
            </div>
          )}
        </div>

        <div style={{ marginBottom: 16 }}>
          <label htmlFor="signup-email" style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
            Email <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="signup-email"
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
          <label htmlFor="signup-password" style={{ display: 'block', marginBottom: 4, fontWeight: 500 }}>
            Password <span style={{ color: 'red' }}>*</span>
          </label>
          <input
            id="signup-password"
            type="password"
            value={password}
            onChange={handlePasswordChange}
            required
            autoComplete="new-password"
            aria-invalid={!!fieldErrors.password}
            aria-describedby={fieldErrors.password ? 'password-error password-requirements' : 'password-requirements'}
            style={{
              display: 'block',
              width: '100%',
              padding: 8,
              border: fieldErrors.password ? '1px solid #dc2626' : '1px solid #d1d5db',
              borderRadius: 4,
              fontSize: 14,
            }}
          />
          <div id="password-requirements" style={{ fontSize: 12, color: '#6b7280', marginTop: 4 }}>
            Must be 8+ characters with uppercase, lowercase, and numbers
          </div>
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
          {loading ? 'Creating account…' : 'Sign up'}
        </button>
      </form>

      <p style={{ marginTop: 16, textAlign: 'center', color: '#6b7280' }}>
        Already have an account?{' '}
        <button
          type="button"
          onClick={onSwitchToLogin}
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
          Sign in
        </button>
      </p>
    </div>
  );
};