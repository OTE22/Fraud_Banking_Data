import numpy as np

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False


def explain_prediction(model, X: np.ndarray, feature_names: list[str]) -> dict:
    if not HAS_SHAP:
        return {"features": [{"feature": n, "shap_value": 0, "direction": "unknown"} for n in feature_names], "note": "shap not installed"}
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    if isinstance(shap_values, list):
        shap_values = shap_values[1]
    features = []
    for i, name in enumerate(feature_names):
        features.append({"feature": name, "shap_value": float(np.mean(np.abs(shap_values[:, i]))), "direction": "positive" if np.mean(shap_values[:, i]) > 0 else "negative"})
    return {"features": sorted(features, key=lambda x: x["shap_value"], reverse=True)}
