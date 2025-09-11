import { test } from 'node:test';
import assert from 'node:assert';
import React from 'react';
import { renderToString } from 'react-dom/server';

// Import compiled components built by `build:test`
import { App } from '../dist-tests/src/ui/App.js';
import { AuthProvider } from '../dist-tests/src/ui/auth/useAuth.js';

// Basic SSR smoke: App under AuthProvider shows Loading… initially
test('App SSR renders loading state', () => {
  const html = renderToString(React.createElement(AuthProvider, null, React.createElement(App)));
  assert.match(html, /Loading…/);
});
