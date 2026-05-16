from app.ml.predictor import PREDICTOR
from app.rules.risk_scoring import compute_risk_score
from app.rules.alert_manager import alert_manager


async def score_transaction(transaction) -> dict:
    result = PREDICTOR.predict(transaction)
    risk = compute_risk_score(transaction, result.fraud_probability, anomaly_score=0.0)
    await alert_manager.dispatch(transaction.transaction_id, risk["final_score"], risk["decision"], risk["triggered_rules"])
    return {"transaction_id": transaction.transaction_id, "fraud_probability": result.fraud_probability, **risk}
