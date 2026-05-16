from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.rbac import require_role
from app.roles.role_manager import list_roles
from app.audit.audit_logger import audit_logger
from app.ml.customer_segmentation import load_segmentation_model, segment_with_pretrained
from app.config import get_settings
from app.core.db import get_db
from app.domain.user_schema import UserCreate, UserResponse
from app.users.services import register_user, list_all_users, update_user_roles
from app.core.logging import LOGGER
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


@router.get("/users", response_model=list[UserResponse])
async def list_users(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    users = await list_all_users(db, skip, limit)
    return [UserResponse(id=u.id, username=u.username, email=u.email, roles=u.roles.split(","), is_active=u.is_active) for u in users]


@router.post("/users", response_model=UserResponse)
async def create_user_admin(body: UserCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    try:
        user = await register_user(db, body.username, body.email, body.password, body.roles)
        LOGGER.info("admin_user_created", username=body.username, roles=body.roles)
        return UserResponse(id=user.id, username=user.username, email=user.email, roles=user.roles.split(","), is_active=user.is_active)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def assign_role(user_id: int, body: UserCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    try:
        user = await update_user_roles(db, user_id, body.roles)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        LOGGER.info("role_assigned", user_id=user_id, roles=body.roles)
        return UserResponse(id=user.id, username=user.username, email=user.email, roles=user.roles.split(","), is_active=user.is_active)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
