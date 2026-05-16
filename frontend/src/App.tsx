import { useState } from 'react'
import Dashboard from './components/Dashboard'
import PredictForm from './components/PredictForm'
import DriftView from './components/DriftView'
import LogsView from './components/LogsView'
import FeastView from './components/FeastView'

type Tab = 'dashboard' | 'predict' | 'drift' | 'logs' | 'features'

const tabs: { key: Tab; label: string; icon: string }[] = [
  { key: 'dashboard', label: 'Dashboard', icon: '📊' },
  { key: 'predict', label: 'Predict', icon: '🔍' },
  { key: 'logs', label: 'Logs', icon: '📋' },
  { key: 'features', label: 'Features', icon: '🏪' },
  { key: 'drift', label: 'Drift Monitor', icon: '📈' },
]

export default function App() {
  const [tab, setTab] = useState<Tab>('dashboard')

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
        <nav style={{ display: 'flex', gap: 6 }}>
          {tabs.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={tab === t.key ? 'btn btn-primary' : 'btn btn-secondary'}
              style={{ padding: '8px 16px', fontSize: 13 }}
            >
              <span>{t.icon}</span>
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      <div className="fade-in" key={tab}>
        {tab === 'dashboard' && <Dashboard />}
        {tab === 'predict' && <PredictForm />}
        {tab === 'logs' && <LogsView />}
        {tab === 'features' && <FeastView />}
        {tab === 'drift' && <DriftView />}
      </div>

      <footer style={{ textAlign: 'center', marginTop: 48, fontSize: 12, color: 'var(--text2)' }}>
        Fraud Detection System &bull; AI-Powered
      </footer>
    </div>
  )
}
