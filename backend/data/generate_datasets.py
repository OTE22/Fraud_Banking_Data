import numpy as np
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent
N_TRANSACTIONS = 200_000
N_CUSTOMERS = 10_000
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)


def generate_transactions() -> pd.DataFrame:
    n = N_TRANSACTIONS
    types = np.random.choice(
        ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"],
        size=n, p=[0.3, 0.2, 0.25, 0.15, 0.1]
    )
    amounts = np.random.lognormal(mean=5.0, sigma=2.0, size=n)
    amounts = np.clip(amounts, 1, 10_000_000)

    old_balance_orig = np.random.lognormal(mean=8.0, sigma=2.5, size=n)
    new_balance_orig = old_balance_orig - amounts
    new_balance_orig = np.clip(new_balance_orig, 0, None)

    old_balance_dest = np.random.lognormal(mean=8.0, sigma=2.5, size=n)
    new_balance_dest = old_balance_dest + amounts

    is_fraud = np.zeros(n, dtype=int)
    fraud_mask = np.random.random(n) < 0.007
    n_fraud = fraud_mask.sum()
    is_fraud[fraud_mask] = 1

    old_balance_orig[fraud_mask] = np.random.lognormal(mean=10.0, sigma=2.0, size=n_fraud)
    new_balance_orig[fraud_mask] = np.clip(
        old_balance_orig[fraud_mask] - amounts[fraud_mask] * np.random.uniform(0.8, 1.2, size=n_fraud),
        0, None
    )
    is_flagged = np.zeros(n, dtype=int)
    is_flagged[(amounts > 200_000) & (is_fraud == 1)] = 1

    df = pd.DataFrame({
        "step": np.random.randint(1, 744, size=n),
        "type": types,
        "amount": amounts.round(2),
        "nameOrig": [f"CUST-{i:06d}" for i in np.random.randint(0, 1_000_000, size=n)],
        "oldbalanceOrg": old_balance_orig.round(2),
        "newbalanceOrig": new_balance_orig.round(2),
        "nameDest": [f"CUST-{i:06d}" for i in np.random.randint(0, 1_000_000, size=n)],
        "oldbalanceDest": old_balance_dest.round(2),
        "newbalanceDest": new_balance_dest.round(2),
        "isFraud": is_fraud,
        "isFlaggedFraud": is_flagged,
    })
    return df


def generate_customers() -> pd.DataFrame:
    n = N_CUSTOMERS
    ages = np.random.randint(18, 85, size=n).astype(float)
    income = np.random.lognormal(mean=10.5, sigma=0.8, size=n).round(2)
    credit_score = np.clip(np.random.normal(650, 100, size=n), 300, 850).round(0)
    account_balance = np.random.lognormal(mean=8.0, sigma=2.5, size=n).round(2)
    tenure_months = np.random.randint(1, 240, size=n)

    transaction_freq = np.random.poisson(lam=20, size=n)
    avg_tx_amount = np.random.lognormal(mean=5.0, sigma=1.5, size=n).round(2)
    n_fraud_tx = np.random.poisson(lam=0.1, size=n)

    high_risk = ((ages < 25) & (credit_score < 550)).astype(int)

    df = pd.DataFrame({
        "customer_id": [f"CUST-{i:08d}" for i in range(n)],
        "age": ages,
        "annual_income": income,
        "credit_score": credit_score,
        "account_balance": account_balance,
        "tenure_months": tenure_months,
        "transaction_frequency_30d": transaction_freq,
        "avg_transaction_amount": avg_tx_amount,
        "num_fraudulent_tx_90d": n_fraud_tx,
        "high_risk_flag": high_risk,
    })
    return df


def main():
    DATA_DIR.mkdir(exist_ok=True)
    print("Generating transaction dataset...")
    tx_df = generate_transactions()
    tx_path = DATA_DIR / "transactions.csv"
    tx_df.to_csv(tx_path, index=False)
    print(f"  -> {tx_path} ({len(tx_df)} rows, fraud rate: {tx_df['isFraud'].mean():.4f})")

    print("Generating customer dataset...")
    cust_df = generate_customers()
    cust_path = DATA_DIR / "customers.csv"
    cust_df.to_csv(cust_path, index=False)
    print(f"  -> {cust_path} ({len(cust_df)} rows)")

    print("Done. Datasets saved to", DATA_DIR)


if __name__ == "__main__":
    main()
