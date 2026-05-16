from sklearn.feature_selection import SelectKBest, mutual_info_classif
import numpy as np


def select_top_features(X: np.ndarray, y: np.ndarray, feature_names: list[str], k: int = 8) -> tuple[list[str], np.ndarray]:
    selector = SelectKBest(mutual_info_classif, k=min(k, X.shape[1]))
    X_selected = selector.fit_transform(X, y)
    scores = selector.scores_
    top_indices = np.argsort(scores)[::-1][:k]
    return [feature_names[i] for i in top_indices], X_selected
