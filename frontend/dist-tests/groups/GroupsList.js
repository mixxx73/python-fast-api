import { jsx as _jsx, jsxs as _jsxs, Fragment as _Fragment } from 'react/jsx-runtime';
import React from 'react';
import { useAuth } from '../auth/useAuth';
export const GroupsList = () => {
  const { client } = useAuth();
  const [groups, setGroups] = React.useState(null);
  const [error, setError] = React.useState(null);
  const [newName, setNewName] = React.useState('');
  const [creating, setCreating] = React.useState(false);
  const [editingId, setEditingId] = React.useState(null);
  const [editName, setEditName] = React.useState('');
  const [savingId, setSavingId] = React.useState(null);
  const [users, setUsers] = React.useState(null);
  const [selectedAddUser, setSelectedAddUser] = React.useState({});
  const [addingId, setAddingId] = React.useState(null);
  React.useEffect(() => {
    let mounted = true;
    Promise.all([client.listGroups(), client.listUsers()])
      .then(([gs, us]) => {
        if (mounted) {
          setGroups(gs);
          setUsers(us);
        }
      })
      .catch((e) => setError(e?.message || 'Failed to load groups'));
    return () => {
      mounted = false;
    };
  }, [client]);
  if (error) return _jsx('div', { style: { color: 'red' }, children: error });
  if (!groups) return _jsx('div', { children: 'Loading groups\u2026' });
  const onCreate = async (e) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      setCreating(true);
      setError(null);
      const g = await client.createGroup(newName.trim());
      setGroups((prev) => (prev ? [g, ...prev] : [g]));
      setNewName('');
    } catch (e) {
      setError(e?.message || 'Failed to create group');
    } finally {
      setCreating(false);
    }
  };
  const startEdit = (g) => {
    setEditingId(g.id);
    setEditName(g.name);
    setError(null);
  };
  const cancelEdit = () => {
    setEditingId(null);
    setEditName('');
  };
  const saveEdit = async (id) => {
    if (!editName.trim()) return;
    try {
      setSavingId(id);
      const updated = await client.updateGroup(id, editName.trim());
      setGroups((prev) => (prev ? prev.map((g) => (g.id === id ? updated : g)) : [updated]));
      setEditingId(null);
      setEditName('');
    } catch (e) {
      setError(e?.message || 'Failed to update group');
    } finally {
      setSavingId(null);
    }
  };
  const renderList = () => {
    if (groups.length === 0) return _jsx('div', { children: 'No groups yet.' });
    return _jsx('div', {
      style: { display: 'flex', flexDirection: 'column', gap: 8 },
      children: groups.map((g) =>
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
              style: {
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: 12,
              },
              children: [
                _jsxs('div', {
                  style: { flex: 1 },
                  children: [
                    editingId === g.id
                      ? _jsx('input', {
                          type: 'text',
                          value: editName,
                          onChange: (e) => setEditName(e.target.value),
                          style: {
                            width: '100%',
                            padding: 6,
                            border: '1px solid #e5e7eb',
                            borderRadius: 6,
                          },
                        })
                      : _jsx('div', {
                          style: { fontWeight: 600 },
                          children: g.name || 'Untitled group',
                        }),
                    _jsxs('div', {
                      style: { color: '#6b7280', fontSize: 12 },
                      children: [g.members.length, ' member', g.members.length === 1 ? '' : 's'],
                    }),
                  ],
                }),
                _jsxs('div', {
                  style: { display: 'flex', alignItems: 'center', gap: 8 },
                  children: [
                    users &&
                      (() => {
                        const nonMembers = users.filter((u) => !g.members.includes(u.id));
                        if (nonMembers.length === 0) {
                          return _jsx('span', {
                            style: { color: '#6b7280', fontSize: 12 },
                            children: 'All users are members',
                          });
                        }
                        const selected =
                          selectedAddUser[g.id] &&
                          nonMembers.some((u) => u.id === selectedAddUser[g.id])
                            ? selectedAddUser[g.id]
                            : nonMembers[0].id;
                        return _jsxs(_Fragment, {
                          children: [
                            _jsx('select', {
                              value: selected,
                              onChange: (e) =>
                                setSelectedAddUser((m) => ({ ...m, [g.id]: e.target.value })),
                              style: { padding: 6, border: '1px solid #e5e7eb', borderRadius: 6 },
                              'aria-label': 'Add user to group',
                              children: nonMembers.map((u) =>
                                _jsxs(
                                  'option',
                                  { value: u.id, children: [u.name, ' (', u.email, ')'] },
                                  u.id,
                                ),
                              ),
                            }),
                            _jsx('button', {
                              onClick: async () => {
                                const userId = selected;
                                try {
                                  setAddingId(g.id);
                                  const updated = await client.joinGroup(g.id, userId);
                                  setGroups((prev) =>
                                    prev
                                      ? prev.map((x) => (x.id === g.id ? updated : x))
                                      : [updated],
                                  );
                                } catch (e) {
                                  setError(e?.message || 'Failed to add user');
                                } finally {
                                  setAddingId(null);
                                }
                              },
                              disabled: addingId === g.id,
                              children: addingId === g.id ? 'Adding…' : 'Add user',
                            }),
                          ],
                        });
                      })(),
                    editingId === g.id
                      ? _jsxs(_Fragment, {
                          children: [
                            _jsx('button', {
                              onClick: () => saveEdit(g.id),
                              disabled: savingId === g.id || !editName.trim(),
                              children: savingId === g.id ? 'Saving…' : 'Save',
                            }),
                            _jsx('button', {
                              onClick: cancelEdit,
                              disabled: savingId === g.id,
                              children: 'Cancel',
                            }),
                          ],
                        })
                      : _jsx('button', { onClick: () => startEdit(g), children: 'Edit' }),
                    _jsx('code', { style: { color: '#6b7280', fontSize: 12 }, children: g.id }),
                  ],
                }),
              ],
            }),
          },
          g.id,
        ),
      ),
    });
  };
  return _jsxs('div', {
    style: { display: 'flex', flexDirection: 'column', gap: 16 },
    children: [
      _jsxs('form', {
        onSubmit: onCreate,
        style: { display: 'flex', gap: 8, alignItems: 'center' },
        children: [
          _jsx('input', {
            type: 'text',
            placeholder: 'New group name',
            value: newName,
            onChange: (e) => setNewName(e.target.value),
            style: { flex: 1, padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 },
          }),
          _jsx('button', {
            type: 'submit',
            disabled: creating || !newName.trim(),
            children: creating ? 'Creating…' : 'Create group',
          }),
        ],
      }),
      error && _jsx('div', { style: { color: 'red' }, children: error }),
      renderList(),
    ],
  });
};
