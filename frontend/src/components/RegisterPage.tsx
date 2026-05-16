import { useState } from 'react'

const API = window.location.origin.includes('3000') ? 'http://localhost:8000' : ''

export default function RegisterPage({ onSwitch }: { onSwitch: () => void }) {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const r = await fetch(`${API}/api/v1/auth/register`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password, roles: ['fraud_analyst'] }),
      })
      if (!r.ok) { const d = await r.json(); throw new Error(d.detail || 'Registration failed') }
      setSuccess(true)
    } catch (err: any) {
      setError(err.message)
    } finally { setLoading(false) }
  }

  if (success) {
    return (
      <div style={{ maxWidth: 400, margin: '80px auto' }}>
        <div className="card" style={{ padding: 32, textAlign: 'center' }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>✅</div>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Registration Successful</h2>
          <p style={{ fontSize: 13, color: 'var(--text2)', margin: '12px 0' }}>Your account has been created. You can now log in.</p>
          <button className="btn btn-primary" onClick={onSwitch} style={{ padding: '8px 24px' }}>Go to Login</button>
        </div>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 400, margin: '80px auto' }}>
      <div className="card" style={{ padding: 32 }}>
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <div style={{ fontSize: 48, marginBottom: 8 }}>📝</div>
          <h2 style={{ fontSize: 20, fontWeight: 700 }}>Create Account</h2>
          <p style={{ fontSize: 13, color: 'var(--text2)' }}>Register for fraud detection platform access</p>
        </div>
        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, display: 'block' }}>Username</label>
            <input className="input" value={username} onChange={e => setUsername(e.target.value)} required minLength={3} style={{ width: '100%' }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, display: 'block' }}>Email</label>
            <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} required style={{ width: '100%' }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 13, fontWeight: 600, marginBottom: 4, display: 'block' }}>Password</label>
            <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={8} style={{ width: '100%' }} />
            <p style={{ fontSize: 11, color: 'var(--text2)', marginTop: 4 }}>Minimum 8 characters</p>
          </div>
          {error && <div style={{ color: '#ef4444', fontSize: 13, marginBottom: 12 }}>{error}</div>}
          <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: '100%', padding: '10px 0' }}>
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>
        <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text2)', marginTop: 16 }}>
          Already have an account? <button className="btn btn-secondary" onClick={onSwitch} style={{ padding: '4px 12px', fontSize: 13 }}>Sign In</button>
        </p>
      </div>
    </div>
  )
}
