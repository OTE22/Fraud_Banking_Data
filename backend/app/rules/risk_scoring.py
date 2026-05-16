from app.rules.rules_engine import evaluate_rules


def compute_risk_score(transaction, ml_probability: float, anomaly_score: float = 0.0) -> dict:
    rules_score, triggered_rules = evaluate_rules(transaction)
    weighted = ml_probability * 0.5 + rules_score * 0.3 + anomaly_score * 0.2
    return {
        "final_score": round(weighted, 4),
        "ml_component": round(ml_probability, 4),
        "rules_component": round(rules_score, 4),
        "anomaly_component": round(anomaly_score, 4),
        "triggered_rules": triggered_rules,
        "decision": "block" if weighted > 0.6 else ("review" if weighted > 0.3 else "allow"),
    }
