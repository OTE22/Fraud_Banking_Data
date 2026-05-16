# PROJECT_MAP — Enterprise Banking Fraud Detection & AI Platform

## [BUSINESS_GOAL]

Enterprise-grade real-time fraud detection and behavioral intelligence platform for banking systems:
- Real-time fraud detection, reduced false positives, explainable AI decisions
- Customer segmentation, ML + anomaly detection + rules engine
- RBAC/IAM security, model/data drift tracking, MLOps lifecycle
- Scalable AWS deployment, future reinforcement learning optimization

---

## [BUSINESS_KPIs]

| KPI | Target |
|-----|--------|
| Fraud Detection Recall | > 97% |
| False Positive Rate | < 1.5% |
| Fraud Detection Latency | < 200ms |
| Model Drift Detection Time | < 6h |
| API Availability | 99.9% |
| Transaction Throughput | 5K TPS |
| Customer Friction Reduction | -30% |
| Fraud Loss Reduction | -60% |

---

## [TECH_STACK]

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Backend API | FastAPI | 0.136+ | REST APIs |
| Validation | Pydantic | 2.13+ | Schema validation |
| ASGI Server | Uvicorn | 0.46+ | Production serving |
| ML Models | scikit-learn | 1.6+ | Fraud classification |
| Gradient Boosting | XGBoost | Latest | Fraud scoring |
| Feature Store | Feast | 0.44+ | Online/offline features |
| Drift Detection | Evidently AI | 0.6+ | Drift monitoring |
| Experiment Tracking | MLflow | Latest | MLOps |
| Dataset Versioning | DVC | Latest | Data versioning |
| Streaming | Apache Kafka | Latest | Real-time transactions |
| Stream Processing | Apache Spark | Latest | Real-time fraud analytics |
| Cache | Redis | 7-alpine | Online feature store |
| Database | PostgreSQL | 16+ | Persistent storage |
| ORM | SQLAlchemy | Latest | DB abstraction |
| Scheduler | APScheduler | 3.11+ | Drift jobs |
| Frontend | React | 19+ | SPA dashboard |
| Build Tool | Vite | 6+ | Frontend bundling |
| Charts | Recharts | 2.15+ | Fraud/drift dashboards |
| Authentication | OAuth2 + JWT | Latest | Security |
| Password Hashing | bcrypt | Latest | Secure auth |
| Containerization | Docker | Latest | Packaging |
| Orchestration | Kubernetes | Latest | Scaling |
| Infrastructure | Amazon Web Services | — | Cloud deployment |
| CI/CD | GitHub Actions | — | Automation |
| Monitoring | Grafana | Latest | Dashboards |
| Metrics | Prometheus | Latest | Metrics collection |

---

## [SYSTEM_FLOW]

```
Customer Transaction
        │
        ▼
Kafka Streaming Pipeline
        │
        ▼
Feature Engineering Pipeline
        │
        ├──────────────┬──────────────┐
        ▼              ▼              ▼
 Rules Engine     ML Fraud Model   Anomaly Detection
        │              │              │
        └──────────────┴──────────────┘
                       │
                       ▼
               Ensemble Risk Scoring
                       │
                       ▼
                Fraud Decision API
                       │
         ┌─────────────┴─────────────┐
         ▼                           ▼
 Allow Transaction          Block/Review Transaction
         │                           │
         ▼                           ▼
  Audit Logging             Fraud Investigation
         │
         ▼
 Drift Monitoring + Retraining
```

---

## [ARCHITECTURE]

```
enterprise_banking_fraud_platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI lifespan, CORS, router mounts
│   │   ├── config.py            # Pydantic Settings (env-based)
│   │   ├── api/
│   │   │   ├── routes.py        # Core REST endpoints
│   │   │   ├── auth_routes.py   # OAuth2 + JWT auth endpoints
│   │   │   ├── fraud_routes.py  # Fraud-specific endpoints
│   │   │   ├── drift_routes.py  # Drift monitoring endpoints
│   │   │   └── admin_routes.py  # Admin management endpoints
│   │   ├── core/
│   │   │   ├── logging.py       # Structured JSON logger
│   │   │   ├── deps.py          # FastAPI dependency injection
│   │   │   ├── security.py      # OAuth2 scheme + JWT validation
│   │   │   └── middleware.py    # Request logging, rate limiting
│   │   ├── domain/
│   │   │   ├── schemas.py       # Base Pydantic models
│   │   │   ├── fraud_schema.py  # Fraud-related schemas
│   │   │   ├── user_schema.py   # User/account schemas
│   │   │   └── role_schema.py   # RBAC role schemas
│   │   ├── auth/
│   │   │   ├── jwt_handler.py   # JWT encode/decode
│   │   │   ├── password_utils.py# bcrypt hashing
│   │   │   ├── permissions.py   # Permission checks
│   │   │   └── rbac.py          # Role-based access control
│   │   ├── users/
│   │   │   ├── models.py        # User ORM model
│   │   │   ├── repository.py    # User DB operations
│   │   │   └── services.py      # User business logic
│   │   ├── roles/
│   │   │   ├── role_manager.py  # Role CRUD
│   │   │   └── permission_manager.py
│   │   ├── groups/
│   │   │   └── group_manager.py # Group management
│   │   ├── audit/
│   │   │   └── audit_logger.py  # Audit trail logging
│   │   ├── analytics/
│   │   │   ├── visualization.py # Data viz helpers
│   │   │   ├── kpi_analysis.py  # KPI computation
│   │   │   └── fraud_patterns.py# Pattern detection
│   │   ├── features/
│   │   │   ├── feature_engineering.py
│   │   │   ├── graph_features.py
│   │   │   ├── temporal_features.py
│   │   │   ├── feature_selection.py
│   │   │   ├── feature_pipeline.py
│   │   │   └── feast_store.py   # Feast wrapper
│   │   ├── rules/
│   │   │   ├── rules_engine.py  # Business rules
│   │   │   ├── risk_scoring.py  # Risk scoring
│   │   │   └── alert_manager.py # Alert dispatch
│   │   ├── ml/
│   │   │   ├── train_model.py   # Model training script
│   │   │   ├── predictor.py     # sklearn inference
│   │   │   ├── anomaly_detection.py
│   │   │   ├── ensemble_engine.py
│   │   │   ├── evaluate_model.py
│   │   │   ├── shap_analysis.py
│   │   │   ├── customer_segmentation.py
│   │   │   └── drift.py         # Evidently drift
│   │   ├── rl/
│   │   │   ├── banking_environment.py
│   │   │   └── train_rl_agent.py
│   │   ├── streaming/
│   │   │   ├── kafka_producer.py
│   │   │   ├── kafka_consumer.py
│   │   │   └── realtime_scoring.py
│   │   ├── monitoring/
│   │   │   ├── prometheus_metrics.py
│   │   │   ├── grafana_dashboards/
│   │   │   └── drift_monitor.py
│   │   └── data/
│   │       ├── database.py      # DB engine + session
│   │       ├── cleaning.py      # Data cleaning
│   │       ├── validation.py    # Data validation
│   │       └── load_data.py     # Data loading
│   ├── models/
│   ├── notebooks/
│   ├── tests/
│   ├── feature_repo/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx / api.ts / auth.ts
│   │   ├── components/ (Dashboard, PredictForm, DriftView,
│   │   │                FraudAlerts, UserManagement,
│   │   │                RoleManagement, AuditLogs,
│   │   │                CustomerSegmentation, LogsView, FeastView)
│   │   └── main.tsx
│   └── vite.config.ts
├── infra/
│   ├── docker-compose.yml
│   ├── ec2-setup.sh
│   ├── terraform/
│   └── kubernetes/
└── .github/workflows/ci-cd.yml
```

---

## [FRAUD_FEATURES]

| Feature | Purpose |
|---------|---------|
| transaction_velocity | Detect bots |
| avg_spending_24h | Behavioral baseline |
| geo_distance | Impossible travel |
| device_change_rate | Account takeover |
| merchant_risk_score | Dangerous merchants |
| failed_login_count | Credential attacks |
| shared_device_count | Fraud rings |
| night_activity_ratio | Suspicious activity |

---

## [ML_PIPELINE]

```
Raw Transactions → Data Validation → Cleaning Pipeline
→ Feature Engineering → Feature Store → Training Pipeline
→ MLflow Tracking → Model Registry → Deployment
→ Monitoring & Drift Detection
```

---

## [RBAC_SYSTEM]

| Role | Permissions |
|------|-------------|
| Admin | Full system |
| Fraud Analyst | View alerts, freeze accounts |
| Data Scientist | Train/retrain models |
| ML Engineer | Deploy models |
| Auditor | Read-only access |
| SOC Team | Security investigations |

---

## [DRIFT_MONITORING]

| Type | Tool |
|------|------|
| Data Drift | Evidently AI |
| API Metrics | Prometheus |
| Visualization | Grafana |
| Log Aggregation | ELK Stack |
| Alerting | Slack/Email |

---

## [AWS_DEPLOYMENT]

| Service | Purpose |
|---------|---------|
| EC2 | API hosting |
| S3 | Model/data storage |
| RDS PostgreSQL | Database |
| ElastiCache Redis | Online feature cache |
| ECR | Docker registry |
| CloudWatch | Logs/monitoring |
| IAM | Security |
| ALB | Load balancing |

---

## [CI_CD_PIPELINE]

```
Git Push → GitHub Actions → Linting → Unit Tests
→ Build Docker Images → Push to ECR
→ Deploy to EC2/Kubernetes → Health Checks → Production
```

---

## [PENDING_ENTERPRISE_FEATURES]

| Feature | Priority |
|---------|----------|
| Reinforcement Learning Adaptive Scoring | High |
| Graph Neural Network Fraud Rings | High |
| Real-Time Spark Streaming | Medium |
| MFA Authentication | High |
| SSO Integration | Medium |
| Canary Deployment | Medium |
| A/B Testing | Medium |
| SHAP Dashboard | High |
| Real-Time Notification Engine | Medium |
| Auto Retraining Pipeline | High |

---

**Built:** Enterprise-grade modular design with explainable AI, streaming analytics, RBAC security, MLOps, and scalable AWS deployment.
