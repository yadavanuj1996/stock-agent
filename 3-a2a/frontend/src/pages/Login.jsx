import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';

const styles = {
  page: {
    minHeight: '100vh',
    background: 'var(--bg)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '24px',
  },
  card: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '10px',
    padding: '40px',
    width: '100%',
    maxWidth: '380px',
  },
  logo: {
    fontFamily: 'var(--mono)',
    fontSize: '1rem',
    fontWeight: 600,
    color: 'var(--accent)',
    letterSpacing: '0.1em',
    marginBottom: '8px',
  },
  title: {
    fontSize: '1.35rem',
    fontWeight: 600,
    color: 'var(--text)',
    marginBottom: '4px',
  },
  subtitle: {
    fontSize: '0.82rem',
    color: 'var(--text-muted)',
    marginBottom: '32px',
  },
  label: {
    display: 'block',
    fontSize: '0.75rem',
    fontFamily: 'var(--mono)',
    color: 'var(--text-muted)',
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
    marginBottom: '6px',
  },
  input: {
    width: '100%',
    background: 'var(--bg)',
    border: '1px solid var(--border)',
    borderRadius: '6px',
    padding: '10px 14px',
    color: 'var(--text)',
    fontSize: '0.9rem',
    fontFamily: 'var(--mono)',
    outline: 'none',
    marginBottom: '18px',
    transition: 'border-color 0.15s',
  },
  inputFocus: {
    borderColor: 'var(--accent)',
  },
  error: {
    background: 'rgba(255, 68, 68, 0.1)',
    border: '1px solid rgba(255, 68, 68, 0.3)',
    borderRadius: '6px',
    padding: '10px 14px',
    color: 'var(--red)',
    fontSize: '0.82rem',
    marginBottom: '18px',
    fontFamily: 'var(--mono)',
  },
  btn: {
    width: '100%',
    background: 'var(--accent)',
    color: '#0a0a0f',
    border: 'none',
    borderRadius: '6px',
    padding: '12px',
    fontWeight: 700,
    fontSize: '0.9rem',
    cursor: 'pointer',
    letterSpacing: '0.05em',
    fontFamily: 'var(--mono)',
    transition: 'opacity 0.15s',
    marginTop: '4px',
  },
  btnDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  back: {
    display: 'block',
    textAlign: 'center',
    marginTop: '20px',
    fontSize: '0.8rem',
    color: 'var(--text-muted)',
    textDecoration: 'none',
    cursor: 'pointer',
  },
};

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [focusedField, setFocusedField] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!username || !password) return;
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <div style={styles.logo}>STOCK_AGENT</div>
        <div style={styles.title}>Sign in</div>
        <div style={styles.subtitle}>Access the research dashboard</div>

        <form onSubmit={handleSubmit}>
          {error && <div style={styles.error}>{error}</div>}

          <label style={styles.label}>Username</label>
          <input
            style={{
              ...styles.input,
              ...(focusedField === 'user' ? styles.inputFocus : {}),
            }}
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            onFocus={() => setFocusedField('user')}
            onBlur={() => setFocusedField(null)}
            autoFocus
            autoComplete="username"
          />

          <label style={styles.label}>Password</label>
          <input
            style={{
              ...styles.input,
              ...(focusedField === 'pass' ? styles.inputFocus : {}),
              marginBottom: '24px',
            }}
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            onFocus={() => setFocusedField('pass')}
            onBlur={() => setFocusedField(null)}
            autoComplete="current-password"
          />

          <button
            type="submit"
            style={{
              ...styles.btn,
              ...(loading || !username || !password ? styles.btnDisabled : {}),
            }}
            disabled={loading || !username || !password}
          >
            {loading ? 'SIGNING IN...' : 'SIGN IN'}
          </button>
        </form>

        <span style={styles.back} onClick={() => navigate('/')}>
          ← Back to home
        </span>
      </div>
    </div>
  );
}
