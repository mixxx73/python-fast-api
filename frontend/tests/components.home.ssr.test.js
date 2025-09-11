import { test } from 'node:test';
import assert from 'node:assert';
import React from 'react';
import { renderToString } from 'react-dom/server';

import { Home } from '../dist-tests/src/ui/home/Home.js';
import { Profile } from '../dist-tests/src/ui/home/Profile.js';
import { GroupsList } from '../dist-tests/src/ui/groups/GroupsList.js';
import { Expenses } from '../dist-tests/src/ui/expenses/Expenses.js';
import { AuthProvider } from '../dist-tests/src/ui/auth/useAuth.js';

test('Home SSR renders header', () => {
  const html = renderToString(React.createElement(AuthProvider, null, React.createElement(Home)));
  assert.match(html, /Expense App/);
});

test('Profile SSR shows loading initially', () => {
  const html = renderToString(
    React.createElement(AuthProvider, null, React.createElement(Profile)),
  );
  assert.match(html, /Loading profile…/);
});

test('GroupsList SSR shows loading initially', () => {
  const html = renderToString(
    React.createElement(AuthProvider, null, React.createElement(GroupsList)),
  );
  assert.match(html, /Loading groups…/);
});

test('Expenses SSR renders base UI (group select + loading)', () => {
  const html = renderToString(
    React.createElement(AuthProvider, null, React.createElement(Expenses)),
  );
  // Should contain the Group label and a loading state for expenses
  assert.match(html, /Group/);
  // Initial selectedGroup is set in an effect, so first render has loading marker for expenses section
  assert.match(html, /Loading expenses…|No expenses yet\./);
});
