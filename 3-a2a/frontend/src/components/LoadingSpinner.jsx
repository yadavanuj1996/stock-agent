import React from 'react';

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '16px',
    padding: '48px 24px',
  },
  dots: {
    display: 'flex',
    gap: '8px',
  },
  dot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: 'var(--accent)',
  },
  label: {
    fontFamily: 'var(--mono)',
    fontSize: '0.82rem',
    color: 'var(--text-muted)',
    letterSpacing: '0.1em',
  },
  stages: {
    fontSize: '0.75rem',
    color: 'var(--text-muted)',
    fontFamily: 'var(--mono)',
    textAlign: 'center',
    lineHeight: 2,
    opacity: 0.7,
  },
};

export default function LoadingSpinner({ ticker }) {
  return (
    <div style={styles.container}>
      <div style={styles.dots}>
        {[0, 1, 2].map(i => (
          <div
            key={i}
            style={{
              ...styles.dot,
              animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
            }}
          />
        ))}
      </div>
      <div style={styles.label}>
        AGENTS RUNNING{ticker ? ` · ${ticker}` : ''}
      </div>
      <div style={styles.stages}>
        Researcher → fetching price, fundamentals, news<br />
        Analyst → technical analysis + charts<br />
        Orchestrator → compiling report
      </div>
    </div>
  );
}
