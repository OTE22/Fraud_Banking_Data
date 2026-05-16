const BASE = '/api/v1'

export interface TransactionInput {
  transaction_id: string
  step: number
  transaction_type: string
  amount: number
  customer_id: string
  merchant_id: string
  oldbalance_orig: number
  newbalance_orig: number
  oldbalance_dest: number
  newbalance_dest: number
  is_flagged_fraud: boolean
}

export interface PredictionResult {
  transaction_id: string
  fraud_probability: number
  is_fraudulent: boolean
  model_version: string
  timestamp: string
}

export interface DriftMetric {
  feature_name: string
  drift_score: number
  drifted: boolean
  test_type: string
}

export interface DriftReport {
  timestamp: string
  total_features: number
  drifted_features: number
  drift_percentage: number
  metrics: DriftMetric[]
}

export interface HealthStatus {
  status: string
  model_loaded: boolean
  feast_connected: boolean
  db_connected: boolean
  version: string
}

export interface PredictionHistoryItem {
  transaction_id: string
  fraud_probability: number
  is_fraudulent: boolean
  created_at: string
}

export interface DriftHistoryItem {
  id: number
  drift_percentage: number
  drifted_features: number
  created_at: string
}

export interface StepFeature {
  name: string
  raw_value: number
  scaled_value: number
}

export interface PredictionLog {
  transaction_id: string
  fraud_probability: number
  is_fraudulent: boolean
  model_version: string
  timestamp: string
  input_raw: Record<string, unknown>
  encoded_type: string
  encoded_type_value: number
  features: StepFeature[]
  tree_votes_fraud: number
  tree_votes_legit: number
  global_feature_importance: { feature: string; importance: number }[]
}

export interface PredictionLogSummary {
  transaction_id: string
  fraud_probability: number
  is_fraudulent: boolean
  created_at: string
  has_detail: boolean
}

export interface FeastFeatureField {
  name: string
  dtype: string
}

export interface FeastFeatureView {
  name: string
  ttl: string
  fields: FeastFeatureField[]
  entities: string[]
  row_count?: number
  stats?: Record<string, { count: number; min: number | null; max: number | null; mean: number | null; nulls: number }>
  non_numeric_cols?: string[]
}

export interface FeastEntity {
  name: string
  join_keys: string[]
}

export interface FeastInfo {
  connected: boolean
  online_store?: string
  offline_store?: string
  feature_views?: FeastFeatureView[]
  entities?: FeastEntity[]
  push_sources?: { name: string }[]
  error?: string
}

async function request<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  })
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}

export const api = {
  health: () => request<HealthStatus>('/health'),
  predict: (tx: TransactionInput) =>
    request<PredictionResult>('/predict', { method: 'POST', body: JSON.stringify(tx) }),
  driftStatus: () => request<DriftReport | null>('/drift/status'),
  runDrift: () => request<DriftReport>('/drift/run', { method: 'POST' }),
  setReference: () => request<{ status: string; rows: number }>('/drift/reference', { method: 'POST' }),
  predictionHistory: (limit = 20) => request<PredictionHistoryItem[]>(`/predictions/history?limit=${limit}`),
  driftHistory: (limit = 10) => request<DriftHistoryItem[]>(`/drift/history?limit=${limit}`),
  predictionLog: (txId: string) => request<PredictionLog>(`/predictions/log/${encodeURIComponent(txId)}`),
  predictionLogs: (limit = 20) => request<PredictionLogSummary[]>(`/predictions/logs?limit=${limit}`),
  feastInfo: () => request<FeastInfo>('/features/feast'),
}
