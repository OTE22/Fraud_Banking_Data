from fastapi import APIRouter, Depends
from app.auth.rbac import require_role
from app.roles.role_manager import list_roles
from app.audit.audit_logger import audit_logger
from app.ml.customer_segmentation import segment_customers
import numpy as np

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/roles")
async def get_roles(_=Depends(require_role("admin"))):
    return list_roles()


@router.get("/audit-logs")
async def get_audit_logs(limit: int = 50, _=Depends(require_role("auditor"))):
    return await audit_logger.get_logs(limit)


@router.post("/segmentation")
async def run_segmentation(n_clusters: int = 4, _=Depends(require_role("data_scientist"))):
    X = np.random.randn(100, 8)
    return segment_customers(X, n_clusters=n_clusters)
