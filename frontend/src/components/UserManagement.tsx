import { useState } from 'react'

export default function UserManagement() {
  const [users] = useState<any[]>([])

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>👥</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>User Management</h2>
        <span style={{ fontSize: 13, color: 'var(--text2)', marginLeft: 'auto' }}>{users.length} users</span>
      </div>
      <div className="card" style={{ textAlign: 'center', padding: 40, color: 'var(--text2)' }}>
        User management dashboard — manage users, roles, and permissions.
        <div style={{ marginTop: 16, display: 'flex', gap: 12, justifyContent: 'center' }}>
          <button className="btn btn-primary" style={{ padding: '8px 20px' }}>➕ Add User</button>
          <button className="btn btn-secondary" style={{ padding: '8px 20px' }}>🔄 Refresh</button>
        </div>
      </div>
    </div>
  )
}
