import React, { useState, useEffect, useRef } from 'react';
import Navbar from '../components/Navbar';
import ChartGrid from '../components/ChartGrid';
import AnalysisPanel from '../components/AnalysisPanel';
import SentimentPanel from '../components/SentimentPanel';
import LoadingSpinner from '../components/LoadingSpinner';
import { analyse } from '../services/api';

const MAX_RECENT = 8;

const styles = {
  page: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: 'var(--bg)',
    overflow: 'hidden',
  },
  body: {
    flex: 1,
    display: 'flex',
    overflow: 'hidden',
  },
  sidebar: {
    width: '220px',
    flexShrink: 0,
    background: 'var(--surface)',
    borderRight: '1px solid var(--border)',
    display: 'flex',
    flexDirection: 'column',
    padding: '16px',
    gap: '12px',
  },
  inputWrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: '8px',
  },
  inputLabel: {
    fontFamily: 'var(--mono)',
    fontSize: '0.68rem',
    color: 'var(--text-muted)',
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
  },
  input: {
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: '5px',
    padding: '8px 10px',
    color: 'var(--text)',
    fontSize: '0.85rem',
    fontFamily: 'var(--mono)',
    outline: 'none',
    width: '100%',
    transition: 'border-color 0.15s',
    textTransform: 'uppercase',
  },
  analyseBtn: (disabled) => ({
    background: disabled ? 'rgba(0,255,136,0.15)' : 'var(--accent)',
    color: disabled ? 'var(--text-muted)' : '#0a0a0f',
    border: 'none',
    borderRadius: '5px',
    padding: '9px',
    fontWeight: 700,
    fontSize: '0.8rem',
    fontFamily: 'var(--mono)',
    letterSpacing: '0.08em',
    cursor: disabled ? 'not-allowed' : 'pointer',
    width: '100%',
    transition: 'background 0.15s, color 0.15s',
  }),
  divider: {
    height: '1px',
    background: 'var(--border)',
    margin: '4px 0',
  },
  recentLabel: {
    fontFamily: 'var(--mono)',
    fontSize: '0.68rem',
    color: 'var(--text-muted)',
    letterSpacing: '0.12em',
    textTransform: 'uppercase',
  },
  recentList: {
    display: 'flex',
    flexDirection: 'column',
    gap: '4px',
    overflowY: 'auto',
  },
  recentItem: {
    fontFamily: 'var(--mono)',
    fontSize: '0.82rem',
    color: 'var(--text-muted)',
    padding: '6px 8px',
    borderRadius: '4px',
    cursor: 'pointer',
    transition: 'background 0.1s, color 0.1s',
    letterSpacing: '0.04em',
  },
  main: {
    flex: 1,
    overflow: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  empty: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    color: 'var(--text-muted)',
    gap: '12px',
    textAlign: 'center',
    padding: '48px',
  },
  emptyTitle: {
    fontFamily: 'var(--mono)',
    fontSize: '0.9rem',
    color: 'var(--text-muted)',
    letterSpacing: '0.08em',
  },
  emptyHint: {
    fontSize: '0.78rem',
    color: 'var(--text-muted)',
    opacity: 0.6,
    lineHeight: 1.7,
  },
  errorBox: {
    background: 'rgba(255,68,68,0.08)',
    border: '1px solid rgba(255,68,68,0.25)',
    borderRadius: '6px',
    padding: '12px 16px',
    color: 'var(--red)',
    fontFamily: 'var(--mono)',
    fontSize: '0.82rem',
  },
};

export default function Dashboard() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [recent, setRecent] = useState(() => {
    try { return JSON.parse(localStorage.getItem('recent_tickers') || '[]'); }
    catch { return []; }
  });
  const inputRef = useRef(null);

  const saveRecent = (ticker) => {
    const updated = [ticker, ...recent.filter(t => t !== ticker)].slice(0, MAX_RECENT);
    setRecent(updated);
    localStorage.setItem('recent_tickers', JSON.stringify(updated));
  };

  const handleAnalyse = async (queryText) => {
    const q = (queryText || query).trim();
    if (!q || loading) return;
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await analyse(q);
      setResult(res.data);
      saveRecent(res.data.ticker);
    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Check agents are running.');
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === 'Enter') handleAnalyse();
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div style={styles.page}>
      <Navbar />
      <div style={styles.body}>
        <aside style={styles.sidebar}>
          <div style={styles.inputWrap}>
            <span style={styles.inputLabel}>Stock / Query</span>
            <input
              ref={inputRef}
              style={styles.input}
              type="text"
              placeholder="AAPL, NVDA, Tesla..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKey}
              onFocus={e => (e.target.style.borderColor = 'var(--accent)')}
              onBlur={e => (e.target.style.borderColor = 'var(--border)')}
              disabled={loading}
            />
            <button
              style={styles.analyseBtn(loading || !query.trim())}
              onClick={() => handleAnalyse()}
              disabled={loading || !query.trim()}
            >
              {loading ? 'RUNNING...' : 'ANALYSE'}
            </button>
          </div>

          {recent.length > 0 && (
            <>
              <div style={styles.divider} />
              <span style={styles.recentLabel}>Recent</span>
              <div style={styles.recentList}>
                {recent.map(t => (
                  <div
                    key={t}
                    style={styles.recentItem}
                    onClick={() => { setQuery(t); handleAnalyse(t); }}
                    onMouseEnter={e => {
                      e.currentTarget.style.background = 'var(--accent-dim)';
                      e.currentTarget.style.color = 'var(--accent)';
                    }}
                    onMouseLeave={e => {
                      e.currentTarget.style.background = 'transparent';
                      e.currentTarget.style.color = 'var(--text-muted)';
                    }}
                  >
                    {t}
                  </div>
                ))}
              </div>
            </>
          )}
        </aside>

        <main style={styles.main}>
          {error && <div style={styles.errorBox}>ERROR: {error}</div>}

          {loading && <LoadingSpinner ticker={query.trim().toUpperCase()} />}

          {!loading && !result && !error && (
            <div style={styles.empty}>
              <div style={{ fontSize: '2rem' }}>📈</div>
              <div style={styles.emptyTitle}>READY</div>
              <div style={styles.emptyHint}>
                Enter a stock ticker or company name<br />
                to run the multi-agent research pipeline
              </div>
            </div>
          )}

          {!loading && result && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <AnalysisPanel ticker={result.ticker} response={result.response} />
              <SentimentPanel sentiment={result.sentiment} />
              <ChartGrid charts={result.charts} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
