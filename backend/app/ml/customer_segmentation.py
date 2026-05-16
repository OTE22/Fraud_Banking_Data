from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import numpy as np
import joblib
from pathlib import Path
from app.core.logging import LOGGER


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


def load_segmentation_model(path: str | Path) -> dict | None:
    p = Path(path)
    if not p.exists():
        LOGGER.warning("segmentation_model_not_found", path=str(p))
        return None
    artifact = joblib.load(p)
    LOGGER.info("segmentation_model_loaded", path=str(p))
    return artifact


def segment_with_pretrained(features: np.ndarray, artifact: dict) -> dict:
    scaler = artifact["scaler"]
    model = artifact["model"]
    pca = artifact.get("pca")
    feature_cols = artifact.get("feature_cols")
    labels = artifact.get("segment_labels", {})

    X = scaler.transform(features)
    preds = model.predict(X)
    centroids = model.cluster_centers_.tolist()

    result = {
        "labels": [int(p) for p in preds],
        "centroids": centroids,
        "inertia": float(model.inertia_),
        "n_clusters": artifact["n_clusters"],
        "segment_labels": labels,
        "cluster_stats": artifact.get("cluster_stats", {}),
    }
    if pca is not None:
        result["pca_components"] = pca.components_.tolist()
        result["pca_explained_variance"] = pca.explained_variance_ratio_.tolist()
    if feature_cols:
        result["feature_columns"] = feature_cols
    return result
