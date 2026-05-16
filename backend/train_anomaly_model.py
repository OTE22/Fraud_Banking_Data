import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from pathlib import Path

DATA_PATH = Path("backend/data/transactions.csv")
MODEL_PATH = Path("backend/models/anomaly_model.pkl")
RANDOM_SEED = 42

df = pd.read_csv(DATA_PATH, nrows=200_000)
print(f"Loaded {len(df)} transactions (fraud rate: {df['isFraud'].mean():.4f})")

feature_cols = [
    "amount", "oldbalanceOrg", "newbalanceOrig",
    "oldbalanceDest", "newbalanceDest",
]
df["log_amount"] = np.log1p(df["amount"])
df["balance_diff_orig"] = df["oldbalanceOrg"] - df["newbalanceOrig"]
df["balance_diff_dest"] = df["newbalanceDest"] - df["oldbalanceDest"]
df["amt_to_balance_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1)

engineered_cols = [
    "amount", "log_amount", "balance_diff_orig", "balance_diff_dest",
    "amt_to_balance_ratio", "oldbalanceOrg", "newbalanceOrig",
    "oldbalanceDest", "newbalanceDest",
]
print(f"Feature columns: {engineered_cols}")

X = df[engineered_cols].fillna(0).values.astype(np.float64)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    n_estimators=100,
    contamination=0.01,
    max_samples=0.8,
    random_state=RANDOM_SEED,
    n_jobs=-1,
)
print("Training IsolationForest on", len(X_scaled), "samples...")
model.fit(X_scaled)

anomaly_preds = (model.predict(X_scaled) == -1).astype(int)
anomaly_rate = anomaly_preds.mean()
print(f"Anomaly rate: {anomaly_rate:.4f}")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
artifact = {
    "model": model,
    "scaler": scaler,
    "feature_cols": engineered_cols,
    "contamination": 0.01,
    "anomaly_rate": float(anomaly_rate),
}
joblib.dump(artifact, MODEL_PATH)
print(f"Anomaly model saved to {MODEL_PATH}")
