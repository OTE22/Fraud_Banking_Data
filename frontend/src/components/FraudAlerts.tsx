import { useState, useEffect } from 'react'
import { getToken } from '../auth'

const API = window.location.origin.includes('3000') ? 'http://localhost:8000' : ''

export default function FraudAlerts() {
  const [alerts, setAlerts] = useState<any[]>([])
  const [error, setError] = useState('')

  useEffect(() => {
    const token = getToken()
    if (!token) return
    fetch(`${API}/api/v1/fraud/alerts`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : [])
      .then(setAlerts)
      .catch(() => setError('Failed to load alerts'))
  }, [])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>🚨</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Fraud Alerts</h2>
        <span className="status-dot red" style={{ marginLeft: 8 }} />
        <span style={{ fontSize: 13, color: 'var(--text2)' }}>{alerts.length} alerts</span>
      </div>
      {error && <div style={{ color: '#ef4444', fontSize: 13 }}>{error}</div>}
      {alerts.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>No alerts</div>
      ) : (
        alerts.map((a, i) => (
          <div key={i} className="card" style={{ borderLeft: `4px solid ${a.risk_score > 0.6 ? '#ef4444' : a.risk_score > 0.3 ? '#eab308' : '#22c55e'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{a.transaction_id}</span>
              <span style={{ fontWeight: 700, color: a.risk_score > 0.6 ? '#ef4444' : '#eab308' }}>{(a.risk_score * 100).toFixed(0)}%</span>
            </div>
            <div style={{ fontSize: 12, color: 'var(--text2)' }}>
              Decision: <b style={{ color: a.decision === 'block' ? '#ef4444' : a.decision === 'review' ? '#eab308' : '#22c55e' }}>{a.decision}</b>
              &bull; Rules: {a.rules?.join(', ') || 'none'}
              {a.description && <span> &bull; {a.description}</span>}
            </div>
          </div>
        ))
      )}
    </div>
  )
}
