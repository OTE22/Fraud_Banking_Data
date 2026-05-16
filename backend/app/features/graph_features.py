import pandas as pd
from collections import defaultdict


def build_transaction_graph(transactions: pd.DataFrame) -> dict:
    graph: dict[str, set[str]] = defaultdict(set)
    for _, row in transactions.iterrows():
        graph[str(row.get("nameOrig", ""))].add(str(row.get("nameDest", "")))
    return dict(graph)


def detect_fraud_rings(graph: dict, min_cycle_size: int = 3) -> list[list[str]]:
    rings = []
    visited = set()
    for node in graph:
        if node in visited:
            continue
        component = []
        stack = [node]
        while stack:
            current = stack.pop()
            if current in visited:
                continue
            visited.add(current)
            component.append(current)
            stack.extend(graph.get(current, set()) - visited)
        if len(component) >= min_cycle_size:
            rings.append(component)
    return rings


def compute_shared_device_count(device_map: dict[str, list[str]]) -> dict[str, int]:
    return {dev: len(users) for dev, users in device_map.items()}
