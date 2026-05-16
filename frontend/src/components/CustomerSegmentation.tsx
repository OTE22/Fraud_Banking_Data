import { useState, useEffect } from 'react'
import { getToken } from '../auth'

const API = window.location.origin.includes('3000') ? 'http://localhost:8000' : ''

const SEG_COLORS: Record<string, string> = {
  '0': '#22c55e', '1': '#eab308', '2': '#f97316', '3': '#ef4444',
}

const SEG_LABELS: Record<string, string> = {
  '0': 'Low Risk', '1': 'Medium Risk', '2': 'High Risk', '3': 'Critical',
}

const SEG_ICONS: Record<string, string> = {
  '0': '🟢', '1': '🟡', '2': '🟠', '3': '🔴',
}

export default function CustomerSegmentation() {
  const [info, setInfo] = useState<any>(null)
  const [predicting, setPredicting] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const token = getToken()
  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

  useEffect(() => {
    fetch(`${API}/api/v1/segments/info`, { headers })
      .then(r => r.ok ? r.json() : null)
      .then(setInfo)
  }, [])

  const runSegmentation = async () => {
    setPredicting(true); setError('')
    try {
      const r = await fetch(`${API}/api/v1/segments/predict?n_clusters=4`, { method: 'POST', headers })
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail || 'Failed') }
      setResult(await r.json())
    } catch (err: any) { setError(err.message) }
    finally { setPredicting(false) }
  }

  const stats = info?.cluster_stats ? Object.entries(info.cluster_stats).map(([k, v]: [string, any]) => ({
    id: parseInt(k), label: v.label || SEG_LABELS[k] || `Cluster ${k}`,
    pct: v.pct || 0, count: v.count || 0,
  })) : []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>📊</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Customer Segmentation</h2>
        <span style={{ fontSize: 13, color: 'var(--text2)', marginLeft: 'auto' }}>
          {info?.loaded ? `${info.n_clusters} clusters` : 'Model info'}
        </span>
        <button className="btn btn-primary" onClick={runSegmentation} disabled={predicting} style={{ padding: '8px 16px' }}>
          {predicting ? 'Running...' : '▶ Run Segmentation'}
        </button>
      </div>

      {error && <div style={{ color: '#ef4444', fontSize: 13, padding: '8px 16px', background: 'rgba(239,68,68,0.1)', borderRadius: 8 }}>{error}</div>}

      {stats.length > 0 && (
        <div className="card fade-in">
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>📈 Cluster Distribution</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {stats.map((s) => (
              <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <span style={{ fontSize: 20 }}>{SEG_ICONS[String(s.id)] || '⬜'}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 4 }}>
                    <span style={{ fontWeight: 600 }}>{s.label}</span>
                    <span style={{ color: 'var(--text2)' }}>{s.count} customers ({s.pct.toFixed(1)}%)</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 4, background: 'var(--surface2)', overflow: 'hidden' }}>
                    <div style={{ width: `${s.pct}%`, height: '100%', borderRadius: 4, background: SEG_COLORS[String(s.id)] || '#888', transition: 'width 0.6s' }} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {stats.length === 0 && info?.loaded && (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>
          Model loaded. Click "Run Segmentation" to see results.
        </div>
      )}

      {!info?.loaded && (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>
          Segmentation model not loaded.
        </div>
      )}

      {result && (
        <div className="card fade-in">
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 12 }}>📋 Latest Prediction</h3>
          <div style={{ fontSize: 13, color: 'var(--text2)' }}>
            {result.labels?.length ?? 0} customers clustered into {result.n_clusters} groups
            {result.feast_enriched !== undefined && ` · Feast: ${result.feast_enriched ? '✅' : '❌'}`}
          </div>
        </div>
      )}
    </div>
  )
}
