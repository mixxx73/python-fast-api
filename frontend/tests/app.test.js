import { test } from 'node:test';
import assert from 'node:assert';
// Use the alias resolved by our test loader stub
import { ExpenseClient } from '@client/index';

test('frontend can create client', () => {
  const client = new ExpenseClient({ baseUrl: 'http://localhost:8000' });
  assert.ok(client);
});
