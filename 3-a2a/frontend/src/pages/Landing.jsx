import React from 'react';
import { useNavigate } from 'react-router-dom';

const styles = {
  page: {
    minHeight: '100vh',
    background: 'var(--bg)',
    display: 'flex',
    flexDirection: 'column',
  },
  nav: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 48px',
    borderBottom: '1px solid var(--border)',
  },
  logo: {
    fontFamily: 'var(--mono)',
    fontSize: '1.1rem',
    fontWeight: 600,
    color: 'var(--accent)',
    letterSpacing: '0.05em',
  },
  navLinks: {
    display: 'flex',
    gap: '16px',
    alignItems: 'center',
  },
  hero: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    textAlign: 'center',
    padding: '80px 24px 60px',
  },
  eyebrow: {
    fontFamily: 'var(--mono)',
    fontSize: '0.75rem',
    color: 'var(--accent)',
    letterSpacing: '0.2em',
    textTransform: 'uppercase',
    marginBottom: '20px',
    opacity: 0.8,
  },
  h1: {
    fontSize: 'clamp(2rem, 5vw, 3.5rem)',
    fontWeight: 700,
    color: 'var(--text)',
    lineHeight: 1.15,
    marginBottom: '20px',
  },
  subtitle: {
    fontSize: '1.05rem',
    color: 'var(--text-muted)',
    maxWidth: '520px',
    lineHeight: 1.7,
    marginBottom: '36px',
  },
  badges: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    flexWrap: 'wrap',
    marginBottom: '44px',
  },
  badge: {
    fontFamily: 'var(--mono)',
    fontSize: '0.75rem',
    padding: '5px 14px',
    borderRadius: '4px',
    border: '1px solid var(--border)',
    color: 'var(--text-muted)',
    background: 'var(--surface)',
    letterSpacing: '0.05em',
  },
  cta: {
    display: 'flex',
    gap: '12px',
    justifyContent: 'center',
    flexWrap: 'wrap',
  },
  btnPrimary: {
    background: 'var(--accent)',
    color: '#0a0a0f',
    border: 'none',
    borderRadius: '6px',
    padding: '12px 28px',
    fontWeight: 600,
    fontSize: '0.9rem',
    cursor: 'pointer',
    letterSpacing: '0.02em',
    transition: 'opacity 0.15s',
  },
  btnGhost: {
    background: 'transparent',
    color: 'var(--text-muted)',
    border: '1px solid var(--border)',
    borderRadius: '6px',
    padding: '12px 28px',
    fontWeight: 500,
    fontSize: '0.9rem',
    cursor: 'pointer',
    textDecoration: 'none',
    display: 'inline-flex',
    alignItems: 'center',
    gap: '8px',
    transition: 'color 0.15s, border-color 0.15s',
  },
  features: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
    gap: '16px',
    maxWidth: '900px',
    margin: '0 auto',
    padding: '0 24px 80px',
    width: '100%',
  },
  featureCard: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    padding: '24px',
  },
  featureIcon: {
    fontSize: '1.4rem',
    marginBottom: '12px',
  },
  featureTitle: {
    fontFamily: 'var(--mono)',
    fontSize: '0.85rem',
    color: 'var(--text)',
    marginBottom: '8px',
    fontWeight: 600,
  },
  featureDesc: {
    fontSize: '0.82rem',
    color: 'var(--text-muted)',
    lineHeight: 1.6,
  },
  footer: {
    borderTop: '1px solid var(--border)',
    padding: '20px 48px',
    textAlign: 'center',
    fontSize: '0.78rem',
    color: 'var(--text-muted)',
    fontFamily: 'var(--mono)',
  },
};

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={styles.page}>
      <nav style={styles.nav}>
        <span style={styles.logo}>STOCK_AGENT</span>
        <div style={styles.navLinks}>
          <a
            href="https://github.com/yadavanuj1996/stock-agent"
            target="_blank"
            rel="noreferrer"
            style={{ ...styles.btnGhost, padding: '8px 16px', fontSize: '0.82rem' }}
          >
            GitHub
          </a>
          <button style={styles.btnPrimary} onClick={() => navigate('/login')}>
            Launch App
          </button>
        </div>
      </nav>

      <section style={styles.hero}>
        <p style={styles.eyebrow}>AI-Powered Stock Research</p>
        <h1 style={styles.h1}>
          Multi-Agent Stock<br />Research System
        </h1>
        <p style={styles.subtitle}>
          Type a company name. Get full technical analysis, 5 charts,
          and a buy/hold/sell recommendation — powered by LangChain,
          MCP tools, and Google A2A agents.
        </p>
        <div style={styles.badges}>
          {['LangChain DeepAgent', 'FastMCP Tools', 'Google A2A Protocol', 'GPT-4o Orchestrator'].map(b => (
            <span key={b} style={styles.badge}>{b}</span>
          ))}
        </div>
        <div style={styles.cta}>
          <button style={styles.btnPrimary} onClick={() => navigate('/login')}>
            Open Dashboard
          </button>
          <a
            href="https://github.com/yadavanuj1996/stock-agent"
            target="_blank"
            rel="noreferrer"
            style={styles.btnGhost}
          >
            View on GitHub
          </a>
        </div>
      </section>

      <section style={styles.features}>
        {[
          {
            icon: '🔍',
            title: 'Researcher Agent',
            desc: 'Fetches price history, fundamentals, and news via MCP tools on port 8050.',
          },
          {
            icon: '📊',
            title: 'Analyst Agent',
            desc: 'Runs technical analysis — MA, RSI, MACD — and generates 5 charts in a Docker sandbox.',
          },
          {
            icon: '🤖',
            title: 'GPT-4o Orchestrator',
            desc: 'Coordinates both A2A agents, compiles results, and writes the final recommendation.',
          },
          {
            icon: '⚡',
            title: 'Google A2A Protocol',
            desc: 'Agents communicate over HTTP+JSON using the official a2a-sdk v1.1.0.',
          },
        ].map(f => (
          <div key={f.title} style={styles.featureCard}>
            <div style={styles.featureIcon}>{f.icon}</div>
            <div style={styles.featureTitle}>{f.title}</div>
            <div style={styles.featureDesc}>{f.desc}</div>
          </div>
        ))}
      </section>

      <footer style={styles.footer}>
        stock-agent · LangChain · MCP · Google A2A · GPT-4o
      </footer>
    </div>
  );
}
