import type { GroupRead, User } from '@client/index';
import React from 'react';

import { useAuth } from '../auth/useAuth';

export const GroupsList: React.FC = () => {
  const { client } = useAuth();
  const [groups, setGroups] = React.useState<GroupRead[] | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [newName, setNewName] = React.useState('');
  const [creating, setCreating] = React.useState(false);
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [editName, setEditName] = React.useState('');
  const [savingId, setSavingId] = React.useState<string | null>(null);
  const [users, setUsers] = React.useState<User[] | null>(null);
  const [selectedAddUser, setSelectedAddUser] = React.useState<Record<string, string>>({});
  const [addingId, setAddingId] = React.useState<string | null>(null);

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

  if (error) return <div style={{ color: 'red' }}>{error}</div>;
  if (!groups) return <div>Loading groups…</div>;

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newName.trim()) return;
    try {
      setCreating(true);
      setError(null);
      const g = await client.createGroup(newName.trim());
      setGroups((prev) => (prev ? [g, ...prev] : [g]));
      setNewName('');
    } catch (e: any) {
      setError(e?.message || 'Failed to create group');
    } finally {
      setCreating(false);
    }
  };

  const startEdit = (g: GroupRead) => {
    setEditingId(g.id);
    setEditName(g.name);
    setError(null);
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditName('');
  };

  const saveEdit = async (id: string) => {
    if (!editName.trim()) return;
    try {
      setSavingId(id);
      const updated = await client.updateGroup(id, editName.trim());
      setGroups((prev) => (prev ? prev.map((g) => (g.id === id ? updated : g)) : [updated]));
      setEditingId(null);
      setEditName('');
    } catch (e: any) {
      setError(e?.message || 'Failed to update group');
    } finally {
      setSavingId(null);
    }
  };

  const renderList = () => {
    if (groups.length === 0) return <div>No groups yet.</div>;
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {groups.map((g) => (
          <div
            key={g.id}
            style={{
              border: '1px solid #e5e7eb',
              borderRadius: 8,
              padding: 12,
              background: '#fff',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                gap: 12,
              }}
            >
              <div style={{ flex: 1 }}>
                {editingId === g.id ? (
                  <input
                    type="text"
                    value={editName}
                    onChange={(e) => setEditName(e.target.value)}
                    style={{
                      width: '100%',
                      padding: 6,
                      border: '1px solid #e5e7eb',
                      borderRadius: 6,
                    }}
                  />
                ) : (
                  <div style={{ fontWeight: 600 }}>{g.name || 'Untitled group'}</div>
                )}
                <div style={{ color: '#6b7280', fontSize: 12 }}>
                  {g.members.length} member{g.members.length === 1 ? '' : 's'}
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                {users &&
                  (() => {
                    const nonMembers = users.filter((u) => !g.members.includes(u.id));
                    if (nonMembers.length === 0) {
                      return (
                        <span style={{ color: '#6b7280', fontSize: 12 }}>
                          All users are members
                        </span>
                      );
                    }
                    const selected =
                      selectedAddUser[g.id] &&
                      nonMembers.some((u) => u.id === selectedAddUser[g.id])
                        ? selectedAddUser[g.id]
                        : nonMembers[0].id;
                    return (
                      <>
                        <select
                          value={selected}
                          onChange={(e) =>
                            setSelectedAddUser((m) => ({ ...m, [g.id]: e.target.value }))
                          }
                          style={{ padding: 6, border: '1px solid #e5e7eb', borderRadius: 6 }}
                          aria-label="Add user to group"
                        >
                          {nonMembers.map((u) => (
                            <option key={u.id} value={u.id}>
                              {u.name} ({u.email})
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={async () => {
                            const userId = selected;
                            try {
                              setAddingId(g.id);
                              const updated = await client.joinGroup(g.id, userId);
                              setGroups((prev) =>
                                prev ? prev.map((x) => (x.id === g.id ? updated : x)) : [updated],
                              );
                            } catch (e: any) {
                              setError(e?.message || 'Failed to add user');
                            } finally {
                              setAddingId(null);
                            }
                          }}
                          disabled={addingId === g.id}
                        >
                          {addingId === g.id ? 'Adding…' : 'Add user'}
                        </button>
                      </>
                    );
                  })()}
                {editingId === g.id ? (
                  <>
                    <button
                      onClick={() => saveEdit(g.id)}
                      disabled={savingId === g.id || !editName.trim()}
                    >
                      {savingId === g.id ? 'Saving…' : 'Save'}
                    </button>
                    <button onClick={cancelEdit} disabled={savingId === g.id}>
                      Cancel
                    </button>
                  </>
                ) : (
                  <button onClick={() => startEdit(g)}>Edit</button>
                )}
                <code style={{ color: '#6b7280', fontSize: 12 }}>{g.id}</code>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <form onSubmit={onCreate} style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
        <input
          type="text"
          placeholder="New group name"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          style={{ flex: 1, padding: 8, border: '1px solid #e5e7eb', borderRadius: 6 }}
        />
        <button type="submit" disabled={creating || !newName.trim()}>
          {creating ? 'Creating…' : 'Create group'}
        </button>
      </form>

      {error && <div style={{ color: 'red' }}>{error}</div>}

      {renderList()}
    </div>
  );
};
