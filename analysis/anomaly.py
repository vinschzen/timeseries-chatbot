"""
Anomaly detection via z-score on residuals (value minus rolling mean).

Swap-out note: replace analyze()'s body with IsolationForest or
a rolling-IQR method if you want something fancier - the return shape
(list of dicts with date/value/z_score) is the contract the rest of
the app relies on.
"""
import numpy as np


def analyze(df, value_col: str, threshold: float = 2.5) -> dict:
    values = df[value_col]
    rolling_mean = values.rolling(window=14, min_periods=1, center=True).mean()
    residual = values - rolling_mean
    z_scores = (residual - residual.mean()) / residual.std()

    flagged = df.loc[z_scores.abs() > threshold].copy()
    flagged["z_score"] = z_scores[z_scores.abs() > threshold].round(2)

    anomalies = []
    for _, row in flagged.iterrows():
        entry = {
            "date": row["date"].strftime("%Y-%m-%d"),
            "value": round(row[value_col], 1),
            "z_score": float(row["z_score"]),
        }
        # surface any other columns (e.g. promo_flag) so the LLM
        # can try to explain the anomaly instead of guessing blind
        extra_cols = [c for c in df.columns if c not in ("date", value_col)]
        for c in extra_cols:
            entry[c] = row[c]
        anomalies.append(entry)

    return {
        "threshold_z": threshold,
        "count": len(anomalies),
        "anomalies": anomalies,
    }
