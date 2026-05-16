import pandas as pd


def load_dataset(path: str, nrows: int | None = None) -> pd.DataFrame:
    return pd.read_csv(path, nrows=nrows)


def load_parquet_dataset(path: str) -> pd.DataFrame:
    return pd.read_parquet(path)
