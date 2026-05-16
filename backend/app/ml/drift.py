import json
import pandas as pd
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import evidently
from evidently.presets import DataDriftPreset
from sqlalchemy import text
from app.config import get_settings
from app.core.logging import LOGGER
from app.domain.schemas import DriftMetric, DriftReport
from app.domain.models import DriftReportModel

scheduler = AsyncIOScheduler()
_reference_data: pd.DataFrame | None = None
_latest_report: DriftReport | None = None


def set_reference_data(df: pd.DataFrame) -> None:
    global _reference_data
    _reference_data = df
    LOGGER.info("reference_data_set", rows=len(df))


async def run_drift_check(current_data: pd.DataFrame) -> DriftReport:
    global _latest_report
    if _reference_data is None or current_data.empty:
        return DriftReport(
            timestamp=datetime.now(timezone.utc), total_features=0,
            drifted_features=0, drift_percentage=0.0, metrics=[],
        )
    report = evidently.Report(metrics=[DataDriftPreset()])
    report.run(reference_data=_reference_data, current_data=current_data)
    results = report.as_dict()
    metrics_list = []
    drift_count = 0
    drifts = results.get("metrics", [{}])[0].get("result", {}).get("drift_by_columns", {})
    for feat, info in drifts.items():
        score = info.get("drift_score", 0.0)
        drifted = info.get("drift_detected", False)
        if drifted:
            drift_count += 1
        metrics_list.append(DriftMetric(
            feature_name=feat, drift_score=round(score, 4),
            drifted=drifted, test_type=info.get("stattest", "unknown"),
        ))
    total = len(metrics_list) or 1
    _latest_report = DriftReport(
        timestamp=datetime.now(timezone.utc),
        total_features=len(metrics_list),
        drifted_features=drift_count,
        drift_percentage=round(drift_count / total * 100, 2),
        metrics=metrics_list,
    )
    LOGGER.info("drift_check_complete", drifted=drift_count, total=len(metrics_list))
    return _latest_report


def get_latest_report() -> DriftReport | None:
    return _latest_report


async def scheduled_drift_job() -> None:
    from app.core.db import async_session
    settings = get_settings()
    data = _get_recent_production_data()
    report = await run_drift_check(data)
    if report.drift_percentage > settings.drift_threshold * 100:
        LOGGER.warning("drift_threshold_exceeded", pct=report.drift_percentage)
    async with async_session() as session:
        record = DriftReportModel(
            total_features=report.total_features,
            drifted_features=report.drifted_features,
            drift_percentage=report.drift_percentage,
            metrics_json=json.dumps([m.model_dump() for m in report.metrics]),
        )
        session.add(record)
        await session.commit()
    LOGGER.info("drift_report_persisted", id=record.id)


def _get_recent_production_data() -> pd.DataFrame:
    path = "backend/feature_repo/data/transactions.csv"
    if not pd.io.common.file_exists(path):
        LOGGER.warning("production_data_not_found", path=path)
        return pd.DataFrame()
    df = pd.read_csv(path, nrows=1000)
    LOGGER.info("production_data_loaded", rows=len(df), source=path)
    return df


def start_scheduler() -> None:
    settings = get_settings()
    scheduler.add_job(
        scheduled_drift_job, "interval",
        hours=settings.drift_interval_hours,
        id="drift_check",
    )
    scheduler.start()
    LOGGER.info("drift_scheduler_started", interval_h=settings.drift_interval_hours)
