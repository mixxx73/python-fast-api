import type { GroupRead, ExpenseRead, User, BalanceEntry } from '@client/index';
import { formatDistanceToNow } from 'date-fns';
import React from 'react';

import { useAuth } from '../auth/useAuth';

import { Balances } from './Balances';

export const Expenses: React.FC = () => {
  const { client } = useAuth();
  const [groups, setGroups] = React.useState<GroupRead[] | null>(null);
  const [myGroups, setMyGroups] = React.useState<GroupRead[] | null>(null);
  const [selectedGroup, setSelectedGroup] = React.useState<string | null>(null);
  const [expenses, setExpenses] = React.useState<ExpenseRead[] | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [balances, setBalances] = React.useState<BalanceEntry[] | null>(null);
  const [balancesError, setBalancesError] = React.useState<string | null>(null);
  const [users, setUsers] = React.useState<User[] | null>(null);
  const [me, setMe] = React.useState<User | null>(null);

  const [amount, setAmount] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [creating, setCreating] = React.useState(false);
  const [payerId, setPayerId] = React.useState<string>('');

  React.useEffect(() => {
    let mounted = true;
    Promise.all([client.listGroups(), client.me(), client.listUsers()])
      .then(([gs, meUser, us]) => {
        if (!mounted) {
          return;
        }
        setGroups(gs);
        const mine = gs.filter((g) => g.members.includes(meUser.id));
        setMyGroups(mine);
        if (mine.length > 0) {
          setSelectedGroup((prev) => prev ?? mine[0].id);
        }
        setUsers(us);
        setMe(meUser);
        setPayerId(meUser.id);
      })
      .catch((e) => setError(e?.message || 'Failed to load groups'));
    return () => {
      mounted = false;
    };
  }, [client]);

  React.useEffect(() => {
    let mounted = true;
    if (!selectedGroup) {
      setExpenses(null);
      setBalances(null);
      return;
    }
    setExpenses(null);
    setBalances(null);
    client
      .listGroupExpenses(selectedGroup)
      .then((es) => {
        if (mounted) {
          setExpenses(es);
        }
      })
      .catch((e) => setError(e?.message || 'Failed to load expenses'));
    client
      .listGroupBalances(selectedGroup)
      .then((bs) => {
        if (mounted) {
          setBalances(bs);
        }
      })
      .catch((e) => setBalancesError(e?.message || 'Failed to load balances'));
    return () => {
      mounted = false;
    };
  }, [client, selectedGroup]);

  // Ensure payer stays valid for the selected group
  React.useEffect(() => {
    if (!selectedGroup || !groups || !users) {
      return;
    }
    const g = groups.find((x) => x.id === selectedGroup);
    if (!g) {
      return;
    }
    const memberIds = new Set(g.members);
    if (!memberIds.has(payerId)) {
      if (me && memberIds.has(me.id)) {
        setPayerId(me.id);
      } else if (g.members.length > 0) {
        setPayerId(g.members[0]);
      } else {
        setPayerId('');
      }
    }
  }, [selectedGroup, groups, users, me, payerId]);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedGroup) {
      return;
    }
    const amt = parseFloat(amount);
    if (Number.isNaN(amt) || amt <= 0) {
      setError('Enter a valid amount > 0');
      return;
    }
    try {
      setCreating(true);
      setError(null);
      const created = await client.createExpense({
        group_id: selectedGroup,
        amount: amt,
        description: description || null,
        payer_id: payerId,
      });
      setExpenses((prev) => (prev ? [created, ...prev] : [created]));
      // Refresh balances after creating an expense
      try {
        const bs = await client.listGroupBalances(selectedGroup);
        setBalances(bs);
        setBalancesError(null);
      } catch (e: any) {
        setBalancesError(e?.message || 'Failed to refresh balances');
      }
      setAmount('');
      setDescription('');
    } catch (e: any) {
      setError(e?.message || 'Failed to create expense');
    } finally {
      setCreating(false);
    }
  };

  const groupOptions = (myGroups ?? []).map((g) => (
    <option key={g.id} value={g.id}>
      {g.name || 'Untitled'}
    </option>
  ));

  const selectedGroupObj = (groups ?? []).find((g) => g.id === selectedGroup) || null;
  const memberUsers: User[] =
    selectedGroupObj && users ? users.filter((u) => selectedGroupObj.members.includes(u.id)) : [];
  const payerOptions = memberUsers.map((u) => (
    <option key={u.id} value={u.id}>
      {u.name} ({u.email})
    </option>
  ));
  const userById = React.useMemo(() => {
    const m = new Map<string, User>();
    (users ?? []).forEach((u) => m.set(u.id, u));
    return m;
  }, [users]);

  const timeAgo = (iso: string) => formatDistanceToNow(new Date(iso), { addSuffix: true });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div>is:{ me?.is_admin }</div>
        <div>me:{ me?.name }</div>
        <div>ee:{ me?.email }</div>
        <label style={{ fontWeight: 600 }}>Group</label>
        <select
          value={selectedGroup || ''}
          onChange={(e) => setSelectedGroup(e.target.value || null)}
          style={{ padding: 6 }}
        >
          {groupOptions}
        </select>
      </div>
      {me?.is_admin && (
        <form
          onSubmit={onCreate}
          style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}
        >
          <input
            type="number"
            step="0.01"
            min="0"
            placeholder="Amount"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            style={{ width: 140, padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 }}
          />
          <select
            value={payerId}
            onChange={(e) => setPayerId(e.target.value)}
            style={{ minWidth: 220, padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 }}
            aria-label="Payer"
          >
            {payerOptions}
          </select>
          <input
            type="text"
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{
              flex: 1,
              minWidth: 240,
              padding: 8,
              border: '1px solid #e5e7eb',
              borderRadius: 6,
            }}
          />
          <button type="submit" disabled={creating || !selectedGroup || !amount || !payerId}>
            {creating ? 'Adding…' : 'Add expense'}
          </button>
        </form>
      )}

      <Balances
        members={memberUsers.length ? memberUsers : (users ?? [])}
        balances={balances}
        me={me}
        error={balancesError}
      />

      {error && <div style={{ color: 'red' }}>{error}</div>}

      <div>
        {!expenses ? (
          <div>Loading expenses…</div>
        ) : expenses.length === 0 ? (
          <div>No expenses yet.</div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {[...expenses]
              .sort((a, b) => (a.created_at < b.created_at ? 1 : -1))
              .map((e) => (
                <div
                  key={e.id}
                  style={{
                    border: '1px solid #e5e7eb',
                    borderRadius: 8,
                    padding: 12,
                    background: '#fff',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ fontWeight: 600 }}>{`$${e.amount.toFixed(2)}`}</div>
                      {e.description && (
                        <div style={{ color: '#6b7280', fontSize: 12 }}>{e.description}</div>
                      )}
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ color: '#6b7280', fontSize: 12 }}>
                        payer:
                        {userById.get(e.payer_id) ? (
                          <span>
                            {userById.get(e.payer_id)!.name} ({userById.get(e.payer_id)!.email})
                          </span>
                        ) : (
                          <code>{e.payer_id}</code>
                        )}
                      </div>
                      <div style={{ color: '#6b7280', fontSize: 12 }}>{timeAgo(e.created_at)}</div>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>
    </div>
  );
};
