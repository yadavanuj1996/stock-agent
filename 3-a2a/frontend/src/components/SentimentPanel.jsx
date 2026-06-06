import React from 'react';

const sentimentColor = {
  Bullish: '#00ff88',
  Bearish: '#ff4444',
  Neutral: '#ffaa00'
};

const confidenceColor = {
  High: '#00ff88',
  Medium: '#ffaa00',
  Low: '#ff4444'
};

export default function SentimentPanel({ sentiment }) {
  if (!sentiment) return null;

  return (
    <div style={{
      background: '#111118',
      border: '1px solid #1e1e2e',
      borderRadius: '8px',
      padding: '16px',
      marginTop: '16px'
    }}>
      <h6 style={{ color: '#64748b', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
        Social Sentiment — StockTwits
      </h6>

      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
        <span style={{
          background: (sentimentColor[sentiment.overall] || '#ffaa00') + '22',
          color: sentimentColor[sentiment.overall] || '#ffaa00',
          border: `1px solid ${sentimentColor[sentiment.overall] || '#ffaa00'}`,
          borderRadius: '4px',
          padding: '4px 12px',
          fontFamily: 'IBM Plex Mono, monospace',
          fontWeight: '500',
          fontSize: '14px'
        }}>
          {sentiment.overall}
        </span>
        <span style={{ color: confidenceColor[sentiment.confidence] || '#ffaa00', fontSize: '12px' }}>
          {sentiment.confidence} confidence
        </span>
      </div>

      <div style={{ display: 'flex', gap: '16px', marginBottom: '12px' }}>
        <span style={{ color: '#00ff88', fontSize: '12px' }}>
          ▲ {sentiment.bullish_count} Bullish
        </span>
        <span style={{ color: '#ff4444', fontSize: '12px' }}>
          ▼ {sentiment.bearish_count} Bearish
        </span>
        <span style={{ color: '#64748b', fontSize: '12px' }}>
          — {sentiment.neutral_count} Neutral
        </span>
      </div>

      {sentiment.themes && sentiment.themes.length > 0 && (
        <div>
          <p style={{ color: '#64748b', fontSize: '11px', marginBottom: '6px' }}>KEY THEMES</p>
          {sentiment.themes.map((theme, i) => (
            <div key={i} style={{
              color: '#e2e8f0',
              fontSize: '12px',
              padding: '4px 0',
              borderBottom: '1px solid #1e1e2e'
            }}>
              → {theme}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
