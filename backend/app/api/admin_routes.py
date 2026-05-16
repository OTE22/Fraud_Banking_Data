from fastapi import APIRouter, Depends, HTTPException
from app.auth.rbac import require_role
from app.roles.role_manager import list_roles
from app.audit.audit_logger import audit_logger
from app.ml.customer_segmentation import load_segmentation_model, segment_with_pretrained
from app.config import get_settings
import pandas as pd
import numpy as np
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])

_SEG_ARTIFACT: dict | None = None


def _get_segmentation_artifact():
    global _SEG_ARTIFACT
    if _SEG_ARTIFACT is None:
        settings = get_settings()
        model_dir = Path(settings.model_path).parent
        seg_path = model_dir / "segmentation_model.pkl"
        _SEG_ARTIFACT = load_segmentation_model(seg_path)
    return _SEG_ARTIFACT


@router.get("/roles")
async def get_roles(_=Depends(require_role("admin"))):
    return list_roles()


@router.get("/audit-logs")
async def get_audit_logs(limit: int = 50, _=Depends(require_role("auditor"))):
    return await audit_logger.get_logs(limit)


@router.post("/segmentation")
async def run_segmentation(n_clusters: int = 4, _=Depends(require_role("data_scientist"))):
    artifact = _get_segmentation_artifact()
    if artifact is not None:
        csv_path = Path("backend/data/customers.csv")
        if csv_path.exists():
            df = pd.read_csv(csv_path, nrows=500)
            feat_cols = artifact.get("feature_cols")
            if feat_cols:
                available = [c for c in feat_cols if c in df.columns]
                if available:
                    X = df[available].fillna(0).values.astype(np.float64)
                    return segment_with_pretrained(X, artifact)
    X = np.random.randn(100, 8)
    from app.ml.customer_segmentation import segment_customers
    return segment_customers(X, n_clusters=n_clusters)
