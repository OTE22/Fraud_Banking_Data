import { useState, useEffect } from 'react'

const API = window.location.origin.includes('3000') ? 'http://localhost:8000' : ''
const ROLES = ['admin', 'fraud_analyst', 'data_scientist', 'ml_engineer', 'auditor', 'soc_team']

function RoleBadge({ role }: { role: string }) {
  const isAdmin = role === 'admin'
  return <span style={{ padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 600, background: isAdmin ? 'rgba(239,68,68,0.15)' : 'rgba(59,130,246,0.15)', color: isAdmin ? '#ef4444' : '#3b82f6' }}>{role}</span>
}

export default function UserManagement({ isAdmin, token }: { isAdmin?: boolean; token: string | null }) {
  const [users, setUsers] = useState<any[]>([])
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editRoles, setEditRoles] = useState<string[]>([])
  const [error, setError] = useState('')
  const [showAdd, setShowAdd] = useState(false)
  const [newUser, setNewUser] = useState({ username: '', email: '', password: '', roles: ['fraud_analyst'] })

  const headers = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' }

  const fetchUsers = async () => {
    if (!token) return
    const r = await fetch(`${API}/api/v1/admin/users`, { headers: { Authorization: `Bearer ${token}` } })
    if (r.ok) setUsers(await r.json())
  }

  useEffect(() => { fetchUsers() }, [token])

  const assignRole = async (userId: number) => {
    if (!token) return
    const user = users.find(u => u.id === userId)
    if (!user) return
    setError('')
    try {
      const r = await fetch(`${API}/api/v1/admin/users/${userId}/role`, {
        method: 'PUT', headers,
        body: JSON.stringify({ username: user.username, email: user.email, password: 'changeme123', roles: editRoles }),
      })
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail || 'Failed') }
      setEditingId(null); await fetchUsers()
    } catch (err: any) { setError(err.message) }
  }

  const addUser = async (e: React.FormEvent) => {
    e.preventDefault(); setError('')
    try {
      const r = await fetch(`${API}/api/v1/admin/users`, { method: 'POST', headers, body: JSON.stringify(newUser) })
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail || 'Failed') }
      setShowAdd(false); setNewUser({ username: '', email: '', password: '', roles: ['fraud_analyst'] }); await fetchUsers()
    } catch (err: any) { setError(err.message) }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>👥</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>User Management</h2>
        <span style={{ fontSize: 13, color: 'var(--text2)', marginLeft: 'auto' }}>{users.length} users</span>
        {isAdmin && <button className="btn btn-primary" onClick={() => setShowAdd(true)} style={{ padding: '8px 16px' }}>➕ Add User</button>}
        <button className="btn btn-secondary" onClick={fetchUsers} style={{ padding: '8px 16px' }}>🔄 Refresh</button>
      </div>

      {error && <div style={{ color: '#ef4444', fontSize: 13, padding: '8px 16px', background: 'rgba(239,68,68,0.1)', borderRadius: 8 }}>{error}</div>}

      {showAdd && (
        <div className="card" style={{ padding: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Create New User</h3>
          <form onSubmit={addUser} style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <input className="input" placeholder="Username" value={newUser.username} onChange={e => setNewUser({ ...newUser, username: e.target.value })} required />
              <input className="input" type="email" placeholder="Email" value={newUser.email} onChange={e => setNewUser({ ...newUser, email: e.target.value })} required />
              <input className="input" type="password" placeholder="Password (min 8 chars)" value={newUser.password} onChange={e => setNewUser({ ...newUser, password: e.target.value })} required minLength={8} />
              <select value={newUser.roles[0]} onChange={e => setNewUser({ ...newUser, roles: [e.target.value] })} className="input">
                {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', gap: 8 }}>
              <button className="btn btn-primary" type="submit">Create User</button>
              <button className="btn btn-secondary" type="button" onClick={() => setShowAdd(false)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {users.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>No users found.</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {users.map(u => (
            <div key={u.id} className="card slide-up" style={{ display: 'flex', alignItems: 'center', gap: 16, padding: '12px 20px' }}>
              <div style={{ width: 36, height: 36, borderRadius: '50%', background: u.is_active ? 'var(--accent)' : '#666', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, color: '#fff', fontWeight: 700 }}>
                {u.username[0].toUpperCase()}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: 14, fontWeight: 600 }}>{u.username}</div>
                <div style={{ fontSize: 12, color: 'var(--text2)' }}>{u.email}</div>
              </div>
              <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                {(u.roles || []).map((r: string) => <RoleBadge key={r} role={r} />)}
              </div>
              {isAdmin && editingId === u.id ? (
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <select multiple value={editRoles} onChange={e => setEditRoles(Array.from(e.target.selectedOptions, o => o.value))} style={{ height: 120, fontSize: 12 }}>
                    {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <button className="btn btn-primary" onClick={() => assignRole(u.id)} style={{ padding: '4px 12px', fontSize: 12 }}>Save</button>
                    <button className="btn btn-secondary" onClick={() => setEditingId(null)} style={{ padding: '4px 12px', fontSize: 12 }}>Cancel</button>
                  </div>
                </div>
              ) : isAdmin ? (
                <button className="btn btn-secondary" onClick={() => { setEditingId(u.id); setEditRoles(u.roles || []) }} style={{ padding: '4px 12px', fontSize: 12 }}>Assign Role</button>
              ) : null}
              <span style={{ fontSize: 11, color: u.is_active ? '#22c55e' : '#ef4444' }}>{u.is_active ? 'Active' : 'Inactive'}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
