from app.core.logging import LOGGER

DEMO_ALERTS = [
    {"transaction_id": "TXN100045", "risk_score": 0.92, "decision": "block", "rules": ["velocity_check", "geo_anomaly", "amount_threshold"], "description": "Large transfer from new device", "status": "active"},
    {"transaction_id": "TXN100032", "risk_score": 0.78, "decision": "review", "rules": ["amount_threshold", "high_risk_merchant"], "description": "High-value merchant payment", "status": "active"},
    {"transaction_id": "TXN100028", "risk_score": 0.65, "decision": "review", "rules": ["velocity_check"], "description": "Multiple rapid transactions", "status": "active"},
    {"transaction_id": "TXN100019", "risk_score": 0.45, "decision": "allow", "rules": ["amount_threshold"], "description": "Slightly above normal amount", "status": "resolved"},
    {"transaction_id": "TXN100011", "risk_score": 0.88, "decision": "block", "rules": ["geo_anomaly", "new_payment_method"], "description": "Login from unusual location", "status": "active"},
]


class AlertManager:
    def __init__(self):
        self.alerts: list[dict] = list(DEMO_ALERTS)

    async def dispatch(self, transaction_id: str, risk_score: float, decision: str, rules: list[str]) -> dict:
        alert = {"transaction_id": transaction_id, "risk_score": risk_score, "decision": decision, "rules": rules, "description": "", "status": "active"}
        self.alerts.append(alert)
        LOGGER.info("alert_dispatched", tx_id=transaction_id, score=risk_score, decision=decision)
        if decision == "block":
            LOGGER.warning("transaction_blocked", tx_id=transaction_id, score=risk_score)
        return alert

    async def get_recent(self, limit: int = 20) -> list[dict]:
        return list(reversed(self.alerts[-limit:]))

    def get_recent_safe(self, limit: int = 20) -> list[dict]:
        return list(reversed(self.alerts[-limit:]))


alert_manager = AlertManager()
