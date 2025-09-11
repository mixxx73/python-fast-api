import { ExpenseClient } from '@client/index';

const client = new ExpenseClient({ baseUrl: 'http://localhost:8000' });
console.log('Frontend initialized', client);
