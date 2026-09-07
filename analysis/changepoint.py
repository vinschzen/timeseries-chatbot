"""
Changepoint detection: finds days where the recent trend visibly shifts.

Deliberately simple (no `ruptures` dependency) - compares the mean of the
window before a point to the mean of the window after it, and flags the
biggest jumps. Swap-out note: if you want proper changepoint detection,
install `ruptures` and replace analyze()'s body; keep the same return shape.
"""
import numpy as np


def analyze(df, value_col: str, window: int = 14, top_n: int = 3) -> dict:
    values = df[value_col].to_numpy()
    n = len(values)

    if n < window * 2:
        return {"detected": False, "reason": "not enough data for this window size"}

    shifts = []
    for i in range(window, n - window):
        before = values[i - window:i].mean()
        after = values[i:i + window].mean()
        shifts.append(abs(after - before))

    shifts = np.array(shifts)
    top_idx = np.argsort(shifts)[-top_n:][::-1]

    changepoints = []
    for idx in top_idx:
        real_idx = idx + window  # offset back into original array
        changepoints.append({
            "date": df["date"].iloc[real_idx].strftime("%Y-%m-%d"),
            "shift_magnitude": round(float(shifts[idx]), 1),
        })

    return {"changepoints": changepoints}
