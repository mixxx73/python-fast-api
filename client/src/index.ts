export interface ClientOptions {
  baseUrl: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface SignupRequest extends LoginRequest {
  name: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  is_admin: boolean;
}

export interface GroupRead {
  id: string;
  name: string;
  members: string[];
}

export interface GroupCreate {
  name: string;
}

export interface ExpenseRead {
  id: string;
  group_id: string;
  payer_id: string;
  amount: number;
  created_at: string;
  description?: string | null;
}

export interface BalanceEntry {
  user_id: string;
  balance: number;
}

export interface ExpenseCreate {
  group_id: string;
  payer_id: string;
  amount: number;
  description?: string | null;
}

export class ExpenseClient {
  private token: string | null = null;

  constructor(private options: ClientOptions) {}

  setToken(token: string | null) {
    this.token = token;
  }

  private headers(json = false): HeadersInit {
    const h: Record<string, string> = {};
    if (json) h["Content-Type"] = "application/json";
    if (this.token) h["Authorization"] = `Bearer ${this.token}`;
    return h;
  }

  async ping(): Promise<string> {
    const res = await fetch(`${this.options.baseUrl}/`, { headers: this.headers() });
    const data = await res.json();
    return data.status as string;
  }

  async login(payload: LoginRequest): Promise<Token> {
    const res = await fetch(`${this.options.baseUrl}/auth/login`, {
      method: "POST",
      headers: this.headers(true),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      let message = `Login failed (${res.status})`;
      try {
        const data = await res.json();
        if (typeof data?.detail === 'string') message = data.detail;
      } catch {}
      if (res.status === 401) message = 'Invalid email or password';
      const err = new Error(message) as Error & { status?: number };
      (err as any).status = res.status;
      throw err;
    }
    const token = (await res.json()) as Token;
    this.setToken(token.access_token);
    return token;
  }

  async signup(payload: SignupRequest): Promise<Token> {
    const res = await fetch(`${this.options.baseUrl}/auth/signup`, {
      method: "POST",
      headers: this.headers(true),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      let message = `Signup failed (${res.status})`;
      try {
        const data = await res.json();
        if (typeof data?.detail === 'string') message = data.detail;
      } catch {}
      if (res.status === 409) message = 'Email already exists';
      const err = new Error(message) as Error & { status?: number };
      (err as any).status = res.status;
      throw err;
    }
    const token = (await res.json()) as Token;
    this.setToken(token.access_token);
    return token;
  }

  async me(): Promise<User> {
      // console.log('zzzzzzzzzzzzzzzzz');
    const res = await fetch(`${this.options.baseUrl}/auth/me`, {
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(`Unauthorized (${res.status})`);
    }
    // const u =await res.json();
    // console.log('zzxxxxxx',u);
    // return u as User;
    return (await res.json()) as User;
  }

  async updateUserName(id: string, name: string): Promise<User> {
    const res = await fetch(`${this.options.baseUrl}/users/${id}`, {
      method: "PATCH",
      headers: this.headers(true),
      body: JSON.stringify({ name }),
    });
    if (!res.ok) {
      let message = `Failed to update profile (${res.status})`;
      try {
        const data = await res.json();
        if (typeof data?.detail === 'string') message = data.detail;
      } catch {}
      throw new Error(message);
    }
    return (await res.json()) as User;
  }

  async listUsers(): Promise<User[]> {
    const res = await fetch(`${this.options.baseUrl}/users/`, {
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(`Failed to load users (${res.status})`);
    }
    return (await res.json()) as User[];
  }

  async listGroups(): Promise<GroupRead[]> {
    const res = await fetch(`${this.options.baseUrl}/groups/`, {
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(`Failed to load groups (${res.status})`);
    }
    return (await res.json()) as GroupRead[];
  }

  async listUserGroups(userId: string): Promise<GroupRead[]> {
    const res = await fetch(`${this.options.baseUrl}/users/${userId}/groups`, {
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(`Failed to load user's groups (${res.status})`);
    }
    return (await res.json()) as GroupRead[];
  }

  async createGroup(name: string): Promise<GroupRead> {
    const payload: GroupCreate = { name };
    const res = await fetch(`${this.options.baseUrl}/groups/`, {
      method: "POST",
      headers: this.headers(true),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error(`Failed to create group (${res.status})`);
    }
    return (await res.json()) as GroupRead;
  }

  async updateGroup(id: string, name: string): Promise<GroupRead> {
    const res = await fetch(`${this.options.baseUrl}/groups/${id}`, {
      method: "PATCH",
      headers: this.headers(true),
      body: JSON.stringify({ name }),
    });
    if (!res.ok) {
      throw new Error(`Failed to update group (${res.status})`);
    }
    return (await res.json()) as GroupRead;
  }

  async joinGroup(groupId: string, userId?: string): Promise<GroupRead> {
    let uid = userId;
    if (!uid) {
      const me = await this.me();
      uid = me.id;
    }
    const res = await fetch(`${this.options.baseUrl}/groups/${groupId}/members/${uid}`, {
      method: "POST",
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(`Failed to join group (${res.status})`);
    }
    return (await res.json()) as GroupRead;
  }

  async listGroupExpenses(groupId: string): Promise<ExpenseRead[]> {
    const res = await fetch(`${this.options.baseUrl}/groups/${groupId}/expenses`, {
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(`Failed to load expenses (${res.status})`);
    }
    return (await res.json()) as ExpenseRead[];
  }

  async createExpense(input: Omit<ExpenseCreate, 'payer_id'> & { payer_id?: string }): Promise<ExpenseRead> {
    let payload: ExpenseCreate = {
      group_id: input.group_id,
      payer_id: input.payer_id || '',
      amount: input.amount,
      description: input.description ?? null,
    };
    if (!payload.payer_id) {
      const me = await this.me();
      payload.payer_id = me.id;
    }
    const res = await fetch(`${this.options.baseUrl}/expenses/`, {
      method: "POST",
      headers: this.headers(true),
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      throw new Error(`Failed to create expense (${res.status})`);
    }
    return (await res.json()) as ExpenseRead;
  }

  async listGroupBalances(groupId: string): Promise<BalanceEntry[]> {
    const res = await fetch(`${this.options.baseUrl}/groups/${groupId}/balances`, {
      headers: this.headers(),
    });
    if (!res.ok) {
      throw new Error(`Failed to load balances (${res.status})`);
    }
    return (await res.json()) as BalanceEntry[];
  }
}
