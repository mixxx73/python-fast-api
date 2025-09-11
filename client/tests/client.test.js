import { test } from 'node:test';
import assert from 'node:assert';
import { ExpenseClient } from '../dist/index.js';

test('constructs client', () => {
  const client = new ExpenseClient({ baseUrl: 'http://localhost:8000' });
  assert.ok(client);
});
