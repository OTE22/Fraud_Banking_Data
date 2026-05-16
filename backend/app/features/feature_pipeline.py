import pandas as pd
import numpy as np
from app.features.feature_engineering import encode_transaction_type, compute_balance_change
from app.features.temporal_features import compute_night_activity_ratio
from app.features.graph_features import build_transaction_graph


def run_feature_pipeline(df: pd.DataFrame) -> np.ndarray:
    df = df.copy()
    df["type_encoded"] = encode_transaction_type(df["type"])
    df["balance_change_orig"] = df.apply(lambda r: compute_balance_change(r["oldbalanceOrg"], r["newbalanceOrig"]), axis=1)
    df["balance_change_dest"] = df.apply(lambda r: compute_balance_change(r["oldbalanceDest"], r["newbalanceDest"]), axis=1)
    df["amount_to_balance_ratio"] = df["amount"] / (df["oldbalanceOrg"] + 1)
    feature_cols = ["step", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest", "isFlaggedFraud", "type_encoded", "balance_change_orig", "balance_change_dest", "amount_to_balance_ratio"]
    return df[feature_cols].values
