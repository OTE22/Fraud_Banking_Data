from datetime import datetime, timedelta


def detect_velocity_anomaly(transaction_times: list[datetime], threshold_minutes: int = 1) -> bool:
    if len(transaction_times) < 3:
        return False
    recent = [t for t in transaction_times if t > datetime.utcnow() - timedelta(minutes=5)]
    return len(recent) >= 3 and (max(recent) - min(recent)).total_seconds() < threshold_minutes * 60


def detect_impossible_travel(prev_location: tuple[float, float], new_location: tuple[float, float], time_diff_hours: float) -> bool:
    from math import radians, sin, cos, sqrt, atan2
    lat1, lon1 = map(radians, prev_location)
    lat2, lon2 = map(radians, new_location)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance_km = 6371 * c
    return distance_km / max(time_diff_hours, 0.1) > 900
