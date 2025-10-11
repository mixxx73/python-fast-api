import type { User, GroupRead } from '@client/index';
import React from 'react';

import { useAuth } from '../auth/useAuth';

export const Profile: React.FC = () => {
  const { client } = useAuth();
  const [user, setUser] = React.useState<User | null>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [editing, setEditing] = React.useState(false);
  const [nameInput, setNameInput] = React.useState('');
  const [saving, setSaving] = React.useState(false);
  const [groups, setGroups] = React.useState<GroupRead[] | null>(null);
  const [groupsError, setGroupsError] = React.useState<string | null>(null);

  React.useEffect(() => {
    client
      .me()
      .then(setUser)
      .catch((e) => setError(e?.message || 'Failed to load profile'));
  }, [client]);

  React.useEffect(() => {
    if (!user) {
      return;
    }
    setGroups(null);
    setGroupsError(null);
    client
      .listUserGroups(user.id)
      .then(setGroups)
      .catch((e) => setGroupsError(e?.message || 'Failed to load groups'));
  }, [client, user]);

  if (error) {
    return <div style={{ color: 'red' }}>{error}</div>;
  }
  if (!user) {
    return <div>Loading profile…</div>;
  }

  const startEdit = () => {
    setEditing(true);
    setNameInput(user.name);
  };

  const cancelEdit = () => {
    setEditing(false);
    setNameInput('');
    // Clear any previous error on cancel
    setError(null);
  };

  const saveName = async () => {
    if (!user) {
      return;
    }
    const newName = nameInput.trim();
    if (!newName || newName === user.name) {
      setEditing(false);
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const updated = await client.updateUserName(user.id, newName);
      setUser(updated);
      setEditing(false);
    } catch (e: any) {
      setError(e?.message || 'Failed to update name');
    } finally {
      setSaving(false);
    }
  };

  return (
    <section style={{ marginTop: 16 }}>
      <h2 style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <span style={{ flex: 1 }}>Your Profile</span>
        {!editing && (
          <button onClick={startEdit} style={{ padding: '4px 8px' }}>
            Edit
          </button>
        )}
      </h2>
      <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, maxWidth: 480 }}>
        <div style={{ marginBottom: 8 }}>
          <strong>Name:</strong>{' '}
          {!editing ? (
            <span>{user.name}</span>
          ) : (
            <span>
              <input
                type="text"
                value={nameInput}
                onChange={(e) => setNameInput(e.target.value)}
                disabled={saving}
                style={{ marginRight: 8 }}
              />
              <button
                onClick={saveName}
                disabled={saving || !nameInput.trim()}
                style={{ marginRight: 4 }}
              >
                {saving ? 'Saving…' : 'Save'}
              </button>
              <button onClick={cancelEdit} disabled={saving}>
                Cancel
              </button>
            </span>
          )}
        </div>
        <div>
          <strong>Email:</strong> {user.email}
        </div>
        <div>
          <strong>User ID:</strong> {user.id}
        </div>
        <div style={{ marginTop: 12 }}>
          <strong>Groups:</strong>
          <div style={{ marginTop: 4 }}>
            {groupsError && <div style={{ color: 'red' }}>{groupsError}</div>}
            {!groups && !groupsError && <div>Loading groups…</div>}
            {groups && groups.length === 0 && <div>No groups yet.</div>}
            {groups && groups.length > 0 && (
              <ul style={{ paddingLeft: 18, margin: 0 }}>
                {groups.map((g) => (
                  <li key={g.id}>{g.name || '(unnamed group)'}</li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};
