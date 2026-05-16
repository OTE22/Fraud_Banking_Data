import { useEffect, useState } from 'react'
import { api, FeastInfo, FeastFeatureView } from '../api'

const DTYPE_COLORS: Record<string, string> = {
  Float32: '#3b82f6', Float64: '#3b82f6', Int32: '#8b5cf6', Int64: '#8b5cf6', Bool: '#22c55e', String: '#f59e0b',
}

export default function FeastView() {
  const [info, setInfo] = useState<FeastInfo | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expanded, setExpanded] = useState<string | null>(null)

  useEffect(() => {
    api.feastInfo()
      .then(setInfo)
      .catch((e) => setError(e.message))
  }, [])

  if (error) return <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--red)' }}>⚠ Failed to load Feast info: {error}</div>
  if (!info) return <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>Loading feature store...</div>
  if (!info.connected) return <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--red)' }}>⚠ Feast not connected: {info.error}</div>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <div className="card slide-up" style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
        <div style={{ width: 48, height: 48, borderRadius: 12, background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24 }}>🏪</div>
        <div style={{ flex: 1 }}>
          <h2 style={{ fontSize: 18, fontWeight: 700, marginBottom: 4 }}>Feast Feature Store</h2>
          <p style={{ fontSize: 13, color: 'var(--text2)' }}>Online feature serving for real-time ML predictions</p>
        </div>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <StoreBadge label="Online" value={info.online_store ?? 'N/A'} color="#ef4444" />
          <StoreBadge label="Offline" value={info.offline_store ?? 'N/A'} color="#3b82f6" />
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, padding: '6px 14px', borderRadius: 20, background: 'rgba(34,197,94,0.15)', color: '#22c55e', fontSize: 12, fontWeight: 600 }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#22c55e' }} />
            Connected
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
        <div className="card fade-in">
          <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text2)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.5px' }}>📌 Entities</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {info.entities?.map((e) => (
              <div key={e.name} style={{ padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface2)' }}>
                <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 4 }}>{e.name}</div>
                <div style={{ fontSize: 11, color: 'var(--text2)', fontFamily: 'JetBrains Mono, monospace' }}>join_keys: {e.join_keys.join(', ')}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="card fade-in">
          <h3 style={{ fontSize: 13, fontWeight: 600, color: 'var(--text2)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.5px' }}>📤 Push Sources</h3>
          {info.push_sources?.length ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {info.push_sources.map((ps) => (
                <div key={ps.name} style={{ padding: '12px 14px', borderRadius: 8, border: '1px solid var(--border)', background: 'var(--surface2)', display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{ fontSize: 18 }}>🔌</span>
                  <span style={{ fontSize: 13, fontWeight: 600, fontFamily: 'JetBrains Mono, monospace' }}>{ps.name}</span>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text2)', fontSize: 13 }}>No push sources configured</p>
          )}
        </div>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 700, marginTop: 8 }}>Feature Views</h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {info.feature_views?.map((fv) => (
          <FeatureViewCard key={fv.name} fv={fv} expanded={expanded === fv.name} onToggle={() => setExpanded(expanded === fv.name ? null : fv.name)} />
        ))}
      </div>
    </div>
  )
}

function StoreBadge({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
      <span style={{ fontSize: 10, color: 'var(--text2)', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</span>
      <span style={{ fontSize: 13, fontWeight: 700, color, fontFamily: 'JetBrains Mono, monospace' }}>{value}</span>
    </div>
  )
}

function FeatureViewCard({ fv, expanded, onToggle }: { fv: FeastFeatureView; expanded: boolean; onToggle: () => void }) {
  return (
    <div className={`card ${expanded ? 'glow' : ''}`} style={{ padding: 0, overflow: 'hidden', transition: 'all 0.3s' }}>
      <div onClick={onToggle} style={{ padding: '16px 20px', display: 'flex', alignItems: 'center', gap: 16, cursor: 'pointer', userSelect: 'none' }}>
        <div style={{ width: 40, height: 40, borderRadius: 10, background: 'linear-gradient(135deg, var(--accent), var(--accent2))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18 }}>📋</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 15, fontWeight: 600 }}>{fv.name}</div>
          <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 2 }}>{fv.fields.length} fields &bull; TTL: {fv.ttl} &bull; {fv.row_count?.toLocaleString() ?? '?'} rows</div>
        </div>
        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
          {fv.fields.map((f) => (
            <span key={f.name} style={{
              padding: '2px 8px', borderRadius: 4, fontSize: 10, fontWeight: 600,
              background: `${DTYPE_COLORS[f.dtype] || '#888'}20`, color: DTYPE_COLORS[f.dtype] || '#888',
              fontFamily: 'JetBrains Mono, monospace',
            }}>{f.dtype}</span>
          ))}
        </div>
        <span style={{ fontSize: 12, color: 'var(--text2)', transform: expanded ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }}>▼</span>
      </div>
      {expanded && (
        <div className="fade-in" style={{ borderTop: '1px solid var(--border)', padding: '16px 20px' }}>
          <div style={{ marginBottom: 14 }}>
            <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text2)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Schema</h4>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                  <th style={{ textAlign: 'left', padding: '6px 10px', color: 'var(--text2)', fontWeight: 600 }}>Field</th>
                  <th style={{ textAlign: 'left', padding: '6px 10px', color: 'var(--text2)', fontWeight: 600 }}>Type</th>
                  <th style={{ textAlign: 'right', padding: '6px 10px', color: 'var(--text2)', fontWeight: 600 }}>Count</th>
                  <th style={{ textAlign: 'right', padding: '6px 10px', color: 'var(--text2)', fontWeight: 600 }}>Min</th>
                  <th style={{ textAlign: 'right', padding: '6px 10px', color: 'var(--text2)', fontWeight: 600 }}>Max</th>
                  <th style={{ textAlign: 'right', padding: '6px 10px', color: 'var(--text2)', fontWeight: 600 }}>Mean</th>
                  <th style={{ textAlign: 'right', padding: '6px 10px', color: 'var(--text2)', fontWeight: 600 }}>Nulls</th>
                </tr>
              </thead>
              <tbody>
                {fv.fields.map((f) => {
                  const s = fv.stats?.[f.name]
                  return (
                    <tr key={f.name} style={{ borderBottom: '1px solid var(--border)' }}>
                      <td style={{ padding: '6px 10px', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>{f.name}</td>
                      <td style={{ padding: '6px 10px' }}>
                        <span style={{
                          padding: '1px 6px', borderRadius: 3, fontSize: 10, fontWeight: 600,
                          background: `${DTYPE_COLORS[f.dtype] || '#888'}20`, color: DTYPE_COLORS[f.dtype] || '#888',
                        }}>{f.dtype}</span>
                      </td>
                      <td style={{ padding: '6px 10px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace' }}>{s?.count?.toLocaleString() ?? '-'}</td>
                      <td style={{ padding: '6px 10px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace' }}>{s?.min != null ? s.min.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}</td>
                      <td style={{ padding: '6px 10px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace' }}>{s?.max != null ? s.max.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}</td>
                      <td style={{ padding: '6px 10px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace' }}>{s?.mean != null ? s.mean.toLocaleString(undefined, { maximumFractionDigits: 2 }) : '-'}</td>
                      <td style={{ padding: '6px 10px', textAlign: 'right', fontFamily: 'JetBrains Mono, monospace', color: (s?.nulls ?? 0) > 0 ? 'var(--red)' : 'var(--text2)' }}>{s?.nulls ?? '-'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          {fv.entities.length > 0 && (
            <div>
              <h4 style={{ fontSize: 12, fontWeight: 600, color: 'var(--text2)', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Entities</h4>
              <div style={{ display: 'flex', gap: 8 }}>
                {fv.entities.map((e) => (
                  <span key={e} style={{ padding: '4px 12px', borderRadius: 6, background: 'var(--surface2)', fontSize: 12, fontFamily: 'JetBrains Mono, monospace' }}>{e}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}