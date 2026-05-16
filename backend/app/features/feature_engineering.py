import pandas as pd
import numpy as np


def compute_transaction_velocity(tx_df: pd.DataFrame, window_minutes: int = 5) -> pd.Series:
    return tx_df.groupby("customer_id")["amount"].rolling(f"{window_minutes}T").count().reset_index(level=0, drop=True)


def compute_avg_spending_24h(tx_df: pd.DataFrame) -> pd.Series:
    return tx_df.groupby("customer_id")["amount"].rolling("24h").mean().reset_index(level=0, drop=True)


def encode_transaction_type(types: pd.Series) -> np.ndarray:
    mapping = {"PAYMENT": 0, "TRANSFER": 1, "CASH_OUT": 2, "CASH_IN": 3, "DEBIT": 4}
    return np.array([mapping.get(t, -1) for t in types])


def compute_balance_change(old_balance: float, new_balance: float) -> float:
    return old_balance - new_balance


def extract_hour_feature(timestamp_series: pd.Series) -> pd.Series:
    return pd.to_datetime(timestamp_series).dt.hour
