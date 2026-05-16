import pandas as pd
from datetime import datetime, timedelta


def compute_night_activity_ratio(tx_df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.Series:
    hours = pd.to_datetime(tx_df[timestamp_col]).dt.hour
    return (hours < 6).astype(float).groupby(tx_df.get("customer_id")).transform("mean")


def compute_weekend_activity_ratio(tx_df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.Series:
    days = pd.to_datetime(tx_df[timestamp_col]).dt.dayofweek
    return (days >= 5).astype(float).groupby(tx_df.get("customer_id")).transform("mean")


def compute_time_since_last_tx(tx_df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.Series:
    sorted_df = tx_df.sort_values(timestamp_col)
    return sorted_df.groupby("customer_id")[timestamp_col].diff().dt.total_seconds().fillna(0)
