AVERAGE_THRESHOLD = 0.5
MULTIPLIER = 1


def ensemble_score(ml_score: float, rules_score: float, anomaly_score: float) -> dict:
    final = ml_score * 0.4 + rules_score * 0.35 + anomaly_score * 0.25
    return {"final_score": round(final, 4), "decision": "fraud" if final > AVERAGE_THRESHOLD else "legitimate"}
