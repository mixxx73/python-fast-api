import { jsx as _jsx, jsxs as _jsxs } from 'react/jsx-runtime';
import React from 'react';
import { useAuth } from '../auth/useAuth';
export const Expenses = () => {
  const { client } = useAuth();
  const [groups, setGroups] = React.useState(null);
  const [myGroups, setMyGroups] = React.useState(null);
  const [selectedGroup, setSelectedGroup] = React.useState(null);
  const [expenses, setExpenses] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [users, setUsers] = React.useState(null);
  const [me, setMe] = React.useState(null);
  const [amount, setAmount] = React.useState('');
  const [description, setDescription] = React.useState('');
  const [creating, setCreating] = React.useState(false);
  const [payerId, setPayerId] = React.useState('');
  React.useEffect(() => {
    let mounted = true;
    Promise.all([client.listGroups(), client.me(), client.listUsers()])
      .then(([gs, meUser, us]) => {
        if (!mounted) return;
        setGroups(gs);
        const mine = gs.filter((g) => g.members.includes(meUser.id));
        setMyGroups(mine);
        if (mine.length > 0) setSelectedGroup((prev) => prev ?? mine[0].id);
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
      return;
    }
    setExpenses(null);
    client
      .listGroupExpenses(selectedGroup)
      .then((es) => {
        if (mounted) setExpenses(es);
      })
      .catch((e) => setError(e?.message || 'Failed to load expenses'));
    return () => {
      mounted = false;
    };
  }, [client, selectedGroup]);
  // Ensure payer stays valid for the selected group
  React.useEffect(() => {
    if (!selectedGroup || !groups || !users) return;
    const g = groups.find((x) => x.id === selectedGroup);
    if (!g) return;
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
  const onCreate = async (e) => {
    e.preventDefault();
    if (!selectedGroup) return;
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
        payer_id: payerId || me?.id,
      });
      setExpenses((prev) => (prev ? [created, ...prev] : [created]));
      setAmount('');
      setDescription('');
    } catch (e) {
      setError(e?.message || 'Failed to create expense');
    } finally {
      setCreating(false);
    }
  };
  const groupOptions = (myGroups ?? []).map((g) =>
    _jsx('option', { value: g.id, children: g.name || 'Untitled' }, g.id),
  );
  const selectedGroupObj = (groups ?? []).find((g) => g.id === selectedGroup) || null;
  const memberUsers =
    selectedGroupObj && users ? users.filter((u) => selectedGroupObj.members.includes(u.id)) : [];
  const payerOptions = memberUsers.map((u) =>
    _jsxs('option', { value: u.id, children: [u.name, ' (', u.email, ')'] }, u.id),
  );
  return _jsxs('div', {
    style: { display: 'flex', flexDirection: 'column', gap: 16 },
    children: [
      _jsxs('div', {
        style: { display: 'flex', alignItems: 'center', gap: 8 },
        children: [
          _jsx('label', { style: { fontWeight: 600 }, children: 'Group' }),
          _jsx('select', {
            value: selectedGroup || '',
            onChange: (e) => setSelectedGroup(e.target.value || null),
            style: { padding: 6 },
            children: groupOptions,
          }),
        ],
      }),
      _jsxs('form', {
        onSubmit: onCreate,
        style: { display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' },
        children: [
          _jsx('input', {
            type: 'number',
            step: '0.01',
            min: '0',
            placeholder: 'Amount',
            value: amount,
            onChange: (e) => setAmount(e.target.value),
            style: { width: 140, padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 },
          }),
          _jsx('select', {
            value: payerId,
            onChange: (e) => setPayerId(e.target.value),
            style: { minWidth: 220, padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 },
            'aria-label': 'Payer',
            children: payerOptions,
          }),
          _jsx('input', {
            type: 'text',
            placeholder: 'Description (optional)',
            value: description,
            onChange: (e) => setDescription(e.target.value),
            style: {
              flex: 1,
              minWidth: 240,
              padding: 8,
              border: '1px solid #e5e7eb',
              borderRadius: 6,
            },
          }),
          _jsx('button', {
            type: 'submit',
            disabled: creating || !selectedGroup || !amount || !payerId,
            children: creating ? 'Adding…' : 'Add expense',
          }),
        ],
      }),
      error && _jsx('div', { style: { color: 'red' }, children: error }),
      _jsx('div', {
        children: !expenses
          ? _jsx('div', { children: 'Loading expenses\u2026' })
          : expenses.length === 0
            ? _jsx('div', { children: 'No expenses yet.' })
            : _jsx('div', {
                style: { display: 'flex', flexDirection: 'column', gap: 8 },
                children: expenses.map((e) =>
                  _jsx(
                    'div',
                    {
                      style: {
                        border: '1px solid #e5e7eb',
                        borderRadius: 8,
                        padding: 12,
                        background: '#fff',
                      },
                      children: _jsxs('div', {
                        style: { display: 'flex', justifyContent: 'space-between' },
                        children: [
                          _jsxs('div', {
                            children: [
                              _jsx('div', {
                                style: { fontWeight: 600 },
                                children: `$${e.amount.toFixed(2)}`,
                              }),
                              e.description &&
                                _jsx('div', {
                                  style: { color: '#6b7280', fontSize: 12 },
                                  children: e.description,
                                }),
                            ],
                          }),
                          _jsxs('div', {
                            style: { color: '#6b7280', fontSize: 12 },
                            children: ['payer: ', _jsx('code', { children: e.payer_id })],
                          }),
                        ],
                      }),
                    },
                    e.id,
                  ),
                ),
              }),
      }),
    ],
  });
};
