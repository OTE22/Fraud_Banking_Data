from app.core.logging import LOGGER


class AlertManager:
    def __init__(self):
        self.alerts: list[dict] = []

    async def dispatch(self, transaction_id: str, risk_score: float, decision: str, rules: list[str]) -> dict:
        alert = {"transaction_id": transaction_id, "risk_score": risk_score, "decision": decision, "rules": rules}
        self.alerts.append(alert)
        LOGGER.info("alert_dispatched", **alert)
        if decision == "block":
            LOGGER.warning("transaction_blocked", tx_id=transaction_id, score=risk_score)
        return alert

    async def get_recent(self, limit: int = 20) -> list[dict]:
        return list(reversed(self.alerts[-limit:]))


alert_manager = AlertManager()
