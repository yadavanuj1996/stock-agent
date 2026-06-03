import React from 'react';

function extractRecommendation(text) {
  const upper = text.toUpperCase();
  if (/STRONG\s+BUY/.test(upper)) return 'STRONG BUY';
  if (/STRONG\s+SELL/.test(upper)) return 'STRONG SELL';
  if (/\bBUY\b/.test(upper)) return 'BUY';
  if (/\bSELL\b/.test(upper)) return 'SELL';
  if (/\bHOLD\b/.test(upper)) return 'HOLD';
  return 'NEUTRAL';
}

const recColor = {
  'STRONG BUY': 'var(--accent)',
  BUY: 'var(--accent)',
  HOLD: 'var(--amber)',
  SELL: 'var(--red)',
  'STRONG SELL': 'var(--red)',
  NEUTRAL: 'var(--text-muted)',
};

function parseBold(text) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) =>
    part.startsWith('**') && part.endsWith('**')
      ? <strong key={i} style={{ color: 'var(--text)', fontWeight: 600 }}>{part.slice(2, -2)}</strong>
      : part
  );
}

function renderMarkdown(text) {
  const lines = text.split('\n');
  const elements = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith('### ')) {
      elements.push(
        <h3 key={i} style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text)', margin: '14px 0 6px', fontFamily: 'var(--mono)' }}>
          {parseBold(line.slice(4))}
        </h3>
      );
    } else if (line.startsWith('## ')) {
      elements.push(
        <h2 key={i} style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent)', margin: '20px 0 8px', fontFamily: 'var(--mono)', letterSpacing: '0.04em' }}>
          {parseBold(line.slice(3))}
        </h2>
      );
    } else if (line.startsWith('# ')) {
      elements.push(
        <h1 key={i} style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)', margin: '20px 0 10px', fontFamily: 'var(--mono)' }}>
          {parseBold(line.slice(2))}
        </h1>
      );
    } else if (line.match(/^[-*] /)) {
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '4px', paddingLeft: '4px' }}>
          <span style={{ color: 'var(--accent)', flexShrink: 0, marginTop: '1px' }}>▸</span>
          <span>{parseBold(line.slice(2))}</span>
        </div>
      );
    } else if (line.match(/^\d+\. /)) {
      const content = line.replace(/^\d+\. /, '');
      elements.push(
        <div key={i} style={{ display: 'flex', gap: '8px', marginBottom: '4px', paddingLeft: '4px' }}>
          <span style={{ color: 'var(--text-muted)', flexShrink: 0, fontFamily: 'var(--mono)', fontSize: '0.8rem' }}>{line.match(/^\d+/)[0]}.</span>
          <span>{parseBold(content)}</span>
        </div>
      );
    } else if (line.trim() === '' || line.trim() === '---') {
      elements.push(<div key={i} style={{ height: '10px' }} />);
    } else {
      elements.push(
        <p key={i} style={{ margin: '0 0 8px', lineHeight: 1.8 }}>
          {parseBold(line)}
        </p>
      );
    }

    i++;
  }

  return elements;
}

const styles = {
  panel: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    overflow: 'hidden',
  },
  header: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '14px 18px',
    borderBottom: '1px solid var(--border)',
    background: 'var(--surface-2)',
  },
  ticker: {
    fontFamily: 'var(--mono)',
    fontSize: '1.1rem',
    fontWeight: 700,
    color: 'var(--text)',
    letterSpacing: '0.05em',
  },
  recBadge: (rec) => ({
    fontFamily: 'var(--mono)',
    fontSize: '0.72rem',
    fontWeight: 700,
    letterSpacing: '0.12em',
    padding: '4px 10px',
    borderRadius: '4px',
    border: `1px solid ${recColor[rec] || 'var(--border)'}`,
    color: recColor[rec] || 'var(--text-muted)',
    background: `${recColor[rec]}22` || 'transparent',
  }),
  body: {
    padding: '18px 20px',
    fontSize: '0.85rem',
    lineHeight: 1.8,
    color: 'var(--text)',
  },
};

export default function AnalysisPanel({ ticker, response }) {
  if (!response) return null;

  const rec = extractRecommendation(response);

  return (
    <div style={styles.panel} className="fade-in">
      <div style={styles.header}>
        <span style={styles.ticker}>{ticker}</span>
        <span style={styles.recBadge(rec)}>{rec}</span>
      </div>
      <div style={styles.body}>
        {renderMarkdown(response)}
      </div>
    </div>
  );
}
