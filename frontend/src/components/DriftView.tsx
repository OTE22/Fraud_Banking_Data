import { useEffect, useState, useCallback } from 'react'
import { api, DriftReport } from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

export default function DriftView() {
  const [report, setReport] = useState<DriftReport | null>(null)
  const [loading, setLoading] = useState(false)

  const fetch = useCallback(async () => {
    setLoading(true)
    try { setReport(await api.driftStatus()) } finally { setLoading(false) }
  }, [])

  const run = useCallback(async () => {
    setLoading(true)
    try { setReport(await api.runDrift()) } finally { setLoading(false) }
  }, [])

  useEffect(() => { fetch() }, [fetch])

  const barData = report?.metrics.map((m) => ({
    name: m.feature_name,
    score: +(m.drift_score * 100).toFixed(1),
    drifted: m.drifted,
  })) ?? []

  const barColors = (score: number) => score > 15 ? 'var(--red)' : score > 5 ? 'var(--yellow)' : 'var(--green)'

  const driftLevel = report
    ? report.drift_percentage > 15 ? '🔴 Critical' : report.drift_percentage > 5 ? '🟡 Warning' : '🟢 Normal'
    : '⚪ Unknown'

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: 16 }}>
        <div className="card slide-up" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>{driftLevel.split(' ')[0]}</div>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{report ? `${report.drift_percentage}%` : '—'}</div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 4 }}>Overall Drift</div>
        </div>
        <div className="card slide-up" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>📊</div>
          <div style={{ fontSize: 28, fontWeight: 700 }}>{report ? `${report.drifted_features}/${report.total_features}` : '—'}</div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 4 }}>Drifted Features</div>
        </div>
        <div className="card slide-up" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>🕐</div>
          <div style={{ fontSize: 16, fontWeight: 600, fontFamily: '"JetBrains Mono", monospace' }}>{report ? new Date(report.timestamp).toLocaleTimeString() : '—'}</div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 4 }}>Last Check</div>
        </div>
        <div className="card slide-up" style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>{driftLevel}</div>
          <div style={{ fontSize: 14, fontWeight: 600 }}>{driftLevel}</div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 4 }}>Status</div>
        </div>
      </div>

      {report && barData.length > 0 && (
        <div className="card">
          <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text2)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Feature Drift Scores
          </h3>
          <ResponsiveContainer width="100%" height={Math.max(200, barData.length * 40)}>
            <BarChart data={barData} layout="vertical" margin={{ left: 100, right: 40 }}>
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11, fill: 'var(--text2)' }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11, fill: 'var(--text2)' }} width={90} />
              <Tooltip
                contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }}
                formatter={(v: number) => [`${v.toFixed(1)}%`, 'Drift Score']}
              />
              <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                {barData.map((entry, i) => (
                  <Cell key={i} fill={barColors(entry.score)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="card">
        <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text2)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Feature Details</h3>
        {report && report.metrics.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Feature</th>
                <th>Drift Score</th>
                <th>Drifted</th>
                <th>Test</th>
              </tr>
            </thead>
            <tbody>
              {report.metrics.map((m) => (
                <tr key={m.feature_name}>
                  <td style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 13 }}>{m.feature_name}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ flex: 1, height: 6, background: 'var(--surface2)', borderRadius: 3, maxWidth: 100 }}>
                        <div style={{ width: `${Math.min(m.drift_score * 100, 100)}%`, height: '100%', background: barColors(m.drift_score * 100), borderRadius: 3, transition: 'width 0.5s' }} />
                      </div>
                      {(m.drift_score * 100).toFixed(1)}%
                    </div>
                  </td>
                  <td>
                    <span className={`status-dot ${m.drifted ? 'red' : 'green'}`} />
                    {m.drifted ? 'Yes' : 'No'}
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--text2)' }}>{m.test_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p style={{ color: 'var(--text2)', textAlign: 'center', padding: 20 }}>
            {loading ? 'Loading...' : 'No drift data available. Click "Run Drift Check" to start.'}
          </p>
        )}
      </div>

      <div style={{ display: 'flex', gap: 10, justifyContent: 'center' }}>
        <button onClick={fetch} disabled={loading} className="btn btn-secondary">
          🔄 Refresh
        </button>
        <button onClick={run} disabled={loading} className="btn btn-primary">
          {loading ? '⏳ Running...' : '🚀 Run Drift Check'}
        </button>
      </div>
    </div>
  )
}
