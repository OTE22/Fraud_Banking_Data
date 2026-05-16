import pandas as pd
import numpy as np


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates(subset=["step", "amount", "nameOrig", "nameDest"], keep="first")
    df = df[df["amount"] > 0]
    df = df.dropna(subset=["amount", "oldbalanceOrg", "newbalanceOrig"])
    return df


def normalize_amounts(df: pd.DataFrame, col: str = "amount") -> pd.Series:
    return np.log1p(df[col])
