RULES: list[dict] = [
    {"name": "high_amount_transfer", "condition": lambda t: t.transaction_type == "TRANSFER" and t.amount > 500000, "score": 0.7},
    {"name": "flagged_fraud", "condition": lambda t: t.is_flagged_fraud, "score": 0.9},
    {"name": "zero_balance_after_transfer", "condition": lambda t: t.transaction_type in ("TRANSFER", "CASH_OUT") and t.newbalance_orig == 0 and t.amount > 100000, "score": 0.6},
    {"name": "rapid_succession", "condition": lambda t: t.step > 0 and t.step < 10, "score": 0.3},
    {"name": "large_cash_out", "condition": lambda t: t.transaction_type == "CASH_OUT" and t.amount > 200000, "score": 0.5},
]


def evaluate_rules(transaction) -> tuple[float, list[str]]:
    max_score = 0.0
    triggered = []
    for rule in RULES:
        try:
            if rule["condition"](transaction):
                max_score = max(max_score, rule["score"])
                triggered.append(rule["name"])
        except Exception:
            continue
    return max_score, triggered
