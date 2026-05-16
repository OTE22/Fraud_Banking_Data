import joblib
import numpy as np
from pathlib import Path
from datetime import datetime
from app.config import get_settings
from app.core.logging import LOGGER
from app.domain.schemas import TransactionInput, PredictionOutput


class FraudPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.type_encoder = None
        self.feature_cols = None
        self._load_model()

    def _load_model(self) -> None:
        path = Path(get_settings().model_path)
        if path.exists():
            artifact = joblib.load(path)
            self.model = artifact["model"]
            self.scaler = artifact["scaler"]
            self.type_encoder = artifact["type_encoder"]
            self.feature_cols = artifact["feature_cols"]
            LOGGER.info("model_loaded", path=str(path))
        else:
            LOGGER.warning("model_not_found", path=str(path))

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def _build_features(self, tx: TransactionInput) -> np.ndarray:
        type_encoded = self.type_encoder.transform([tx.transaction_type])[0]
        raw = np.array([[
            tx.step, tx.amount, tx.oldbalance_orig, tx.newbalance_orig,
            tx.oldbalance_dest, tx.newbalance_dest,
            int(tx.is_flagged_fraud), type_encoded,
        ]])
        return self.scaler.transform(raw)

    def predict(self, tx: TransactionInput) -> PredictionOutput:
        if not self.loaded:
            return PredictionOutput(
                transaction_id=tx.transaction_id, fraud_probability=0.0,
                is_fraudulent=False, model_version="unavailable", timestamp=datetime.utcnow(),
            )
        X = self._build_features(tx)
        proba = self.model.predict_proba(X)[0, 1]
        pred = bool(self.model.predict(X)[0])
        LOGGER.info("prediction_made", tx_id=tx.transaction_id, proba=round(proba, 4))
        return PredictionOutput(
            transaction_id=tx.transaction_id, fraud_probability=round(float(proba), 4),
            is_fraudulent=pred, model_version="v1.0", timestamp=datetime.utcnow(),
        )

    def predict_with_detail(self, tx: TransactionInput) -> tuple:
        if not self.loaded:
            return PredictionOutput(
                transaction_id=tx.transaction_id, fraud_probability=0.0,
                is_fraudulent=False, model_version="unavailable", timestamp=datetime.utcnow(),
            ), {}
        type_encoded = self.type_encoder.transform([tx.transaction_type])[0]
        raw_values = [
            tx.step, tx.amount, tx.oldbalance_orig, tx.newbalance_orig,
            tx.oldbalance_dest, tx.newbalance_dest, int(tx.is_flagged_fraud),
        ]
        raw = np.array([raw_values + [type_encoded]])
        scaled = self.scaler.transform(raw)
        proba = self.model.predict_proba(scaled)[0, 1]
        pred = bool(self.model.predict(scaled)[0])
        trees_fraud = sum(1 for t in self.model.estimators_ if t.predict(scaled)[0] == 1)
        features_detail = [
            {"name": f, "raw_value": float(raw[0, i]), "scaled_value": float(scaled[0, i])}
            for i, f in enumerate(self.feature_cols)
        ]
        detail = {
            "input_raw": tx.model_dump(), "encoded_type": tx.transaction_type,
            "encoded_type_value": int(type_encoded), "features": features_detail,
            "fraud_probability": round(float(proba), 4), "is_fraudulent": pred,
            "model_version": "v1.0",
            "tree_votes_fraud": trees_fraud,
            "tree_votes_legit": len(self.model.estimators_) - trees_fraud,
            "global_feature_importance": [
                {"feature": f, "importance": round(float(v), 4)}
                for f, v in zip(self.feature_cols, self.model.feature_importances_)
            ],
        }
        LOGGER.info("prediction_detail", tx_id=tx.transaction_id, proba=round(proba, 4))
        return PredictionOutput(
            transaction_id=tx.transaction_id, fraud_probability=round(float(proba), 4),
            is_fraudulent=pred, model_version="v1.0", timestamp=datetime.utcnow(),
        ), detail


PREDICTOR = FraudPredictor()
