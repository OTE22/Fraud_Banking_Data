from sklearn.ensemble import IsolationForest
import numpy as np


class AnomalyDetector:
    def __init__(self, contamination: float = 0.01):
        self.model = IsolationForest(contamination=contamination, random_state=42)
        self.fitted = False

    def fit(self, X: np.ndarray) -> None:
        self.model.fit(X)
        self.fitted = True

    def predict(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        if not self.fitted:
            return np.zeros(len(X)), np.zeros(len(X))
        preds = self.model.predict(X)
        scores = self.model.score_samples(X)
        return (preds == -1).astype(float), scores
