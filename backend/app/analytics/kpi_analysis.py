from datetime import datetime, timedelta


def compute_fraud_rate(total: int, fraud_count: int) -> float:
    return round(fraud_count / total, 4) if total > 0 else 0.0


def compute_precision_recall(tp: int, fp: int, fn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    return {"precision": round(precision, 4), "recall": round(recall, 4), "f1": round(2 * precision * recall / (precision + recall), 4) if (precision + recall) > 0 else 0}


def compute_detection_latency(timestamps: list[datetime]) -> float:
    if len(timestamps) < 2:
        return 0
    latencies = [(timestamps[i] - timestamps[i - 1]).total_seconds() * 1000 for i in range(1, len(timestamps))]
    return round(sum(latencies) / len(latencies), 2)
