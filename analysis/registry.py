"""
The registry is the ONE place that wires an analysis module into the app.

To swap an algorithm: edit the corresponding module file (e.g. trend.py),
not this file. To add a brand new algorithm: write a new module with an
analyze(df, value_col) -> dict function, then add one line below.
Everything else (tool schemas, the LLM's ability to call it, the app)
picks it up automatically.
"""
from analysis import trend, seasonality, anomaly, changepoint

ANALYSES = {
    "trend": {
        "func": trend.analyze,
        "description": "Get the overall trend direction and % change over the period.",
    },
    "seasonality": {
        "func": seasonality.analyze,
        "description": "Detect weekly seasonality - which days run high/low.",
    },
    "anomaly": {
        "func": anomaly.analyze,
        "description": "Find statistical outlier days (spikes/dips) via z-score.",
    },
    "changepoint": {
        "func": changepoint.analyze,
        "description": "Find days where the underlying trend visibly shifted.",
    },
}
