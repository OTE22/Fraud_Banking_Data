import joblib
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from app.config import get_settings
from app.core.logging import LOGGER
from app.domain.schemas import TransactionInput, PredictionOutput


class FraudPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.type_encoder = None
        self.feature_cols = None
        self.anomaly_model = None
        self.anomaly_scaler = None
        self.anomaly_feature_cols = None
        self._load_model()
        self._load_anomaly_model()

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

    def _load_anomaly_model(self) -> None:
        path = Path(get_settings().anomaly_model_path)
        if path.exists():
            artifact = joblib.load(path)
            self.anomaly_model = artifact["model"]
            self.anomaly_scaler = artifact.get("scaler")
            self.anomaly_feature_cols = artifact.get("feature_cols")
            LOGGER.info("anomaly_model_loaded", path=str(path), feat_cols=self.anomaly_feature_cols)
        else:
            LOGGER.warning("anomaly_model_not_found", path=str(path))

    @property
    def loaded(self) -> bool:
        return self.model is not None

    def _build_anomaly_features(self, tx: TransactionInput) -> np.ndarray:
        raw_vals = {
            "amount": tx.amount,
            "log_amount": np.log1p(tx.amount),
            "balance_diff_orig": tx.oldbalance_orig - tx.newbalance_orig,
            "balance_diff_dest": tx.newbalance_dest - tx.oldbalance_dest,
            "amt_to_balance_ratio": tx.amount / (tx.oldbalance_orig + 1),
            "oldbalanceOrg": tx.oldbalance_orig,
            "newbalanceOrig": tx.newbalance_orig,
            "oldbalanceDest": tx.oldbalance_dest,
            "newbalanceDest": tx.newbalance_dest,
        }
        cols = self.anomaly_feature_cols or list(raw_vals.keys())
        return np.array([[raw_vals[c] for c in cols]])

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
                is_fraudulent=False, model_version="unavailable", timestamp=datetime.now(timezone.utc),
            )
        X = self._build_features(tx)
        proba = self.model.predict_proba(X)[0, 1]
        pred = bool(self.model.predict(X)[0])
        LOGGER.info("prediction_made", tx_id=tx.transaction_id, proba=round(proba, 4))
        return PredictionOutput(
            transaction_id=tx.transaction_id, fraud_probability=round(float(proba), 4),
            is_fraudulent=pred, model_version="v1.0", timestamp=datetime.now(timezone.utc),
        )

    def predict_anomaly(self, tx: TransactionInput) -> float | None:
        if self.anomaly_model is None or self.anomaly_scaler is None:
            return None
        try:
            anom_raw = self._build_anomaly_features(tx)
            anom_scaled = self.anomaly_scaler.transform(anom_raw)
            return float(self.anomaly_model.score_samples(anom_scaled)[0])
        except Exception as e:
            LOGGER.warning("anomaly_predict_failed", error=str(e))
            return None

    def predict_with_detail(self, tx: TransactionInput) -> tuple:
        if not self.loaded:
            return PredictionOutput(
                transaction_id=tx.transaction_id, fraud_probability=0.0,
                is_fraudulent=False, model_version="unavailable", timestamp=datetime.now(timezone.utc),
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
        anomaly_score = None
        if self.anomaly_model is not None and self.anomaly_scaler is not None:
            try:
                anom_raw = self._build_anomaly_features(tx)
                anom_scaled = self.anomaly_scaler.transform(anom_raw)
                anomaly_score = float(self.anomaly_model.score_samples(anom_scaled)[0])
            except Exception as e:
                LOGGER.warning("anomaly_score_failed", error=str(e))

        detail = {
            "input_raw": tx.model_dump(), "encoded_type": tx.transaction_type,
            "encoded_type_value": int(type_encoded), "features": features_detail,
            "fraud_probability": round(float(proba), 4), "is_fraudulent": pred,
            "model_version": "v1.0",
            "tree_votes_fraud": trees_fraud,
            "tree_votes_legit": len(self.model.estimators_) - trees_fraud,
            "anomaly_score": anomaly_score,
            "global_feature_importance": [
                {"feature": f, "importance": round(float(v), 4)}
                for f, v in zip(self.feature_cols, self.model.feature_importances_)
            ],
        }
        LOGGER.info("prediction_detail", tx_id=tx.transaction_id, proba=round(proba, 4))
        return PredictionOutput(
            transaction_id=tx.transaction_id, fraud_probability=round(float(proba), 4),
            is_fraudulent=pred, model_version="v1.0", timestamp=datetime.now(timezone.utc),
        ), detail


PREDICTOR = FraudPredictor()
