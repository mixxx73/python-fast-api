// Test stub for the API client consumed by the UI.
// Provides the methods referenced by the components, returning simple data.

export class ExpenseClient {
  constructor({ baseUrl } = { baseUrl: '/api' }) {
    this.baseUrl = baseUrl;
    this._token = null;
  }
  setToken(t) {
    this._token = t;
  }

  // Auth
  async login({ email, password }) {
    return { access_token: `fake.${btoa(email)}.${btoa(password)}` };
  }
  async signup({ name, email, password }) {
    return { access_token: `fake.${btoa(name)}.${btoa(email)}` };
  }
  async me() {
    return { id: 'u_me', name: 'Test User', email: 'me@example.com' };
  }

  // Users
  async listUsers() {
    return [
      { id: 'u1', name: 'Alice', email: 'alice@example.com' },
      { id: 'u2', name: 'Bob', email: 'bob@example.com' },
      { id: 'u_me', name: 'Test User', email: 'me@example.com' },
    ];
  }
  async updateUserName(id, name) {
    return { id, name, email: 'me@example.com' };
  }

  // Groups
  async listGroups() {
    return [
      { id: 'g1', name: 'Test Group', members: ['u1', 'u_me'] },
      { id: 'g2', name: 'Another Group', members: ['u2'] },
    ];
  }
  async listUserGroups(userId) {
    const all = await this.listGroups();
    return all.filter((g) => g.members.includes(userId));
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

  // Expenses
  async listGroupExpenses(groupId) {
    return [
      {
        id: 'e1',
        group_id: groupId,
        amount: 12.34,
        description: 'Snacks',
        payer_id: 'u1',
        created_at: new Date().toISOString(),
      },
    ];
  }
  async createExpense({ group_id, amount, description, payer_id }) {
    return {
      id: 'e_new',
      group_id,
      amount,
      description,
      payer_id,
      created_at: new Date().toISOString(),
    };
  }
  async listGroupBalances(groupId) {
    const groups = await this.listGroups();
    const g = groups.find((x) => x.id === groupId);
    if (!g || g.members.length === 0) return [];
    const expenses = await this.listGroupExpenses(groupId);
    const balances = Object.fromEntries(g.members.map((m) => [m, 0]));
    for (const e of expenses) {
      const share = e.amount / g.members.length;
      for (const m of g.members) balances[m] -= share;
      if (balances[e.payer_id] !== undefined) balances[e.payer_id] += e.amount;
    }
    return g.members.map((m) => ({
      user_id: m,
      balance: Math.round((balances[m] || 0) * 100) / 100,
    }));
  }
}
