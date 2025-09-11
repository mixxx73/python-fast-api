import { jsx as _jsx, jsxs as _jsxs } from 'react/jsx-runtime';
import React from 'react';
import { useAuth } from './useAuth';
export const Signup = ({ onSwitchToLogin }) => {
  const { client, setToken } = useAuth();
  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [error, setError] = React.useState(null);
  const [loading, setLoading] = React.useState(false);
  const [fieldErrors, setFieldErrors] = React.useState({});
  const validate = () => {
    const errs = {};
    if (!name.trim()) errs.name = 'Name is required';
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) errs.email = 'Enter a valid email';
    if (password.length < 8) errs.password = 'Password must be at least 8 characters';
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };
  const onSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setLoading(true);
    setError(null);
    try {
      const token = await client.signup({ name, email, password });
      setToken(token.access_token);
    } catch (err) {
      setError(err?.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };
  return _jsxs('div', {
    style: { padding: 20, maxWidth: 400 },
    children: [
      _jsx('h1', { children: 'Create account' }),
      _jsxs('form', {
        onSubmit: onSubmit,
        noValidate: true,
        children: [
          _jsxs('div', {
            style: { marginBottom: 8 },
            children: [
              _jsxs('label', {
                children: [
                  'Name',
                  _jsx('input', {
                    type: 'text',
                    value: name,
                    onChange: (e) => setName(e.target.value),
                    required: true,
                    style: { display: 'block', width: '100%', padding: 8 },
                  }),
                ],
              }),
              fieldErrors.name &&
                _jsx('div', { style: { color: 'red', fontSize: 12 }, children: fieldErrors.name }),
            ],
          }),
          _jsxs('div', {
            style: { marginBottom: 8 },
            children: [
              _jsxs('label', {
                children: [
                  'Email',
                  _jsx('input', {
                    type: 'email',
                    value: email,
                    onChange: (e) => setEmail(e.target.value),
                    required: true,
                    style: { display: 'block', width: '100%', padding: 8 },
                  }),
                ],
              }),
              fieldErrors.email &&
                _jsx('div', { style: { color: 'red', fontSize: 12 }, children: fieldErrors.email }),
            ],
          }),
          _jsxs('div', {
            style: { marginBottom: 8 },
            children: [
              _jsxs('label', {
                children: [
                  'Password',
                  _jsx('input', {
                    type: 'password',
                    value: password,
                    onChange: (e) => setPassword(e.target.value),
                    required: true,
                    style: { display: 'block', width: '100%', padding: 8 },
                  }),
                ],
              }),
              fieldErrors.password &&
                _jsx('div', {
                  style: { color: 'red', fontSize: 12 },
                  children: fieldErrors.password,
                }),
            ],
          }),
          error && _jsx('div', { style: { color: 'red', marginBottom: 8 }, children: error }),
          _jsx('button', {
            type: 'submit',
            disabled: loading,
            children: loading ? 'Creating…' : 'Sign up',
          }),
        ],
      }),
      _jsxs('p', {
        style: { color: '#666' },
        children: [
          'Already have an account?',
          ' ',
          _jsx('button', {
            type: 'button',
            onClick: onSwitchToLogin,
            style: {
              background: 'none',
              border: 'none',
              color: '#2563eb',
              cursor: 'pointer',
              padding: 0,
            },
            children: 'Sign in',
          }),
        ],
      }),
    ],
  });
};
