import { useState, useEffect, useCallback } from 'react'
import { api, PredictionResult, TransactionInput, PredictionHistoryItem } from '../api'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'

const defaultTx: TransactionInput = {
  transaction_id: '',
  step: 1, transaction_type: 'PAYMENT', amount: 100,
  customer_id: 'C001', merchant_id: 'M001',
  oldbalance_orig: 5000, newbalance_orig: 4900,
  oldbalance_dest: 10000, newbalance_dest: 10100,
  is_flagged_fraud: false,
}

const TYPES = ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'CASH_IN', 'DEBIT']

export default function PredictForm() {
  const [form, setForm] = useState<TransactionInput>(defaultTx)
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [history, setHistory] = useState<PredictionHistoryItem[]>([])
  const [loading, setLoading] = useState(false)
  const [animating, setAnimating] = useState(false)

  const fetchHistory = useCallback(async () => {
    try { setHistory(await api.predictionHistory(10)) } catch { }
  }, [])

  useEffect(() => { fetchHistory() }, [fetchHistory])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await api.predict({ ...form, transaction_id: `tx-${Date.now()}` })
      setResult(res)
      setAnimating(true)
      setTimeout(() => setAnimating(false), 500)
      fetchHistory()
    } catch { alert('Prediction failed') }
    finally { setLoading(false) }
  }

  const n = (k: keyof TransactionInput) => (e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [k]: +e.target.value })
  const riskColor = result ? (result.fraud_probability > 0.5 ? 'var(--red)' : result.fraud_probability > 0.2 ? 'var(--yellow)' : 'var(--green)') : 'var(--green)'

  const chartData = history.slice().reverse().map((p) => ({
    name: p.transaction_id.slice(-6),
    risk: +(p.fraud_probability * 100).toFixed(0),
    fraud: p.is_fraudulent ? 100 : 0,
  }))

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
      <div className="card">
        <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 20 }}>Transaction Prediction</h2>
        <form onSubmit={handleSubmit} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14 }}>
          <label>Step <input type="number" min={1} value={form.step} onChange={n('step')} /></label>
          <label>Type <select value={form.transaction_type} onChange={(e) => setForm({ ...form, transaction_type: e.target.value })}>
            {TYPES.map((t) => <option key={t}>{t}</option>)}
          </select></label>
          <label>Amount <input type="number" value={form.amount} onChange={n('amount')} /></label>
          <label>Customer ID <input value={form.customer_id} onChange={(e) => setForm({ ...form, customer_id: e.target.value })} /></label>
          <label>Merchant ID <input value={form.merchant_id} onChange={(e) => setForm({ ...form, merchant_id: e.target.value })} /></label>
          <label>Orig Balance <input type="number" value={form.oldbalance_orig} onChange={n('oldbalance_orig')} /></label>
          <label>New Balance <input type="number" value={form.newbalance_orig} onChange={n('newbalance_orig')} /></label>
          <label>Dest Balance <input type="number" value={form.oldbalance_dest} onChange={n('oldbalance_dest')} /></label>
          <label style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
            <input type="checkbox" checked={form.is_flagged_fraud} onChange={(e) => setForm({ ...form, is_flagged_fraud: e.target.checked })} style={{ width: 'auto' }} />
            Flagged Fraud
          </label>
          <button type="submit" disabled={loading} className="btn btn-primary" style={{ gridColumn: '1 / -1', justifyContent: 'center' }}>
            {loading ? 'Analyzing...' : '🔍 Predict'}
          </button>
        </form>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
        {result ? (
          <div className={`card ${animating ? 'scale-in' : 'fade-in'}`} style={{ borderLeft: `4px solid ${riskColor}` }}>
            <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text2)', marginBottom: 16, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Risk Assessment</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 16 }}>
              <div style={{ position: 'relative', width: 80, height: 80 }}>
                <svg viewBox="0 0 36 36" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="var(--surface2)" strokeWidth="3" />
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke={riskColor} strokeWidth="3" strokeDasharray={`${(result.fraud_probability * 100).toFixed(0)}, 100`} />
                </svg>
                <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', fontSize: 20, fontWeight: 800, color: riskColor }}>{(result.fraud_probability * 100).toFixed(0)}%</div>
              </div>
              <div>
                <div style={{ fontSize: 24, fontWeight: 700, color: riskColor, marginBottom: 4 }}>
                  {result.is_fraudulent ? '🚨 Fraudulent' : '✅ Legitimate'}
                </div>
                <div style={{ fontSize: 12, color: 'var(--text2)' }}>Model: {result.model_version}</div>
                <div style={{ fontSize: 12, color: 'var(--text2)' }}>ID: {result.transaction_id}</div>
              </div>
            </div>
          </div>
        ) : (
          <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 140, color: 'var(--text2)', fontSize: 14 }}>
            Submit a transaction to see risk analysis
          </div>
        )}

        <div className="card" style={{ flex: 1 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, color: 'var(--text2)', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.5px' }}>Recent Predictions</h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={120}>
              <BarChart data={chartData}>
                <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'var(--text2)' }} axisLine={false} tickLine={false} />
                <YAxis hide domain={[0, 100]} />
                <Tooltip contentStyle={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="risk" fill="var(--accent)" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <p style={{ color: 'var(--text2)', fontSize: 13, textAlign: 'center' }}>No predictions yet</p>
          )}
        </div>
      </div>
    </div>
  )
}
