import type { BalanceEntry, User } from '@client/index';
import React from 'react';

type Props = {
  members: User[];
  balances: BalanceEntry[] | null;
  me: User | null;
  error?: string | null;
};

export const Balances: React.FC<Props> = ({ members, balances, me, error }) => {
  const [relativeMode, setRelativeMode] = React.useState(true);

  // Persist mode across sessions
  React.useEffect(() => {
    try {
      const v = localStorage.getItem('expense_bal_mode');
      if (v === 'group') {
        setRelativeMode(false);
      } else if (v === 'relative') {
        setRelativeMode(true);
      }
    } catch {}

  }, []);

  React.useEffect(() => {
    try {
      localStorage.setItem('expense_bal_mode', relativeMode ? 'relative' : 'group');
    } catch {}

  }, [relativeMode]);

  const totals = React.useMemo(() => {
    if (!balances || !me) {
      return null;
    }
    const meBal = balances.find((b) => b.user_id === me.id)?.balance || 0;

    if (meBal === 0) {
      return { pos: 0, neg: 0 };
    }

    const pos = meBal > 0 ? Math.round(meBal * 100) / 100 : 0;
    const neg = meBal < 0 ? Math.round(-meBal * 100) / 100 : 0;

    return { pos, neg };
  }, [balances, me]);

  const totalsGroup = React.useMemo(() => {
    if (!balances) {
      return null;
    }

    let pos = 0;
    let neg = 0;
    for (const b of balances) {
      if (b.balance > 0) {
        pos += b.balance;
      } else if (b.balance < 0) {
        neg += -b.balance;
      }
    }

    pos = Math.round(pos * 100) / 100;
    neg = Math.round(neg * 100) / 100;

    return { pos, neg };
  }, [balances]);

  const relativeBalances = React.useMemo(() => {
    if (!balances || !me) {
      return null as Map<string, number> | null;
    }

    const meEntry = balances.find((b) => b.user_id === me.id);
    const meBal = meEntry ? meEntry.balance : 0;
    const result = new Map<string, number>();
    if (meBal > 0) {
      let remaining = meBal;
      const debtors = balances
        .filter((b) => b.user_id !== me.id && b.balance < 0)
        .sort((a, b) => a.balance - b.balance);
      for (const d of debtors) {
        if (remaining <= 0) {
          result.set(d.user_id, 0);
          continue;
        }
        const amt = Math.min(remaining, -d.balance);
        result.set(d.user_id, amt);
        remaining -= amt;
      }
      balances
        .filter((b) => b.user_id !== me.id && b.balance >= 0)
        .forEach((b) => result.set(b.user_id, 0));
      result.set(me.id, 0);
    } else if (meBal < 0) {
      let remaining = -meBal;
      const creditors = balances
        .filter((b) => b.user_id !== me.id && b.balance > 0)
        .sort((a, b) => b.balance - a.balance);
      for (const c of creditors) {
        if (remaining <= 0) {
          result.set(c.user_id, 0);
          continue;
        }
        const amt = Math.min(remaining, c.balance);
        result.set(c.user_id, -amt);
        remaining -= amt;
      }
      balances
        .filter((b) => b.user_id !== me.id && b.balance <= 0)
        .forEach((b) => result.set(b.user_id, 0));
      result.set(me.id, 0);
    } else {
      balances.forEach((b) => result.set(b.user_id, 0));
    }

    return result;
  }, [balances, me]);

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h3 style={{ margin: '8px 0' }}>Balances</h3>
        <div style={{ fontSize: 12, color: '#6b7280' }}>
          <label>
            <input
              type="radio"
              name="bal-mode"
              checked={relativeMode}
              onChange={() => setRelativeMode(true)}
            />{' '}
            relative to me
          </label>
          <label style={{ marginLeft: 8 }}>
            <input
              type="radio"
              name="bal-mode"
              checked={!relativeMode}
              onChange={() => setRelativeMode(false)}
            />{' '}
            group
          </label>
        </div>
      </div>
      <div style={{ color: '#6b7280', fontSize: 12, marginBottom: 6 }}>
        {relativeMode
          ? "Shows, for each member, whether they owe you, you owe them, or you're even."
          : 'Overall group balances; positive = owed, negative = owes.'}
      </div>
      {error && <div style={{ color: 'red' }}>{error}</div>}
      {!balances && !error && <div>Loading balances…</div>}
      {balances && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
          {relativeMode ? (
            <>
              {members
                .filter((u) => !me || u.id !== me.id)
                .map((u) => {
                  const val = relativeBalances?.get(u.id) ?? 0;
                  let text = 'even';
                  let color = '#6b7280';
                  if (val > 0) {
                    text = `owes you $${val.toFixed(2)}`;
                    color = '#16a34a';
                  } else if (val < 0) {
                    text = `you owe $${(-val).toFixed(2)}`;
                    color = '#dc2626';
                  }
                  return (
                    <div key={u.id} style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <div>
                        {u.name} ({u.email})
                      </div>
                      <div style={{ color }}>{text}</div>
                    </div>
                  );
                })}
              {totals && (
                <div
                  style={{
                    marginTop: 6,
                    paddingTop: 6,
                    borderTop: '1px solid #e5e7eb',
                    color: '#6b7280',
                  }}
                >
                  {totals.pos > 0 && (
                    <div>
                      Net: others owe you{' '}
                      <span style={{ color: '#16a34a' }}>${totals.pos.toFixed(2)}</span>
                    </div>
                  )}
                  {totals.neg > 0 && (
                    <div>
                      Net: you owe others{' '}
                      <span style={{ color: '#dc2626' }}>${totals.neg.toFixed(2)}</span>
                    </div>
                  )}
                  {totals.pos === 0 && totals.neg === 0 && <div>Net: even</div>}
                </div>
              )}
            </>
          ) : (
            <>
              {members.map((u) => {
                const entry = balances.find((b) => b.user_id === u.id);
                const val = entry ? entry.balance : 0;
                const pos = val > 0;
                return (
                  <div key={u.id} style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div>
                      {u.name} ({u.email})
                    </div>
                    <div style={{ color: pos ? '#16a34a' : val < 0 ? '#dc2626' : '#6b7280' }}>
                      {pos ? '+' : ''}
                      {val.toFixed(2)}
                    </div>
                  </div>
                );
              })}
              {totalsGroup && (
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginTop: 6,
                    paddingTop: 6,
                    borderTop: '1px solid #e5e7eb',
                  }}
                >
                  <div style={{ fontWeight: 600 }}>Totals</div>
                  <div>
                    <span style={{ color: '#16a34a', marginRight: 8 }}>
                      +{totalsGroup.pos.toFixed(2)}
                    </span>
                    <span style={{ color: '#dc2626' }}>-{totalsGroup.neg.toFixed(2)}</span>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};
