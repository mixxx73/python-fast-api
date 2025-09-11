export class ExpenseClient {
  constructor({ baseUrl } = { baseUrl: '/api' }) {
    Object.defineProperty(this, 'baseUrl', {
      enumerable: true,
      configurable: true,
      writable: true,
      value: void 0,
    });
    Object.defineProperty(this, '_token', {
      enumerable: true,
      configurable: true,
      writable: true,
      value: null,
    });
    this.baseUrl = baseUrl;
  }
  setToken(t) {
    this._token = t;
  }
  async login({ email, password }) {
    return {
      access_token: `fake.${Buffer.from(email).toString('base64')}.${Buffer.from(password).toString('base64')}`,
    };
  }
  async signup({ name, email }) {
    return {
      access_token: `fake.${Buffer.from(name).toString('base64')}.${Buffer.from(email).toString('base64')}`,
    };
  }
  async me() {
    return { id: 'u_me', name: 'Test User', email: 'me@example.com' };
  }
  async listUsers() {
    return [
      { id: 'u1', name: 'Alice', email: 'alice@example.com' },
      { id: 'u2', name: 'Bob', email: 'bob@example.com' },
      { id: 'u_me', name: 'Test User', email: 'me@example.com' },
    ];
  }
  async listGroups() {
    return [
      { id: 'g1', name: 'Test Group', members: ['u1', 'u_me'] },
      { id: 'g2', name: 'Another Group', members: ['u2'] },
    ];
  }
  async createGroup(name) {
    return { id: `g_${name.toLowerCase()}`, name, members: [] };
  }
  async updateGroup(id, name) {
    return { id, name, members: ['u1'] };
  }
  async joinGroup(id, userId) {
    return { id, name: 'Joined', members: ['u1', userId] };
  }
  async listGroupExpenses(groupId) {
    return [{ id: 'e1', group_id: groupId, amount: 12.34, description: 'Snacks', payer_id: 'u1' }];
  }
  async createExpense({ group_id, amount, description, payer_id }) {
    return { id: 'e_new', group_id, amount, description, payer_id };
  }
}
