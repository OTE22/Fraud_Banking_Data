from fastapi import APIRouter, Depends, HTTPException
from app.auth.rbac import require_role
from app.ml.customer_segmentation import load_segmentation_model, segment_with_pretrained
from app.ml.predictor import PREDICTOR
from app.config import get_settings
from app.features.feast_store import get_online_features
from app.core.logging import LOGGER
import pandas as pd
import numpy as np
from pathlib import Path

router = APIRouter(prefix="/segments", tags=["segments"])
_SEG_ARTIFACT: dict | None = None


def _get_seg_artifact():
    global _SEG_ARTIFACT
    if _SEG_ARTIFACT is None:
        settings = get_settings()
        model_dir = Path(settings.model_path).parent
        seg_path = model_dir / "segmentation_model.pkl"
        _SEG_ARTIFACT = load_segmentation_model(seg_path)
    return _SEG_ARTIFACT


@router.post("/predict")
async def predict_segment(n_clusters: int = 4, _=Depends(require_role("data_scientist"))):
    artifact = _get_seg_artifact()
    if artifact is not None:
        csv_path = Path("backend/data/customers.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path, nrows=500)
            feat_cols = artifact.get("feature_cols")
            if feat_cols:
                available = [c for c in feat_cols if c in df.columns]
                if available:
                    X = df[available].fillna(0).values.astype(np.float64)
                    result = segment_with_pretrained(X, artifact)
                    try:
                        feast_rows = [{"customer_id": str(row.get("customer_id", f"cust_{i}"))} for i, row in df.head(100).iterrows()]
                        feast_features = [f"customer_profiles:{c}" for c in available]
                        feast_data = get_online_features(feast_rows, feast_features)
                        if feast_data:
                            result["feast_enriched"] = True
                    except Exception as e:
                        LOGGER.warning("feast_enrich_failed", error=str(e))
                        result["feast_enriched"] = False
                    return result
    X = np.random.randn(100, 8)
    from app.ml.customer_segmentation import segment_customers
    result = segment_customers(X, n_clusters=n_clusters)
    result["feast_enriched"] = False
    return result


@router.post("/predict/customer")
async def predict_customer_segment(customer_id: str, _=Depends(require_role("data_scientist"))):
    feast_features = [f"customer_profiles:{c}" for c in [
        "age", "annual_income", "credit_score", "account_balance",
        "tenure_months", "transaction_frequency_30d",
        "avg_transaction_amount", "num_fraudulent_tx_90d", "high_risk_flag",
    ]]
    feast_data = get_online_features([{"customer_id": customer_id}], feast_features)
    if feast_data and any(v is not None for v in feast_data.values()):
        feat_vals = {k: v[0] if isinstance(v, list) else v for k, v in feast_data.items()}
        expected_cols = [f.split(":")[1] for f in feast_features]
        vals = [feat_vals.get(c, 0.0) or 0.0 for c in expected_cols]
        X = np.array([vals], dtype=np.float64)
        artifact = _get_seg_artifact()
        if artifact:
            return segment_with_pretrained(X, artifact)
    raise HTTPException(status_code=404, detail="Customer not found in feature store")


@router.get("/info")
async def segments_info():
    artifact = _get_seg_artifact()
    if artifact is None:
        return {"loaded": False}
    return {
        "loaded": True,
        "n_clusters": artifact.get("n_clusters"),
        "feature_cols": artifact.get("feature_cols"),
        "cluster_stats": artifact.get("cluster_stats", {}),
        "segment_labels": artifact.get("segment_labels", {}),
    }
