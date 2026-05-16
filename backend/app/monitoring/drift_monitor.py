from app.ml.drift import scheduled_drift_job


class DriftMonitor:
    def __init__(self):
        self.last_check = None

    async def run_check(self) -> dict:
        await scheduled_drift_job()
        self.last_check = None
        return {"status": "drift_check_completed"}
