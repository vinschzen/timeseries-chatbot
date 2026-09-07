"""
Weekly seasonality detection via classical decomposition.

Swap-out note: if you don't want the statsmodels dependency, replace
the body of analyze() with a simple groupby(weekday).mean() comparison
- the return shape below is all the rest of the app cares about.
"""
from statsmodels.tsa.seasonal import seasonal_decompose


def analyze(df, value_col: str) -> dict:
    series = df[value_col]

    if len(series) < 14:
        return {"detected": False, "reason": "not enough data (need 2+ weeks)"}

    result = seasonal_decompose(series, model="additive", period=7, extrapolate_trend="period")
    seasonal = result.seasonal

    # which weekday is strongest / weakest, on average
    df_local = df.copy()
    df_local["_seasonal"] = seasonal.values
    df_local["_weekday"] = df_local["date"].dt.day_name()
    by_weekday = df_local.groupby("_weekday")["_seasonal"].mean().round(1)

    strongest = by_weekday.idxmax()
    weakest = by_weekday.idxmin()
    amplitude = round(by_weekday.max() - by_weekday.min(), 1)

    return {
        "detected": amplitude > (series.std() * 0.1),  # rough significance check
        "strongest_day": strongest,
        "weakest_day": weakest,
        "amplitude": amplitude,
    }
