from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TransactionInput(BaseModel):
    transaction_id: str
    step: int = Field(1, ge=1, description="Time step (hour)")
    transaction_type: str = Field("PAYMENT", pattern=r"^(PAYMENT|TRANSFER|CASH_OUT|CASH_IN|DEBIT)$")
    amount: float = Field(..., gt=0)
    customer_id: str
    merchant_id: str
    oldbalance_orig: float = Field(0, ge=0)
    newbalance_orig: float = Field(0, ge=0)
    oldbalance_dest: float = Field(0, ge=0)
    newbalance_dest: float = Field(0, ge=0)
    is_flagged_fraud: bool = False


class PredictionOutput(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_fraudulent: bool
    model_version: str
    timestamp: datetime


class DriftMetric(BaseModel):
    feature_name: str
    drift_score: float
    drifted: bool
    test_type: str


class DriftReport(BaseModel):
    timestamp: datetime
    total_features: int
    drifted_features: int
    drift_percentage: float
    metrics: list[DriftMetric]


class StepFeature(BaseModel):
    name: str
    raw_value: float
    scaled_value: float


class PredictionLogDetail(BaseModel):
    transaction_id: str
    fraud_probability: float
    is_fraudulent: bool
    model_version: str
    timestamp: datetime
    input_raw: dict
    encoded_type: str
    encoded_type_value: int
    features: list[StepFeature]
    tree_votes_fraud: int
    tree_votes_legit: int
    global_feature_importance: list[dict]


class FeastInfo(BaseModel):
    connected: bool


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    feast_connected: bool
    db_connected: bool
    version: str
