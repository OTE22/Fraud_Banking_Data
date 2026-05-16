from prometheus_client import Counter, Histogram, generate_latest

PREDICTIONS_TOTAL = Counter("fraud_predictions_total", "Total predictions", ["model_version"])
FRAUD_DETECTED = Counter("fraud_detected_total", "Fraud detected", ["model_version"])
PREDICTION_LATENCY = Histogram("fraud_prediction_latency_seconds", "Prediction latency")


def get_metrics():
    return generate_latest()
