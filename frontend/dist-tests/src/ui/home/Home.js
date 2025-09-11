import { jsx as _jsx, jsxs as _jsxs } from 'react/jsx-runtime';
import React from 'react';
import { useAuth } from '../auth/useAuth';
import { Profile } from './Profile';
import { GroupsList } from '../groups/GroupsList';
import { Expenses } from '../expenses/Expenses';
export const Home = () => {
  const { setToken } = useAuth();
  const [activeTab, setActiveTab] = React.useState('profile');
  const menuItem = (key, label) =>
    _jsx(
      'button',
      {
        onClick: () => setActiveTab(key),
        style: {
          textAlign: 'left',
          padding: '10px 12px',
          border: 'none',
          background: activeTab === key ? '#eef2ff' : 'transparent',
          color: '#111827',
          cursor: 'pointer',
          borderRadius: 6,
          width: '100%',
          fontWeight: activeTab === key ? 600 : 500,
        },
        children: label,
      },
      key,
    );
  return _jsxs('div', {
    style: { padding: 20 },
    children: [
      _jsxs('header', {
        style: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
        children: [
          _jsx('h1', { children: 'Expense App' }),
          _jsx('button', { onClick: () => setToken(null), children: 'Logout' }),
        ],
      }),
      _jsxs('div', {
        style: { display: 'flex', gap: 16, marginTop: 16 },
        children: [
          _jsxs('nav', {
            'aria-label': 'Home navigation',
            style: {
              display: 'flex',
              flexDirection: 'column',
              gap: 8,
              minWidth: 220,
              padding: 8,
              border: '1px solid #e5e7eb',
              borderRadius: 8,
              background: '#fff',
            },
            children: [
              menuItem('profile', 'Profile'),
              menuItem('groups', 'Group Management'),
              menuItem('expenses', 'Expenses Management'),
            ],
          }),
          _jsxs('section', {
            style: { flex: 1, padding: 8 },
            children: [
              activeTab === 'profile' && _jsx(Profile, {}),
              activeTab === 'groups' &&
                _jsxs('div', {
                  children: [
                    _jsx('h2', { style: { marginTop: 0 }, children: 'Group Management' }),
                    _jsx(GroupsList, {}),
                  ],
                }),
              activeTab === 'expenses' &&
                _jsxs('div', {
                  children: [
                    _jsx('h2', { style: { marginTop: 0 }, children: 'Expenses Management' }),
                    _jsx(Expenses, {}),
                  ],
                }),
            ],
          }),
        ],
      }),
    ],
  });
};
