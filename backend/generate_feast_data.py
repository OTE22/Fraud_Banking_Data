import pandas as pd
import numpy as np
from datetime import datetime, timezone

print("Generating Feast feature data from raw CSV...")
df = pd.read_csv("AIML Dataset.csv", nrows=100000)
now = datetime.now(timezone.utc)

# Customer features: aggregate per customer
cust = df.groupby("nameOrig").agg(
    avg_transaction_amount_30d=("amount", "mean"),
    transaction_count_30d=("amount", "count"),
    is_high_risk_merchant_30d=("isFraud", lambda x: x.mean() > 0.01),
).reset_index()
cust.rename(columns={"nameOrig": "customer_id"}, inplace=True)
cust["event_timestamp"] = now
cust.to_parquet("backend/feature_repo/data/customer_features.parquet", index=False)
print(f"Customer features: {len(cust)} rows")

# Merchant-like features from destination
merch = df[df["nameDest"].str.startswith("M")].groupby("nameDest").agg(
    avg_merchant_amount=("amount", "mean"),
    merchant_fraud_rate_7d=("isFraud", "mean"),
).reset_index()
merch.rename(columns={"nameDest": "merchant_id"}, inplace=True)
merch["event_timestamp"] = now
merch.to_parquet("backend/feature_repo/data/merchant_features.parquet", index=False)
print(f"Merchant features: {len(merch)} rows")

# Customer profile features for segmentation model
customers_csv = "backend/data/customers.csv"
cust_profiles = pd.read_csv(customers_csv, nrows=5000)
cust_profiles.rename(columns={"customer_id": "customer_id"}, inplace=True)
seg_features = [
    "age", "annual_income", "credit_score", "account_balance",
    "tenure_months", "transaction_frequency_30d",
    "avg_transaction_amount", "num_fraudulent_tx_90d",
    "high_risk_flag",
]
available = [c for c in seg_features if c in cust_profiles.columns]
cust_profiles["segment_label"] = 0
cust_profiles["event_timestamp"] = now
cols = ["customer_id"] + available + ["segment_label", "event_timestamp"]
cust_profiles[cols].to_parquet("backend/feature_repo/data/customer_profile_features.parquet", index=False)
print(f"Customer profiles: {len(cust_profiles)} rows, features={available}")

# Anomaly engineered features from transactions
tx = df.head(20000).copy()
tx["log_amount"] = np.log1p(tx["amount"])
tx["balance_diff_orig"] = tx["oldbalanceOrg"] - tx["newbalanceOrig"]
tx["balance_diff_dest"] = tx["newbalanceDest"] - tx["oldbalanceDest"]
tx["amt_to_balance_ratio"] = tx["amount"] / (tx["oldbalanceOrg"] + 1)
tx["anomaly_score"] = 0.0
engineered = [
    "amount", "log_amount", "balance_diff_orig", "balance_diff_dest",
    "amt_to_balance_ratio", "oldbalanceOrg", "newbalanceOrig",
    "oldbalanceDest", "newbalanceDest", "anomaly_score",
]
available_tx = [c for c in engineered if c in tx.columns]
tx["transaction_id"] = tx.index.astype(str)
tx["event_timestamp"] = now
tx[["transaction_id"] + available_tx + ["event_timestamp"]].to_parquet(
    "backend/feature_repo/data/anomaly_features.parquet", index=False
)
print(f"Anomaly features: {len(tx)} rows, features={available_tx}")

# Sample transaction data for drift reference
df_sample = df.head(5000)
df_sample.to_csv("backend/feature_repo/data/transactions.csv", index=False)
print("Drift reference data saved")
print("Feast data generation complete")
