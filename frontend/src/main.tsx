import React from 'react';
import { createRoot } from 'react-dom/client';

import { App } from './ui/App';
import { AuthProvider } from './ui/auth/useAuth';

const rootEl = document.getElementById('root');
if (!rootEl) throw new Error('Missing #root');

createRoot(rootEl).render(
  <React.StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </React.StrictMode>,
);
