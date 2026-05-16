import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.domain.schemas import TransactionInput, PredictionOutput, PredictionLogDetail, StepFeature, HealthResponse
from app.domain.models import PredictionModel
from app.ml.predictor import PREDICTOR
from app.features.feast_store import get_feast_info
from app.core.db import get_db
from app.config import get_settings, Settings
from app.core.logging import LOGGER

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(settings: Settings = Depends(get_settings), db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False
    return HealthResponse(status="ok", model_loaded=PREDICTOR.loaded, feast_connected=True, db_connected=db_ok, version=settings.app_name)


@router.post("/predict", response_model=PredictionOutput)
async def predict(tx: TransactionInput, db: AsyncSession = Depends(get_db)):
    result, detail = PREDICTOR.predict_with_detail(tx)
    record = PredictionModel(transaction_id=tx.transaction_id, fraud_probability=result.fraud_probability, is_fraudulent=result.is_fraudulent, model_version=result.model_version, input_json=tx.model_dump_json(), detail_json=json.dumps(detail) if detail else None)
    db.add(record)
    await db.commit()
    LOGGER.info("api_predict", tx_id=tx.transaction_id, fraud=result.is_fraudulent)
    return result


@router.get("/predictions/history")
async def prediction_history(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PredictionModel).order_by(PredictionModel.id.desc()).limit(limit))
    return [{"transaction_id": r.transaction_id, "fraud_probability": r.fraud_probability, "is_fraudulent": r.is_fraudulent, "created_at": r.created_at.isoformat() if r.created_at else None} for r in result.scalars()]


@router.get("/features/feast")
async def feast_info():
    return get_feast_info()


@router.get("/predictions/log/{transaction_id}")
async def prediction_log(transaction_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PredictionModel).where(PredictionModel.transaction_id == transaction_id).order_by(PredictionModel.id.desc()).limit(1))
    record = result.scalar_one_or_none()
    if not record or not record.detail_json:
        raise HTTPException(status_code=404, detail="No detail log found for this transaction")
    detail = json.loads(record.detail_json)
    ts = record.created_at or datetime.utcnow()
    return PredictionLogDetail(transaction_id=record.transaction_id, fraud_probability=record.fraud_probability, is_fraudulent=record.is_fraudulent, model_version=record.model_version, timestamp=ts, input_raw=detail.get("input_raw", {}), encoded_type=detail.get("encoded_type", ""), encoded_type_value=detail.get("encoded_type_value", 0), features=[StepFeature(**f) for f in detail.get("features", [])], tree_votes_fraud=detail.get("tree_votes_fraud", 0), tree_votes_legit=detail.get("tree_votes_legit", 0), anomaly_score=detail.get("anomaly_score"), global_feature_importance=detail.get("global_feature_importance", []))


@router.get("/predictions/logs")
async def prediction_logs(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PredictionModel).order_by(PredictionModel.id.desc()).limit(limit))
    return [{"transaction_id": r.transaction_id, "fraud_probability": r.fraud_probability, "is_fraudulent": r.is_fraudulent, "created_at": r.created_at.isoformat() if r.created_at else None, "has_detail": r.detail_json is not None} for r in result.scalars()]
