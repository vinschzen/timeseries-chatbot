"""
Trend detection.

Every analysis module in this folder follows the same shape on purpose:

    def analyze(df, value_col: str) -> dict

so you can swap the implementation (e.g. linear regression -> Theil-Sen,
or a smarter slope estimator) without touching anything else in the app.
The registry.py file is the only place that needs to know this function
exists.
"""
import numpy as np


def analyze(df, value_col: str) -> dict:
    y = df[value_col].to_numpy()
    x = np.arange(len(y))

    # simplest possible trend line: least-squares slope
    slope, intercept = np.polyfit(x, y, 1)

    start_val = slope * x[0] + intercept
    end_val = slope * x[-1] + intercept
    pct_change = (end_val - start_val) / start_val * 100

    direction = "flat"
    if pct_change > 2:
        direction = "upward"
    elif pct_change < -2:
        direction = "downward"

    return {
        "direction": direction,
        "pct_change_over_period": round(pct_change, 1),
        "slope_per_day": round(float(slope), 3),
    }
