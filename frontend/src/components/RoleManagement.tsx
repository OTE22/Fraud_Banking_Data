import { useState, useEffect } from 'react'

const API = window.location.origin.includes('3000') ? 'http://localhost:8000' : ''

const ROLE_COLORS: Record<string, string> = {
  admin: '#ef4444', fraud_analyst: '#f59e0b', data_scientist: '#3b82f6',
  ml_engineer: '#8b5cf6', auditor: '#22c55e', soc_team: '#ec4899',
}
const ROLE_ICONS: Record<string, string> = {
  admin: '🛡', fraud_analyst: '🔍', data_scientist: '🧪',
  ml_engineer: '⚙', auditor: '📋', soc_team: '🛡',
}

export default function RoleManagement({ isAdmin, token }: { isAdmin?: boolean; token: string | null }) {
  const [roles, setRoles] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!token) return
    setLoading(true)
    fetch(`${API}/api/v1/admin/roles`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.ok ? r.json() : [])
      .then(setRoles)
      .finally(() => setLoading(false))
  }, [token])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>🔐</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Role Management</h2>
        <span style={{ fontSize: 13, color: 'var(--text2)', marginLeft: 'auto' }}>{roles.length} roles</span>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
        {roles.map((role) => (
          <div key={role.name} className="card slide-up" style={{ borderTop: `3px solid ${ROLE_COLORS[role.name] || '#666'}` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
              <span style={{ fontSize: 28 }}>{ROLE_ICONS[role.name] || '🔑'}</span>
              <div>
                <div style={{ fontSize: 15, fontWeight: 600, textTransform: 'capitalize' }}>{role.name.replace('_', ' ')}</div>
                <div style={{ fontSize: 12, color: 'var(--text2)' }}>{role.description || 'No description'}</div>
              </div>
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
              {(role.permissions || []).map((p: string) => (
                <span key={p} style={{ padding: '2px 6px', borderRadius: 4, fontSize: 11, background: 'rgba(59,130,246,0.1)', color: '#60a5fa' }}>
                  {p}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
