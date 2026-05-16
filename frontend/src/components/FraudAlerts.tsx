import { useState, useEffect } from 'react'
import { api } from '../api'

export default function FraudAlerts() {
  const [alerts, setAlerts] = useState<any[]>([])

  useEffect(() => {
    fetch('/api/v1/fraud/alerts').then(r => r.json()).then(setAlerts).catch(() => {})
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>🚨</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Fraud Alerts</h2>
        <span className="status-dot red" style={{ marginLeft: 8 }} />
        <span style={{ fontSize: 13, color: 'var(--text2)' }}>{alerts.length} active</span>
      </div>
      {alerts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>No alerts</div>
      ) : (
        alerts.map((a, i) => (
          <div key={i} className="card" style={{ borderLeft: `4px solid ${a.risk_score > 0.6 ? 'var(--red)' : a.risk_score > 0.3 ? 'var(--yellow)' : 'var(--green)'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{a.transaction_id}</span>
              <span style={{ fontWeight: 700, color: a.risk_score > 0.6 ? 'var(--red)' : 'var(--yellow)' }}>{(a.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text2)' }}>Decision: <b>{a.decision}</b> &bull; Rules: {a.rules?.join(', ') || 'none'}</div>
          </div>
        ))
      )}
    </div>
  )
}
