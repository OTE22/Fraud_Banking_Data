import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("Generating Feast feature data from raw CSV...")
df = pd.read_csv("AIML Dataset.csv", nrows=100000)

# Customer features: aggregate per customer
cust = df.groupby("nameOrig").agg(
    avg_transaction_amount_30d=("amount", "mean"),
    transaction_count_30d=("amount", "count"),
    is_high_risk_merchant_30d=("isFraud", lambda x: x.mean() > 0.01),
).reset_index()
cust.rename(columns={"nameOrig": "customer_id"}, inplace=True)
cust["event_timestamp"] = datetime.utcnow()
cust.to_parquet("backend/feature_repo/data/customer_features.parquet", index=False)
print(f"Customer features: {len(cust)} rows")

# Merchant-like features from destination
merch = df[df["nameDest"].str.startswith("M")].groupby("nameDest").agg(
    avg_merchant_amount=("amount", "mean"),
    merchant_fraud_rate_7d=("isFraud", "mean"),
).reset_index()
merch.rename(columns={"nameDest": "merchant_id"}, inplace=True)
merch["event_timestamp"] = datetime.utcnow()
merch.to_parquet("backend/feature_repo/data/merchant_features.parquet", index=False)
print(f"Merchant features: {len(merch)} rows")

# Sample transaction data for drift reference
df_sample = df.head(5000)
df_sample.to_csv("backend/feature_repo/data/transactions.csv", index=False)
print("Drift reference data saved")
