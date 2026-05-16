from fastapi import APIRouter, Depends, HTTPException
from app.domain.fraud_schema import FraudAlertResponse, EnsembleScoreRequest, EnsembleScoreResponse
from app.rules.alert_manager import alert_manager
from app.ml.ensemble_engine import ensemble_score
from app.auth.rbac import require_role, get_current_user

router = APIRouter(prefix="/fraud", tags=["fraud"])


@router.get("/alerts", response_model=list[FraudAlertResponse])
async def get_alerts(user: dict = Depends(require_role("fraud_analyst"))):
    alerts = alert_manager.get_recent_safe()
    return [FraudAlertResponse(id=i, **a) for i, a in enumerate(alerts)]


@router.post("/ensemble-score", response_model=EnsembleScoreResponse)
async def ensemble(body: EnsembleScoreRequest):
    result = ensemble_score(body.ml_score, body.rules_score, body.anomaly_score)
    return EnsembleScoreResponse(transaction_id=body.transaction_id, **result)
