import { useState, useEffect } from 'react'
import { getToken, clearToken } from './auth'
import LoginPage from './components/LoginPage'
import RegisterPage from './components/RegisterPage'
import Dashboard from './components/Dashboard'
import PredictForm from './components/PredictForm'
import DriftView from './components/DriftView'
import LogsView from './components/LogsView'
import FeastView from './components/FeastView'
import FraudAlerts from './components/FraudAlerts'
import UserManagement from './components/UserManagement'
import RoleManagement from './components/RoleManagement'
import AuditLogs from './components/AuditLogs'
import CustomerSegmentation from './components/CustomerSegmentation'

type Tab = 'dashboard' | 'predict' | 'logs' | 'features' | 'drift' | 'alerts' | 'users' | 'roles' | 'audit' | 'segments'

const TAB_MAP: Record<string, Tab> = {
  '/': 'dashboard', '/predict': 'predict', '/logs': 'logs',
  '/features': 'features', '/drift': 'drift', '/alerts': 'alerts',
  '/users': 'users', '/roles': 'roles', '/audit': 'audit', '/segments': 'segments',
}
const PATH_MAP: Record<Tab, string> = Object.fromEntries(
  Object.entries(TAB_MAP).map(([k, v]) => [v, k])
) as Record<Tab, string>

const ALL_TABS: { key: Tab; label: string; icon: string; adminOnly?: boolean }[] = [
  { key: 'dashboard', label: 'Dashboard', icon: '📊' },
  { key: 'predict', label: 'Predict', icon: '🔍' },
  { key: 'alerts', label: 'Alerts', icon: '🚨' },
  { key: 'logs', label: 'Logs', icon: '📋' },
  { key: 'features', label: 'Features', icon: '🏪' },
  { key: 'segments', label: 'Segments', icon: '📊' },
  { key: 'users', label: 'Users', icon: '👥', adminOnly: true },
  { key: 'roles', label: 'Roles', icon: '🔐', adminOnly: true },
  { key: 'audit', label: 'Audit', icon: '📜', adminOnly: true },
  { key: 'drift', label: 'Drift Monitor', icon: '📈' },
]

const API = window.location.origin.includes('3000') ? 'http://localhost:8000' : ''

function getPathTab(): Tab {
  return TAB_MAP[window.location.pathname] || 'dashboard'
}

export default function App() {
  const [tab, setTabState] = useState<Tab>(getPathTab)
  const [authed, setAuthed] = useState(false)
  const [showLogin, setShowLogin] = useState(true)
  const [user, setUser] = useState<any>(null)
  const [checking, setChecking] = useState(true)

  const setTab = (t: Tab) => {
    setTabState(t)
    const path = PATH_MAP[t]
    window.history.pushState(null, '', path)
    document.title = `Fraud Detection - ${t.charAt(0).toUpperCase() + t.slice(1)}`
  }

  useEffect(() => {
    const onPop = () => setTabState(getPathTab())
    window.addEventListener('popstate', onPop)
    const initial = getPathTab()
    if (initial !== tab) setTabState(initial)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  useEffect(() => {
    const token = getToken()
    if (token) {
      fetch(`${API}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => r.ok ? r.json() : null)
        .then(u => { if (u) { setUser(u); setAuthed(true) } else { clearToken() } })
        .catch(() => clearToken())
        .finally(() => setChecking(false))
    } else { setChecking(false) }
  }, [])

  const handleLogin = async () => {
    const token = getToken()
    if (!token) return
    const r = await fetch(`${API}/api/v1/auth/me`, { headers: { Authorization: `Bearer ${token}` } })
    if (r.ok) { setUser(await r.json()); setAuthed(true); setTab('dashboard') }
  }

  const handleLogout = () => { clearToken(); setAuthed(false); setUser(null); window.history.pushState(null, '', '/') }

  const isAdmin = user?.roles?.includes('admin')
  const tabs = ALL_TABS.filter(t => !t.adminOnly || isAdmin)

  if (checking) return <div style={{ textAlign: 'center', padding: 100, fontSize: 18 }}>Loading...</div>

  if (!authed) {
    return showLogin
      ? <LoginPage onLogin={handleLogin} onSwitch={() => setShowLogin(false)} />
      : <RegisterPage onSwitch={() => { setShowLogin(true); window.history.pushState(null, '', '/') }} />
  }

  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '24px 24px 48px' }}>
      <header className="glass" style={{ padding: '16px 24px', marginBottom: 28, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ width: 40, height: 40, borderRadius: 10, background: 'linear-gradient(135deg, var(--accent), var(--accent2))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20 }}>🛡</div>
          <div>
            <h1 style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.3px' }}>Fraud Detection</h1>
            <p style={{ fontSize: 12, color: 'var(--text2)' }}>Real-time ML Monitoring</p>
          </div>
        </div>
        <nav style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          {tabs.map((t) => (
            <button key={t.key} onClick={() => setTab(t.key)}
              className={tab === t.key ? 'btn btn-primary' : 'btn btn-secondary'}
              style={{ padding: '8px 16px', fontSize: 13 }}>
              <span>{t.icon}</span> {t.label}
            </button>
          ))}
          <span style={{ fontSize: 12, color: 'var(--text2)', margin: '0 8px' }}>{user?.username}</span>
          <button className="btn btn-secondary" onClick={handleLogout} style={{ padding: '6px 12px', fontSize: 12 }}>Logout</button>
        </nav>
      </header>

      <div className="fade-in" key={tab}>
        {tab === 'dashboard' && <Dashboard />}
        {tab === 'predict' && <PredictForm />}
        {tab === 'alerts' && <FraudAlerts />}
        {tab === 'logs' && <LogsView />}
        {tab === 'features' && <FeastView />}
        {tab === 'segments' && <CustomerSegmentation />}
        {tab === 'users' && <UserManagement isAdmin={isAdmin} token={getToken()} />}
        {tab === 'roles' && <RoleManagement isAdmin={isAdmin} token={getToken()} />}
        {tab === 'audit' && <AuditLogs />}
        {tab === 'drift' && <DriftView />}
      </div>

      <footer style={{ textAlign: 'center', marginTop: 48, fontSize: 12, color: 'var(--text2)' }}>
        Fraud Detection System &bull; AI-Powered &bull; {user?.username}
      </footer>
    </div>
  )
}
