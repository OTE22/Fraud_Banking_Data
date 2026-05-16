from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np


def segment_customers(features: np.ndarray, n_clusters: int = 4) -> dict:
    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X)
    return {
        "labels": labels.tolist(),
        "centroids": model.cluster_centers_.tolist(),
        "inertia": float(model.inertia_),
        "n_clusters": n_clusters,
    }
