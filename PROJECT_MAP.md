# PROJECT_MAP — Fraud Detection System

## [TECH_STACK]

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend | FastAPI | 0.136.1 | REST API framework |
| Validation | Pydantic | 2.13.4 | Data validation & settings |
| ASGI Server | Uvicorn | 0.46.0 | Production server |
| Feature Store | Feast | 0.44.0 | Feature management & serving |
| Drift Detection | Evidently AI | 0.6.0 | Data drift monitoring |
| Scheduler | APScheduler | 3.11.0 | Periodic drift checks |
| ML Model | RandomForest (sklearn) | 1.6.1 | Fraud classifier, 8 features |
| Caching | Redis | 7-alpine | Feast online store |
| Frontend | React | 19.2.6 | SPA UI |
| Build | Vite | 6.x | Frontend bundler |
| Charts | Recharts | 2.15+ | Drift visualization |
| CI/CD | GitHub Actions | — | Lint → Test → Build → Deploy |
| Infra | AWS EC2 (Docker) | — | Production hosting |

## [SYSTEM_FLOW]

```
User (Browser)
    │
    ├── /predict ──► FastAPI ──► Feast (online store) ──► Model ──► Response
    │                     │           └── Redis cache
    │                     └── Evidently (drift check — scheduled)
    │
    ├── /drift/* ──► FastAPI ──► Evidently Report ──► JSON Response
    │
    └── /health ──► FastAPI ──► { status, model, feast }
```

**Data flow:**
1. Transaction arrives via POST /predict
2. Feast retrieves customer/merchant feature vectors (online store)
3. Features + raw input → FraudPredictor.predict_proba()
4. Response returned to frontend
5. Background: APScheduler triggers Evidently drift check every 6h
6. Drift reports queryable via GET /drift/status

## [ARCHITECTURE]

```
fraud_detection/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI lifespan, CORS, router mount
│   │   ├── config.py            # Pydantic Settings (env-based)
│   │   ├── api/routes.py        # REST endpoints (<200 lines)
│   │   ├── core/
│   │   │   ├── logging.py       # Async structlog JSON logger
│   │   │   └── deps.py          # FastAPI dependency injection
│   │   ├── domain/schemas.py    # Pydantic I/O models
│   │   ├── features/
│   │   │   └── feast_store.py   # Feast wrapper (online get/push)
│   │   └── ml/
│   │       ├── predictor.py     # sklearn model inference
│   │       └── drift.py         # Evidently drift + scheduler
│   ├── train_model.py           # Model training script
│   ├── generate_feast_data.py   # Feast Parquet generator
│   ├── tests/
│   │   └── test_api.py          # 5 pytest tests (all passing)
│   ├── models/
│   │   └── fraud_model.pkl      # Trained RandomForest artifact
│   ├── feature_repo/            # Feast definitions + data
│   │   ├── feature_store.yaml
│   │   ├── features.py
│   │   └── data/                # Parquet + CSV sources
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx              # Tab navigation
│   │   ├── api.ts               # API client (fetch wrapper)
│   │   ├── components/
│   │   │   ├── Dashboard.tsx    # Health status cards
│   │   │   ├── PredictForm.tsx  # Transaction form + result
│   │   │   └── DriftView.tsx    # Drift metrics table
│   │   └── main.tsx             # React entry
│   ├── index.html / package.json / vite.config.ts
├── .github/workflows/ci-cd.yml   # CI/CD pipeline
├── infra/
│   ├── docker-compose.yml        # Service orchestration
│   └── ec2-setup.sh              # EC2 bootstrap
└── PROJECT_MAP.md
```

**Key constraints:**
- All source files ≤200 lines (verified: max = 113 lines in tests)
- Domain-driven grouping (api/core/domain/features/ml)
- No micro-files: functional cohesion within each module

## [DOCKER SETUP]

```bash
# Build and run all services
docker compose up --build

# Run in background
docker compose up --build -d

# Check logs
docker compose logs -f api

# Access:
#   UI:     http://localhost:8080
#   API:    http://localhost:8000/api/v1/health
#   Docs:   http://localhost:8000/docs
```

**Services:**
- `redis` — Feast online store backend
- `api` — FastAPI + model + Feast + Evidently (auto-trains model on build)
- `frontend` — Nginx serving React SPA, proxies `/api/*` to backend

## [ORPHANS & PENDING]

| Item | Status | Priority | Notes |
|------|--------|----------|-------|
| Model artifact (fraud_model.pkl) | ✅ DONE | High | RandomForest trained on 200K samples, accuracy 0.9997 |
| Feast data sources (Parquet) | ✅ DONE | High | customer_features.parquet (100K rows) + merchant_features.parquet (39K rows) |
| PostgreSQL + SQLAlchemy models | ✅ DONE | High | prediction + drift_report tables, async engine, auto-create on startup |
| Unit tests (7 tests) | ✅ DONE | Medium | health, predict ×2, drift ×2, history ×2, model_loaded — all passing |
| DB mock for tests | ✅ DONE | Medium | dependency_overrides[get_db] with MockSession |
| Frontend Docker nginx config | ✅ DONE | Low | nginx.conf with API proxy + SPA fallback |
| Drift persistence in scheduled job | ✅ DONE | Medium | scheduled_drift_job now saves to PostgreSQL (was in-memory only) |
| DB health check in /health | ✅ DONE | Medium | db_connected field via `SELECT 1` probe |
| CORS includes Docker port | ✅ DONE | Low | Added localhost:8080 alongside 5173 |
| .gitignore | ✅ DONE | Medium | __pycache__, .pkl, .csv, .parquet, .env, node_modules |
| Orphans cleaned | ✅ DONE | Low | Removed fraud_detection.py (empty stub) + baseline_fraud_model.pkl |
| Production Redis | PENDING | Medium | Replace local Redis with ElastiCache for prod |
| SSL/TLS (HTTPS) | PENDING | Low | Add certbot + domain for production |
| GitHub secrets (EC2_SSH_KEY etc.) | PENDING | High | Set in repo settings before first deploy |
