import pandas as pd
import numpy as np
import joblib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from pathlib import Path

DATA_PATH = Path("backend/data/customers.csv")
MODEL_PATH = Path("backend/models/segmentation_model.pkl")
N_CLUSTERS = 4
RANDOM_SEED = 42

df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} customer records")

feature_cols = [
    "age", "annual_income", "credit_score", "account_balance",
    "tenure_months", "transaction_frequency_30d",
    "avg_transaction_amount", "num_fraudulent_tx_90d",
    "high_risk_flag",
]
print(f"Feature columns: {feature_cols}")

X = df[feature_cols].fillna(0).values.astype(np.float64)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

pca = PCA(n_components=min(4, len(feature_cols)), random_state=RANDOM_SEED)
X_pca = pca.fit_transform(X_scaled)

model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED, n_init=10)
print(f"Training KMeans with {N_CLUSTERS} clusters on {len(X_scaled)} samples...")
labels = model.fit_predict(X_scaled)

for i in range(N_CLUSTERS):
    count = int((labels == i).sum())
    print(f"  Cluster {i}: {count} customers ({count/len(labels)*100:.1f}%)")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
segment_labels = {
    0: "low_risk",
    1: "medium_risk",
    2: "high_risk",
    3: "critical_risk",
}
artifact = {
    "model": model,
    "scaler": scaler,
    "pca": pca,
    "feature_cols": feature_cols,
    "n_clusters": N_CLUSTERS,
    "segment_labels": segment_labels,
    "cluster_stats": {
        int(i): {
            "count": int((labels == i).sum()),
            "pct": float((labels == i).sum() / len(labels) * 100),
            "label": segment_labels.get(i, f"cluster_{i}"),
        }
        for i in range(N_CLUSTERS)
    },
}
joblib.dump(artifact, MODEL_PATH)
print(f"Segmentation model saved to {MODEL_PATH}")
