import { useState, useEffect, useCallback } from 'react'
import { api, PredictionLog, PredictionLogSummary } from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const COLORS = ['#22c55e', '#eab308', '#ef4444']

export default function LogsView() {
  const [logs, setLogs] = useState<PredictionLogSummary[]>([])
  const [selected, setSelected] = useState<PredictionLog | null>(null)
  const [searchId, setSearchId] = useState('')
  const [loading, setLoading] = useState(false)
  const [fetchingLog, setFetchingLog] = useState(false)

  const fetchLogs = useCallback(async () => {
    try { setLogs(await api.predictionLogs(15)) } catch { }
  }, [])

  useEffect(() => { fetchLogs() }, [fetchLogs])

  const handleSearch = async () => {
    if (!searchId.trim()) return
    setFetchingLog(true)
    try {
      setSelected(await api.predictionLog(searchId.trim()))
    } catch {
      alert('Log not found')
    } finally { setFetchingLog(false) }
  }

  const selectLog = async (txId: string) => {
    setFetchingLog(true)
    try { setSelected(await api.predictionLog(txId)) } catch { }
    finally { setFetchingLog(false) }
  }

  const impData = selected?.global_feature_importance
    ? [...selected.global_feature_importance].sort((a, b) => b.importance - a.importance)
    : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div className="card" style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
        <h2 style={{ fontSize: 18, fontWeight: 600, whiteSpace: 'nowrap' }}>🔍 Prediction Logs</h2>
        <div style={{ flex: 1 }} />
        <input
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search by transaction ID..."
          style={{ flex: 1, maxWidth: 320 }}
        />
        <button onClick={handleSearch} disabled={fetchingLog} className="btn btn-primary" style={{ padding: '8px 20px' }}>
          {fetchingLog ? '...' : 'Search'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: selected ? '320px 1fr' : '1fr', gap: 20 }}>
        <div className="card" style={{ maxHeight: 500, overflowY: 'auto' }}>
          <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Recent Predictions</h3>
          {logs.length === 0 ? (
            <p style={{ color: 'var(--text2)', fontSize: 13, textAlign: 'center', padding: 20 }}>No predictions yet</p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {logs.map((log) => (
                <div
                  key={log.transaction_id}
                  onClick={() => selectLog(log.transaction_id)}
                  className={selected?.transaction_id === log.transaction_id ? 'glow' : ''}
                  style={{
                    padding: '10px 12px', borderRadius: 8, cursor: 'pointer', fontSize: 12,
                    background: selected?.transaction_id === log.transaction_id ? 'var(--surface2)' : 'transparent',
                    border: '1px solid var(--border)', transition: 'all 0.2s',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
                    <span style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>{log.transaction_id}</span>
                    <span style={{
                      color: log.is_fraudulent ? 'var(--red)' : log.fraud_probability > 0.2 ? 'var(--yellow)' : 'var(--green)',
                      fontWeight: 700,
                    }}>
                      {(log.fraud_probability * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text2)', fontSize: 10 }}>
                    <span>{log.created_at ? new Date(log.created_at).toLocaleString() : ''}</span>
                    <span>{log.is_fraudulent ? 'Fraud' : log.has_detail ? 'Detail available' : 'No detail'}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {selected && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
            <div className="card fade-in">
              <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text2)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Decision Pipeline</h3>
              <div style={{ display: 'flex', alignItems: 'center', gap: 0, justifyContent: 'space-between' }}>
                {[
                  { icon: '📥', label: 'Input', desc: `${Object.keys(selected.input_raw).length} fields` },
                  { icon: '🔢', label: 'Encode', desc: `${selected.encoded_type} → ${selected.encoded_type_value}` },
                  { icon: '⚖️', label: 'Scale', desc: `${selected.features.length} features` },
                  { icon: '🌲', label: 'Forest', desc: `${selected.tree_votes_legit + selected.tree_votes_fraud} trees` },
                  { icon: '✅', label: 'Result', desc: selected.is_fraudulent ? 'Fraud' : 'Legit' },
                ].map((step, i) => (
                  <div key={step.label} style={{ display: 'flex', alignItems: 'center', gap: 0, flex: 1 }}>
                    <div style={{
                      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6, padding: '12px 8px',
                      borderRadius: 10, background: 'var(--surface2)', minWidth: 80, flex: 1,
                      border: i === 4 ? `2px solid ${selected.is_fraudulent ? 'var(--red)' : 'var(--green)'}` : '2px solid transparent',
                    }}>
                      <span style={{ fontSize: 22 }}>{step.icon}</span>
                      <span style={{ fontSize: 11, fontWeight: 700 }}>{step.label}</span>
                      <span style={{ fontSize: 9, color: 'var(--text2)', textAlign: 'center' }}>{step.desc}</span>
                    </div>
                    {i < 4 && <div style={{ width: 20, height: 2, background: 'var(--border)', margin: '0 4px' }} />}
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div className="card fade-in">
                <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>🌲 Tree Votes</h4>
                <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                  <div style={{ position: 'relative', width: 80, height: 80 }}>
                    <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--surface2)" strokeWidth="3" />
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke={selected.is_fraudulent ? 'var(--red)' : 'var(--green)'} strokeWidth="3" strokeDasharray={`${((selected.tree_votes_fraud / (selected.tree_votes_legit + selected.tree_votes_fraud)) * 100).toFixed(0)}, 100`} />
                    </svg>
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: 16, fontWeight: 800 }}>
                      {selected.tree_votes_fraud}/{selected.tree_votes_legit + selected.tree_votes_fraud}
                    </div>
                  </div>
                  <div style={{ fontSize: 12 }}>
                    <div><span style={{ color: 'var(--red)', fontWeight: 700 }}>{selected.tree_votes_fraud}</span> trees voted <b>Fraud</b></div>
                    <div><span style={{ color: 'var(--green)', fontWeight: 700 }}>{selected.tree_votes_legit}</span> trees voted <b>Legit</b></div>
                    <div style={{ marginTop: 8, fontSize: 10, color: 'var(--text2)' }}>Model: {selected.model_version}</div>
                  </div>
                </div>
              </div>

              <div className="card fade-in">
                <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>📊 Risk Score</h4>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <div style={{ position: 'relative', width: 80, height: 80 }}>
                    <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--surface2)" strokeWidth="3" />
                      <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke={selected.is_fraudulent ? 'var(--red)' : selected.fraud_probability > 0.2 ? 'var(--yellow)' : 'var(--green)'} strokeWidth="3" strokeDasharray={`${(selected.fraud_probability * 100).toFixed(0)}, 100`} />
                    </svg>
                    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: 20, fontWeight: 800, color: selected.is_fraudulent ? 'var(--red)' : selected.fraud_probability > 0.2 ? 'var(--yellow)' : 'var(--green)' }}>
                      {(selected.fraud_probability * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: 22, fontWeight: 700, color: selected.is_fraudulent ? 'var(--red)' : 'var(--green)' }}>
                      {selected.is_fraudulent ? 'Fraudulent' : 'Legitimate'}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--text2)', marginTop: 4 }}>
                      Threshold: 50% &bull; {selected.tree_votes_fraud}/{selected.tree_votes_legit + selected.tree_votes_fraud} trees
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="card fade-in">
              <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>⚙️ Feature Details (Raw → Scaled)</h4>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                      <th style={{ textAlign: 'left', padding: '8px 12px', color: 'var(--text2)', fontWeight: 600 }}>Feature</th>
                      <th style={{ textAlign: 'right', padding: '8px 12px', color: 'var(--text2)', fontWeight: 600 }}>Raw Value</th>
                      <th style={{ textAlign: 'right', padding: '8px 12px', color: 'var(--text2)', fontWeight: 600 }}>Scaled Value</th>
                      <th style={{ textAlign: 'right', padding: '8px 12px', color: 'var(--text2)', fontWeight: 600 }}>Global Importance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selected.features.map((f) => {
                      const imp = selected.global_feature_importance.find((g) => g.feature === f.name)
                      const barW = imp ? (imp.importance * 100).toFixed(1) : '0'
                      return (
                        <tr key={f.name} style={{ borderBottom: '1px solid var(--border)' }}>
                          <td style={{ padding: '8px 12px', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>{f.name}</td>
                          <td style={{ padding: '8px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace' }}>{f.raw_value.toLocaleString()}</td>
                          <td style={{ padding: '8px 12px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', color: 'var(--accent)' }}>{f.scaled_value.toFixed(4)}</td>
                          <td style={{ padding: '8px 12px', textAlign: 'right' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 8 }}>
                              <div style={{ width: 80, height: 6, background: 'var(--surface2)', borderRadius: 3, overflow: 'hidden' }}>
                                <div style={{ width: `${barW}%`, height: '100%', background: 'var(--accent)', borderRadius: 3, transition: 'width 0.5s' }} />
                              </div>
                              <span style={{ fontSize: 10, color: 'var(--text2)', minWidth: 30, textAlign: 'right' }}>{barW}%</span>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="card fade-in">
              <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>🏆 Feature Importance (Global Model)</h4>
              <ResponsiveContainer width="100%" height={Math.max(impData.length * 40, 120)}>
                <BarChart data={impData} layout="vertical" margin={{ left: 100, right: 40, top: 0, bottom: 0 }}>
                  <XAxis type="number" domain={[0, (Math.max(...impData.map((d) => d.importance)) * 1.2).toFixed(4)]} tick={{ fontSize: 10, fill: 'var(--text2)' }} />
                  <YAxis type="category" dataKey="feature" tick={{ fontSize: 11, fill: 'var(--text2)' }} width={90} />
                  <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} formatter={(v: number) => [(v * 100).toFixed(1) + '%']} />
                  <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
                    {impData.map((_, i) => (
                      <rect key={i} fill={COLORS[i % 3]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card fade-in">
              <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>📋 Raw Input</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 8 }}>
                {Object.entries(selected.input_raw).map(([k, v]) => (
                  <div key={k} style={{ padding: '8px 12px', background: 'var(--surface2)', borderRadius: 6, fontSize: 12 }}>
                    <div style={{ color: 'var(--text2)', fontSize: 10, marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.3px' }}>{k}</div>
                    <div style={{ fontWeight: 600, fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>{String(v)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}