from datetime import datetime
from app.core.logging import LOGGER


class AuditLogger:
    def __init__(self):
        self.entries: list[dict] = []

    async def log(self, action: str, user_id: int | None, resource: str, detail: str = "") -> dict:
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "detail": detail,
        }
        self.entries.append(entry)
        LOGGER.info("audit", **entry)
        return entry

    async def get_logs(self, limit: int = 50) -> list[dict]:
        return list(reversed(self.entries[-limit:]))


audit_logger = AuditLogger()
