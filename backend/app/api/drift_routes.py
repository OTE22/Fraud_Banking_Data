from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.domain.schemas import DriftReport
from app.domain.models import DriftReportModel
from app.ml.drift import run_drift_check, get_latest_report, set_reference_data
from app.core.db import get_db
import pandas as pd
import json

router = APIRouter(prefix="/drift", tags=["drift"])


@router.get("/status", response_model=DriftReport | None)
async def drift_status():
    return get_latest_report()


@router.post("/run", response_model=DriftReport)
async def run_drift(db: AsyncSession = Depends(get_db)):
    report = await run_drift_check(pd.DataFrame())
    record = DriftReportModel(total_features=report.total_features, drifted_features=report.drifted_features, drift_percentage=report.drift_percentage, metrics_json=json.dumps([m.model_dump() for m in report.metrics]))
    db.add(record)
    await db.commit()
    return report


@router.get("/history")
async def drift_history(limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DriftReportModel).order_by(DriftReportModel.id.desc()).limit(limit))
    return [{"id": r.id, "drift_percentage": r.drift_percentage, "drifted_features": r.drifted_features, "created_at": r.created_at.isoformat() if r.created_at else None} for r in result.scalars()]


@router.post("/reference")
async def set_reference():
    df = pd.read_csv("backend/feature_repo/data/transactions.csv")
    set_reference_data(df)
    return {"status": "reference_set", "rows": len(df)}
