import { test } from 'node:test';
import assert from 'node:assert';
import React from 'react';
import { renderToString } from 'react-dom/server';

import { Login } from '../dist-tests/src/ui/auth/Login.js';
import { Signup } from '../dist-tests/src/ui/auth/Signup.js';
import { AuthProvider } from '../dist-tests/src/ui/auth/useAuth.js';

test('Login SSR renders form heading', () => {
  const html = renderToString(React.createElement(AuthProvider, null, React.createElement(Login)));
  assert.match(html, /Sign in/);
});

test('Signup SSR renders form heading', () => {
  const html = renderToString(React.createElement(AuthProvider, null, React.createElement(Signup)));
  assert.match(html, /Create account/);
});
