import React from 'react';

import { useAuth } from '../auth/useAuth';
import { Expenses } from '../expenses/Expenses';
import { GroupsList } from '../groups/GroupsList';

import { Profile } from './Profile';

type Tab = 'profile' | 'groups' | 'expenses';

export const Home: React.FC = () => {
  const { setToken, client } = useAuth();
  const parseTab = (hash: string): Tab | null => {
    const h = (hash || '').replace(/^#/, '');
    if (h === 'profile' || h === 'groups' || h === 'expenses') return h;
    return null;
  };
  const [activeTab, setActiveTab] = React.useState<Tab>(
    () => parseTab(window.location.hash) || 'profile',
  );

  // Guard: verify token is valid on mount; if unauthorized, log out (hides menu + logout button)
  React.useEffect(() => {
    let mounted = true;
    client
      .me()
      .catch(() => {
        if (mounted) setToken(null);
      });
    return () => {
      mounted = false;
    };
  }, [client, setToken]);

  React.useEffect(() => {
    const onHash = () => {
      const t = parseTab(window.location.hash);
      if (t && t !== activeTab) setActiveTab(t);
    };
    window.addEventListener('hashchange', onHash);
    return () => window.removeEventListener('hashchange', onHash);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  React.useEffect(() => {
    const target = `#${activeTab}`;
    if (window.location.hash !== target) {
      try {
        window.history.replaceState(null, '', target);
      } catch {
        window.location.hash = target;
      }
    }
  }, [activeTab]);

  const menuItem = (key: Tab, label: string) => (
    <button
      key={key}
      onClick={() => setActiveTab(key)}
      style={{
        textAlign: 'left',
        padding: '10px 12px',
        border: 'none',
        background: activeTab === key ? '#eef2ff' : 'transparent',
        color: '#111827',
        cursor: 'pointer',
        borderRadius: 6,
        width: '100%',
        fontWeight: activeTab === key ? 600 : 500,
      }}
    >
      {label}
    </button>
  );

  return (
    <div style={{ padding: 20 }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Expense App</h1>
        <button onClick={() => setToken(null)}>Logout</button>
      </header>

      {/* Main area with vertical menu */}
      <div style={{ display: 'flex', gap: 16, marginTop: 16 }}>
        <nav
          aria-label="Home navigation"
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: 8,
            minWidth: 220,
            padding: 8,
            border: '1px solid #e5e7eb',
            borderRadius: 8,
            background: '#fff',
          }}
        >
          {menuItem('profile', 'Profile')}
          {menuItem('groups', 'Group Management')}
          {menuItem('expenses', 'Expenses Management')}
        </nav>

        <section style={{ flex: 1, padding: 8 }}>
          {activeTab === 'profile' && <Profile />}

          {activeTab === 'groups' && (
            <div>
              <h2 style={{ marginTop: 0 }}>Group Management</h2>
              <GroupsList />
            </div>
          )}

          {activeTab === 'expenses' && (
            <div>
              <h2 style={{ marginTop: 0 }}>Expenses Management</h2>
              <Expenses />
            </div>
          )}
        </section>
      </div>
    </div>
  );
};
