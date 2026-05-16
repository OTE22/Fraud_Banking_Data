from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import numpy as np
import joblib
from pathlib import Path
from app.core.logging import LOGGER


class AnomalyDetector:
    def __init__(self, contamination: float = 0.01):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.scaler = StandardScaler()
        self.feature_cols = None
        self.fitted = False

    def fit(self, X: np.ndarray) -> None:
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.fitted = True

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if not self.fitted:
            return np.zeros(len(X)), np.zeros(len(X))
        X_scaled = self.scaler.transform(X)
        preds = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        return (preds == -1).astype(float), scores

    def load_pickle(self, path: str | Path) -> bool:
        p = Path(path)
        if not p.exists():
            LOGGER.warning("anomaly_model_not_found", path=str(p))
            return False
        artifact = joblib.load(p)
        self.model = artifact["model"]
        self.scaler = artifact.get("scaler", StandardScaler())
        self.feature_cols = artifact.get("feature_cols")
        self.fitted = True
        LOGGER.info("anomaly_model_loaded", path=str(p))
        return True


ANOMALY_DETECTOR = AnomalyDetector()
