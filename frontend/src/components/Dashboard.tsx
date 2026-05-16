import { useEffect, useState, useCallback } from 'react'
import { api, HealthStatus, PredictionHistoryItem, DriftHistoryItem } from '../api'

export default function Dashboard() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [history, setHistory] = useState<PredictionHistoryItem[]>([])
  const [driftHistory, setDriftHistory] = useState<DriftHistoryItem[]>([])
  const [error, setError] = useState<string | null>(null)

  const fetchAll = useCallback(async () => {
    try {
      const [h, preds, drifts] = await Promise.all([
        api.health(),
        api.predictionHistory(5),
        api.driftHistory(5),
      ])
      setHealth(h)
      setHistory(preds)
      setDriftHistory(drifts)
      setError(null)
    } catch (e: any) {
      setError(e.message)
    }
  }, [])

  useEffect(() => {
    fetchAll()
    const interval = setInterval(fetchAll, 10000)
    return () => clearInterval(interval)
  }, [fetchAll])

  const totalPreds = history.length
  const fraudCount = history.filter((p) => p.is_fraudulent).length
  const fraudRate = totalPreds > 0 ? ((fraudCount / totalPreds) * 100).toFixed(1) : '0.0'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
        <StatCard icon="🛡" label="API Status" value={health?.status ?? '...'} color="var(--green)" dot />
        <StatCard icon="🧠" label="Model" value={health?.model_loaded ? 'Loaded' : 'Offline'} color={health?.model_loaded ? 'var(--green)' : 'var(--red)'} />
        <StatCard icon="🗄" label="Database" value={health?.db_connected ? 'Connected' : 'Disconnected'} color={health?.db_connected ? 'var(--green)' : 'var(--red)'} />
        <StatCard icon="⚡" label="Fraud Rate (recent)" value={`${fraudRate}%`} color={+fraudRate > 5 ? 'var(--red)' : 'var(--green)'} />
      </div>

      {error && (
        <div className="card" style={{ borderColor: 'var(--red)', color: 'var(--red)', textAlign: 'center', padding: 16 }}>
          ⚠ Connection error: {error}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text2)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Recent Predictions</h3>
          {history.length === 0 ? (
            <p style={{ color: 'var(--text2)', fontSize: 13, textAlign: 'center', padding: 20 }}>No predictions yet</p>
          ) : (
            <table>
              <thead>
                <tr><th>ID</th><th>Risk</th><th>Status</th></tr>
              </thead>
              <tbody>
                {history.map((p) => (
                  <tr key={p.transaction_id}>
                    <td style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 12 }}>{p.transaction_id.slice(0, 16)}</td>
                    <td>{(p.fraud_probability * 100).toFixed(0)}%</td>
                    <td>
                      <span className={`status-dot ${p.is_fraudulent ? 'red' : 'green'}`} />
                      {p.is_fraudulent ? 'Fraud' : 'Clear'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12, color: 'var(--text2)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Drift History</h3>
          {driftHistory.length === 0 ? (
            <p style={{ color: 'var(--text2)', fontSize: 13, textAlign: 'center', padding: 20 }}>No drift checks yet</p>
          ) : (
            <table>
              <thead>
                <tr><th>Time</th><th>Drift %</th><th>Features</th></tr>
              </thead>
              <tbody>
                {driftHistory.map((d) => (
                  <tr key={d.id}>
                    <td style={{ fontSize: 12 }}>{new Date(d.created_at).toLocaleTimeString()}</td>
                    <td>
                      <span className={`status-dot ${d.drift_percentage > 10 ? 'red' : d.drift_percentage > 5 ? 'yellow' : 'green'}`} />
                      {d.drift_percentage}%
                    </td>
                    <td>{d.drifted_features} drifted</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      <div className="card" style={{ textAlign: 'center', fontSize: 13, color: 'var(--text2)' }}>
        Auto-refreshes every 10s &bull; Last check: {new Date().toLocaleTimeString()}
      </div>
    </div>
  )
}

function StatCard({ icon, label, value, color, dot }: { icon: string; label: string; value: string; color: string; dot?: boolean }) {
  return (
    <div className="card slide-up" style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
      <div style={{ fontSize: 28 }}>{icon}</div>
      <div>
        <div style={{ fontSize: 12, color: 'var(--text2)', marginBottom: 2 }}>{label}</div>
        <div style={{ fontSize: 18, fontWeight: 700, color, display: 'flex', alignItems: 'center', gap: 6 }}>
          {dot && <span className={`status-dot ${value === 'ok' ? 'green' : 'red'}`} />}
          {value}
        </div>
      </div>
    </div>
  )
}
