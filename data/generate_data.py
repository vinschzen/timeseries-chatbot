"""
Generates data/sales.csv — a fake but realistic daily sales series.
Run once: python data/generate_data.py

Has three ingredients on purpose, so the analysis layer has
something real to find:
  - an upward trend
  - weekly seasonality (weekends dip)
  - a handful of injected anomalies/spikes (e.g. promo days)
"""
import numpy as np
import pandas as pd

np.random.seed(42)

N_DAYS = 365
start = pd.Timestamp("2025-01-01")
dates = pd.date_range(start, periods=N_DAYS, freq="D")

trend = np.linspace(1000, 1800, N_DAYS)                 # slow growth
weekday_effect = np.where(dates.weekday >= 5, -150, 0)   # weekends dip
noise = np.random.normal(0, 60, N_DAYS)

sales = trend + weekday_effect + noise

# inject a few anomalies (promo spikes) with a flag column,
# so the LLM has something to correlate the anomaly with
promo_flag = np.zeros(N_DAYS, dtype=int)
promo_days = [45, 46, 130, 200, 201, 300]
for d in promo_days:
    sales[d] += np.random.uniform(500, 700)
    promo_flag[d] = 1

# one unexplained anomaly (no promo flag) — a good test case
sales[260] += 800

df = pd.DataFrame({
    "date": dates,
    "sales": sales.round(2),
    "promo_flag": promo_flag,
})

df.to_csv("data/sales.csv", index=False)
print(f"Wrote data/sales.csv with {len(df)} rows")
