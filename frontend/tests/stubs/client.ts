export type User = { id: string; name: string; email: string; is_admin?: boolean; };
export type GroupRead = { id: string; name: string; members: string[] };
export type ExpenseRead = {
  id: string;
  group_id: string;
  amount: number;
  description: string | null;
  payer_id: string;
  created_at: string;
};
export type BalanceEntry = { user_id: string; balance: number };

export class ExpenseClient {
  private baseUrl: string;
  private _token: string | null = null;
  constructor({ baseUrl }: { baseUrl: string } = { baseUrl: '/api' }) {
    this.baseUrl = baseUrl;
  }
  setToken(t: string | null) {
    this._token = t;
  }
  async login({
    email,
    password,
  }: {
    email: string;
    password: string;
  }): Promise<{ access_token: string }> {
    return {
      access_token: `fake.${Buffer.from(email).toString('base64')}.${Buffer.from(password).toString('base64')}`,
    };
  }
  async signup({
    name,
    email,
  }: {
    name: string;
    email: string;
    password: string;
  }): Promise<{ access_token: string }> {
    return {
      access_token: `fake.${Buffer.from(name).toString('base64')}.${Buffer.from(email).toString('base64')}`,
    };
  }
  async me(): Promise<User> {
    return { id: 'u_me', name: 'Test User', email: 'me@example.com', is_admin: false };
  }
  async listUsers(): Promise<User[]> {
    return [
      { id: 'u1', name: 'Alice', email: 'alice@example.com', is_admin: false },
      { id: 'u2', name: 'Bob', email: 'bob@example.com', is_admin: false },
      { id: 'u_me', name: 'Test User', email: 'me@example.com', is_admin: false },
    ];
  }
  async updateUserName(id: string, name: string): Promise<User> {
    return { id, name, email: 'me@example.com', is_admin: false };
  }
  async listGroups(): Promise<GroupRead[]> {
    return [
      { id: 'g1', name: 'Test Group', members: ['u1', 'u_me'] },
      { id: 'g2', name: 'Another Group', members: ['u2'] },
    ];
  }
  async listUserGroups(userId: string): Promise<GroupRead[]> {
    const all = await this.listGroups();
    return all.filter((g) => g.members.includes(userId));
  }
  async createGroup(name: string): Promise<GroupRead> {
    return { id: `g_${name.toLowerCase()}`, name, members: [] };
  }
  async updateGroup(id: string, name: string): Promise<GroupRead> {
    return { id, name, members: ['u1'] };
  }
  async joinGroup(id: string, userId: string): Promise<GroupRead> {
    return { id, name: 'Joined', members: ['u1', userId] };
  }
  async listGroupExpenses(groupId: string): Promise<ExpenseRead[]> {
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
  async createExpense({
    group_id,
    amount,
    description,
    payer_id,
  }: {
    group_id: string;
    amount: number;
    description: string | null;
    payer_id: string;
  }): Promise<ExpenseRead> {
    return {
      id: 'e_new',
      group_id,
      amount,
      description,
      payer_id,
      created_at: new Date().toISOString(),
    };
  }
  async listGroupBalances(groupId: string): Promise<BalanceEntry[]> {
    const groups = await this.listGroups();
    const g = groups.find((x) => x.id === groupId);
    if (!g || g.members.length === 0) return [];
    // Derive simple balances from stubbed expenses: single expense 12.34 by u1
    const expenses = await this.listGroupExpenses(groupId);
    const balances: Record<string, number> = Object.fromEntries(g.members.map((m) => [m, 0]));
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
