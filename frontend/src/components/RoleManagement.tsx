const ROLES = [
  { name: 'Admin', icon: '🛡', description: 'Full system access', color: '#ef4444' },
  { name: 'Fraud Analyst', icon: '🔍', description: 'View alerts, freeze accounts', color: '#f59e0b' },
  { name: 'Data Scientist', icon: '🧪', description: 'Train/retrain models', color: '#3b82f6' },
  { name: 'ML Engineer', icon: '⚙', description: 'Deploy models', color: '#8b5cf6' },
  { name: 'Auditor', icon: '📋', description: 'Read-only access', color: '#22c55e' },
  { name: 'SOC Team', icon: '🛡', description: 'Security investigations', color: '#ec4899' },
]

export default function RoleManagement() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div className="card" style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>🔐</span>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Role Management</h2>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 16 }}>
        {ROLES.map((role) => (
          <div key={role.name} className="card slide-up" style={{ borderTop: `3px solid ${role.color}` }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>{role.icon}</div>
            <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 4 }}>{role.name}</div>
            <div style={{ fontSize: 12, color: 'var(--text2)' }}>{role.description}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
