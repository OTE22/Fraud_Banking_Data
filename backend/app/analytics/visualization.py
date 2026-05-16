import pandas as pd
import matplotlib.pyplot as plt
import io
import base64


def plot_to_b64(fig: plt.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()


def plot_risk_distribution(scores: list[float]) -> str:
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.hist(scores, bins=20, color="#6366f1", alpha=0.7)
    ax.set_xlabel("Risk Score"); ax.set_ylabel("Frequency")
    return plot_to_b64(fig)
