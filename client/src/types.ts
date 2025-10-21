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
