import { useState } from 'react'
import { setToken } from '../auth'

const API = window.location.origin.includes('3000') ? 'http://localhost:8000' : ''

export default function LoginPage({ onLogin, onSwitch }: { onLogin: () => void; onSwitch: () => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/v1/auth/login`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password }),
      })
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail || 'Login failed') }
      const data = await r.json()
      setToken(data.access_token)
      onLogin()
    } catch (err: any) {
      setError(err.message)
    } finally { setLoading(false) }
  }

  return (
    <div style={{ maxWidth: 400, margin: '80px auto' }}>
      <div className="card" style={{ padding: 32 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>🛡</div>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Fraud Detection Login</h2>
          <p style={{ fontSize: 13, color: 'var(--text2)' }}>Enterprise Banking Platform</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, display: 'block' }}>Username</label>
            <input className="input" value={username} onChange={e => setUsername(e.target.value)} required style={{ width: '100%' }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, display: 'block' }}>Password</label>
            <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%' }} />
          </div>
          {error && <div style={{ color: '#ef4444', fontSize: 13, marginBottom: 12 }}>{error}</div>}
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', padding: '10px 0' }}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text2)', marginTop: 16 }}>
          No account? <button className="btn btn-secondary" onClick={onSwitch} style={{ padding: '4px 12px', fontSize: 13 }}>Register</button>
        </p>
      </div>
    </div>
  )
}
