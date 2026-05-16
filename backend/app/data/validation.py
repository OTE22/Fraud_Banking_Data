import pandas as pd
import numpy as np


def validate_transaction(row: dict) -> list[str]:
    errors = []
    if row.get("amount", 0) <= 0:
        errors.append("Amount must be positive")
    if row.get("oldbalance_orig", -1) < 0 or row.get("newbalance_orig", -1) < 0:
        errors.append("Balances cannot be negative")
    if row.get("newbalance_orig", 0) > row.get("oldbalance_orig", 0) + row.get("amount", 0):
        errors.append("New balance exceeds old balance + amount")
    return errors
