# Enterprise Banking Fraud Detection & AI Platform

Real-time fraud detection system with ML models, Feast feature store, RBAC, MLOps monitoring, and customer segmentation.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12, FastAPI, SQLAlchemy (async), PostgreSQL |
| **ML** | scikit-learn (RandomForest, IsolationForest, KMeans), PCA |
| **Feature Store** | Feast (Redis online, Parquet offline) |
| **Frontend** | React 19, TypeScript, Vite, Recharts |
| **Infrastructure** | Docker Compose, Nginx, Redis |
| **Auth** | JWT (python-jose), bcrypt, RBAC with role hierarchy |
| **Monitoring** | Evidently AI (drift detection), APScheduler |

## Architecture

```
┌─────────────┐     ┌──────────┐     ┌─────────────┐
│  Frontend   │────▶│  Nginx   │────▶│  FastAPI     │
│  React 19   │     │  Proxy   │     │  Backend     │
│  :8080      │◀────│  :80     │◀────│  :8000       │
└─────────────┘     └──────────┘     └──────┬───────┘
                                            │
                    ┌───────────────────────┼───────────────────┐
                    │                       │                   │
                    ▼                       ▼                   ▼
              ┌──────────┐          ┌───────────┐       ┌──────────┐
              │PostgreSQL│          │  Redis    │       │  Feast   │
              │ :5432    │          │  :6379    │       │  Online  │
              └──────────┘          └───────────┘       └──────────┘
```

## Quick Start

```bash
docker compose up -d --build
```

Access:
- **Frontend**: http://localhost:8080
- **API docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Analyst** | `analyst1` | `admin123` |

> Register new users at http://localhost:8080 (click "Register")

## RBAC Role Hierarchy

| Role | Permissions |
|------|------------|
| **admin** | Full access — users, roles, audit, segments, alerts, drift, all ML endpoints |
| **fraud_analyst** | Predict, alerts, logs, dashboard |
| **data_scientist** | Segmentation, drift, predictions |
| **ml_engineer** | Model info, drift, predictions |
| **auditor** | Audit logs |
| **soc_team** | Alerts, predictions |

> Admin can assign roles via the **Users** tab at `localhost:8080/users`

## ML Models

### 1. Fraud Detection (RandomForest)
- **File**: `backend/models/fraud_model.pkl`
- **Training**: `backend/train_model.py` — 8 features from `AIML Dataset.csv`
- **Accuracy**: ~99.97%
- **Endpoint**: `POST /api/v1/predict`
- **Detail**: `POST /api/v1/predict` (returns 16 fields incl. anomaly_score, feature importance, tree votes)

### 2. Anomaly Detection (IsolationForest)
- **File**: `backend/models/anomaly_model.pkl`
- **Training**: `backend/train_anomaly_model.py` — 9 engineered features from `backend/data/transactions.csv`
- **Contamination rate**: 1%
- **Endpoint**: `POST /api/v1/predict/anomaly`
- **CSV Export**: `GET /api/v1/predict/anomaly/export?limit=1000` — downloads `anomaly_predictions.csv`

### 3. Customer Segmentation (KMeans + PCA)
- **File**: `backend/models/segmentation_model.pkl`
- **Training**: `backend/train_segmentation_model.py` — 9 customer features from `backend/data/customers.csv`
- **Clusters**: 4 (low_risk, medium_risk, high_risk, critical_risk)
- **Endpoints**:
  - `POST /api/v1/segments/predict` — full segmentation
  - `POST /api/v1/segments/predict/customer?customer_id=X` — single via Feast
  - `GET /api/v1/segments/info` — model metadata

## Feast Feature Store

4 registered FeatureViews:

| View | Entity | Fields | Rows |
|------|--------|--------|------|
| `customer_stats` | customer_id | avg_transaction_amount_30d, transaction_count_30d, is_high_risk_merchant_30d | 100K |
| `merchant_stats` | merchant_id | avg_merchant_amount, merchant_fraud_rate_7d | 39K |
| `customer_profiles` | customer_id | age, income, credit_score, balance, tenure, etc. | 5K |
| `anomaly_features` | transaction_id | 9 engineered anomaly features + anomaly_score | 20K |

View at **Features** tab in the UI or `GET /api/v1/features/feast`

## API Endpoints

### Public
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Create account (default: fraud_analyst) |
| POST | `/api/v1/auth/login` | Get JWT token |

### Authenticated
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/auth/me` | Current user info |
| GET | `/api/v1/health` | System health |
| POST | `/api/v1/predict` | Fraud prediction |
| POST | `/api/v1/predict/anomaly` | Anomaly score only |
| GET | `/api/v1/predict/anomaly/export` | Download CSV |
| GET | `/api/v1/predictions/history` | Recent predictions |
| GET | `/api/v1/predictions/logs` | Prediction summaries |
| GET | `/api/v1/predictions/log/{id}` | Full prediction detail |
| GET | `/api/v1/features/feast` | Feast store info |
| GET | `/api/v1/drift/status` | Latest drift report |
| POST | `/api/v1/drift/run` | Trigger drift check |
| POST | `/api/v1/drift/reference` | Set reference data |
| POST | `/api/v1/fraud/ensemble` | Ensemble prediction |

### Admin-Only
| Method | Path | Role Required |
|--------|------|---------------|
| GET | `/api/v1/admin/users` | admin |
| POST | `/api/v1/admin/users` | admin |
| PUT | `/api/v1/admin/users/{id}/role` | admin |
| GET | `/api/v1/admin/roles` | admin |
| GET | `/api/v1/admin/audit-logs` | auditor |
| POST | `/api/v1/segments/predict` | data_scientist |
| GET | `/api/v1/segments/info` | data_scientist |

## Running Tests

```bash
docker compose exec api pip install pytest pytest-asyncio
docker compose exec api python -m pytest backend/tests/ -v
```

All 51 tests pass across 4 test files:
- `test_api.py` (18) — health, predict, history, logs, drift, feast, ensemble, anomaly, CSV export
- `test_auth.py` (10) — register, login, me, token validation
- `test_admin.py` (10) — user CRUD, role assign, roles, audit logs
- `test_rbac.py` (9) — endpoint RBAC enforcement
- `test_segments.py` (4) — segmentation predict, info, RBAC

## Generating Datasets

```bash
# Transaction data (200K rows)
docker compose exec api python backend/data/generate_datasets.py

# Train all models
docker compose exec api python backend/train_model.py
docker compose exec api python backend/train_anomaly_model.py
docker compose exec api python backend/train_segmentation_model.py

# Feast data + apply
docker compose exec api python backend/generate_feast_data.py
docker compose exec api bash -c "cd backend/feature_repo && feast apply && feast materialize 2020-01-01 2030-12-31"
```

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/           # FastAPI route handlers
│   │   │   ├── routes.py          # Predict, health, feast, CSV export
│   │   │   ├── auth_routes.py     # Register, login, me
│   │   │   ├── admin_routes.py    # User/role management
│   │   │   ├── fraud_routes.py    # Ensemble fraud alerts
│   │   │   ├── drift_routes.py    # Drift monitoring
│   │   │   └── segments_routes.py # Segmentation endpoints
│   │   ├── auth/          # JWT, RBAC, password utils
│   │   ├── ml/            # Models: predictor, anomaly, segmentation, drift
│   │   ├── features/      # Feast store integration
│   │   ├── users/         # User service & models
│   │   ├── roles/         # Role definitions
│   │   ├── audit/         # Audit logging
│   │   ├── core/          # DB, logging, middleware, config
│   │   └── domain/        # Schemas, models
│   ├── models/            # Pickled ML models
│   ├── data/              # Generated datasets
│   ├── feature_repo/      # Feast feature definitions
│   ├── tests/             # Pytest test suite
│   ├── train_model.py             # Fraud model training
│   ├── train_anomaly_model.py     # Anomaly model training
│   ├── train_segmentation_model.py # Segmentation model training
│   ├── generate_datasets.py       # Synthetic data generation
│   └── generate_feast_data.py     # Feast parquet generation
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── App.tsx        # Path-based routing
│   │   ├── api.ts         # API client
│   │   └── auth.ts        # JWT storage
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── Dockerfile (API)
```

## CSV Export

Download anomaly predictions as CSV:

```bash
curl "http://localhost:8000/api/v1/predict/anomaly/export?limit=1000" -o anomaly_predictions.csv
```

Columns: `transaction_id, fraud_probability, is_fraudulent, amount, oldbalance_orig, newbalance_orig, oldbalance_dest, newbalance_dest, anomaly_score, anomaly_feature_1..9, created_at`

## Monitoring

- **Drift Detection**: Evidently AI drift reports every 6 hours (configurable)
- **Audit Logs**: All admin actions logged, viewable at `/admin/audit-logs`
- **Prediction Logs**: Each prediction stored with full feature detail
