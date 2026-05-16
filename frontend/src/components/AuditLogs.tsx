import { useState, useEffect } from 'react'

export default function AuditLogs() {
  const [logs] = useState<any[]>([])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>📜</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Audit Logs</h2>
      </div>
      {logs.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>
          <p style={{ marginBottom: 12 }}>No audit logs yet</p>
          <p style={{ fontSize: 12 }}>Audit trail will appear as users interact with the system</p>
        </div>
      ) : (
        <div className="card">
          {logs.map((log, i) => (
            <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid var(--border)', fontSize: 12, display: 'flex', gap: 12 }}>
              <span style={{ color: 'var(--text2)', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}>{log.timestamp}</span>
              <span style={{ fontWeight: 600 }}>{log.action}</span>
              <span style={{ color: 'var(--text2)' }}>{log.resource}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
