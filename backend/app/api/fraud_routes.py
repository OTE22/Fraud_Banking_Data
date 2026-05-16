from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.fraud_schema import FraudAlertResponse, EnsembleScoreRequest, EnsembleScoreResponse
from app.rules.alert_manager import alert_manager
from app.rules.risk_scoring import compute_risk_score
from app.ml.ensemble_engine import ensemble_score
from app.core.db import get_db
from app.auth.rbac import require_role

router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.get("/alerts", response_model=list[FraudAlertResponse])
async def get_alerts(_=Depends(require_role("fraud_analyst"))):
    alerts = await alert_manager.get_recent()
    return [FraudAlertResponse(id=i, **a) for i, a in enumerate(alerts)]


@router.post("/ensemble-score", response_model=EnsembleScoreResponse)
async def ensemble(body: EnsembleScoreRequest):
    result = ensemble_score(body.ml_score, body.rules_score, body.anomaly_score)
    return EnsembleScoreResponse(transaction_id=body.transaction_id, **result)
