import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

print("Loading data...")
df = pd.read_csv("AIML Dataset.csv", nrows=200000)

print("Engineering features...")
type_encoder = LabelEncoder()
df["type_encoded"] = type_encoder.fit_transform(df["type"])

feature_cols = [
    "step", "amount", "oldbalanceOrg", "newbalanceOrig",
    "oldbalanceDest", "newbalanceDest", "isFlaggedFraud", "type_encoded",
]
X = df[feature_cols].copy()
y = df["isFraud"].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

print(f"Training on {len(X)} samples (fraud rate: {y.mean():.4f})...")
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)
model = RandomForestClassifier(
    n_estimators=100, max_depth=12, class_weight="balanced",
    n_jobs=-1, random_state=42,
)
model.fit(X_train, y_train)

acc = model.score(X_test, y_test)
print(f"Test accuracy: {acc:.4f}")

artifact = {
    "model": model,
    "scaler": scaler,
    "type_encoder": type_encoder,
    "feature_cols": feature_cols,
}
joblib.dump(artifact, "backend/models/fraud_model.pkl")
print("Model saved to backend/models/fraud_model.pkl")
