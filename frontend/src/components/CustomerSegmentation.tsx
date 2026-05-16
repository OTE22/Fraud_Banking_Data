const SEGMENTS = [
  { id: 0, name: 'Low Risk', icon: '🟢', color: '#22c55e', desc: 'Regular customers with normal patterns' },
  { id: 1, name: 'Medium Risk', icon: '🟡', color: '#eab308', desc: 'Occasional anomalies detected' },
  { id: 2, name: 'High Risk', icon: '🟠', color: '#f97316', desc: 'Frequent fraud-adjacent behavior' },
  { id: 3, name: 'Critical', icon: '🔴', color: '#ef4444', desc: 'Confirmed fraud patterns' },
]

export default function CustomerSegmentation() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>📊</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Customer Segmentation</h2>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16 }}>
        {SEGMENTS.map((seg) => (
          <div key={seg.id} className="card scale-in" style={{ borderLeft: `4px solid ${seg.color}` }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>{seg.icon}</div>
            <div style={{ fontSize: 15, fontWeight: 600 }}>{seg.name}</div>
            <div style={{ fontSize: 12, color: 'var(--text2)', marginTop: 4 }}>{seg.desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
