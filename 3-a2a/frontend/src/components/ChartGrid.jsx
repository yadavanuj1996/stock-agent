import React, { useState } from 'react';
import { chartUrl } from '../services/api';

const styles = {
  grid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '12px',
  },
  cell: {
    background: 'var(--surface)',
    border: '1px solid var(--border)',
    borderRadius: '8px',
    overflow: 'hidden',
    cursor: 'pointer',
    transition: 'border-color 0.15s',
  },
  img: {
    width: '100%',
    display: 'block',
  },
  overlay: {
    position: 'fixed',
    inset: 0,
    background: 'rgba(0,0,0,0.85)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '24px',
    cursor: 'zoom-out',
  },
  overlayImg: {
    maxWidth: '90vw',
    maxHeight: '90vh',
    borderRadius: '8px',
    boxShadow: '0 8px 48px rgba(0,0,0,0.5)',
  },
};

export default function ChartGrid({ charts }) {
  const [enlarged, setEnlarged] = useState(null);

  if (!charts || charts.length === 0) return null;

  return (
    <>
      <div style={styles.grid}>
        {charts.map(name => (
          <div
            key={name}
            style={styles.cell}
            onClick={() => setEnlarged(name)}
            onMouseEnter={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
            onMouseLeave={e => (e.currentTarget.style.borderColor = 'var(--border)')}
          >
            <img
              src={chartUrl(name)}
              alt={name.replace(/_/g, ' ').replace('.png', '')}
              style={styles.img}
              loading="lazy"
            />
          </div>
        ))}
      </div>

      {enlarged && (
        <div style={styles.overlay} onClick={() => setEnlarged(null)}>
          <img
            src={chartUrl(enlarged)}
            alt="enlarged chart"
            style={styles.overlayImg}
          />
        </div>
      )}
    </>
  );
}
