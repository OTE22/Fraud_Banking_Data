from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class PredictionModel(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_id = Column(String(100), nullable=False, index=True)
    fraud_probability = Column(Float, nullable=False)
    is_fraudulent = Column(Boolean, nullable=False)
    model_version = Column(String(20), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    input_json = Column(Text, nullable=True)
    detail_json = Column(Text, nullable=True)


class DriftReportModel(Base):
    __tablename__ = "drift_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total_features = Column(Integer, nullable=False)
    drifted_features = Column(Integer, nullable=False)
    drift_percentage = Column(Float, nullable=False)
    metrics_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
