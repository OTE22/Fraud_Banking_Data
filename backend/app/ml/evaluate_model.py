from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import numpy as np


def evaluate_model(model, X_test: np.ndarray, y_test: np.ndarray) -> dict:
    preds = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]
    tn, fp, fn, tp = confusion_matrix(y_test, preds).ravel()
    return {
        "classification_report": classification_report(y_test, preds, output_dict=True),
        "confusion_matrix": {"tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)},
        "roc_auc": round(roc_auc_score(y_test, proba), 4),
        "fraud_recall": round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0,
        "false_positive_rate": round(fp / (fp + tn), 4) if (fp + tn) > 0 else 0,
    }
