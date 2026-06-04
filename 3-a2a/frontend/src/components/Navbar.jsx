import React from 'react';
import { useNavigate } from 'react-router-dom';
import { logout } from '../services/api';

const styles = {
  nav: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '0 20px',
    height: '52px',
    background: 'var(--surface)',
    borderBottom: '1px solid var(--border)',
    flexShrink: 0,
  },
  left: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
  },
  logo: {
    fontFamily: 'var(--mono)',
    fontSize: '0.95rem',
    fontWeight: 600,
    color: 'var(--accent)',
    letterSpacing: '0.08em',
  },
  dot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    background: 'var(--accent)',
    boxShadow: '0 0 6px var(--accent)',
    animation: 'pulse 2s infinite',
  },
  status: {
    fontSize: '0.72rem',
    fontFamily: 'var(--mono)',
    color: 'var(--text-muted)',
  },
  logoutBtn: {
    background: 'transparent',
    border: '1px solid var(--border)',
    borderRadius: '5px',
    color: 'var(--text-muted)',
    padding: '5px 14px',
    fontSize: '0.78rem',
    fontFamily: 'var(--mono)',
    cursor: 'pointer',
    letterSpacing: '0.05em',
    transition: 'color 0.15s, border-color 0.15s',
  },
};

export default function Navbar() {
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await logout();
    } finally {
      navigate('/login');
    }
  };

  return (
    <nav style={styles.nav}>
      <div style={styles.left}>
        <span style={styles.logo}>STOCK_AGENT</span>
        <div style={styles.dot} />
        <span style={styles.status}>LIVE</span>
      </div>
      <button style={styles.logoutBtn} onClick={handleLogout}>
        LOGOUT
      </button>
    </nav>
  );
}
