from pydantic import BaseModel, Field
from typing import Optional


class FraudAlertCreate(BaseModel):
    transaction_id: str
    risk_score: float = Field(..., ge=0, le=1)
    rule_name: str
    description: str


class FraudAlertResponse(BaseModel):
    id: int
    transaction_id: str
    risk_score: float
    decision: str
    rules: list[str]
    description: str = ""
    status: str = "active"
    created_at: Optional[str] = None


class EnsembleScoreRequest(BaseModel):
    transaction_id: str
    ml_score: float = Field(..., ge=0, le=1)
    rules_score: float = Field(..., ge=0, le=1)
    anomaly_score: float = Field(..., ge=0, le=1)


class EnsembleScoreResponse(BaseModel):
    transaction_id: str
    final_score: float
    decision: str
