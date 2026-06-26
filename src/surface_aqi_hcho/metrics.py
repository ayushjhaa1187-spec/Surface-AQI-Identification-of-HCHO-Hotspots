"""Model evaluation metrics for surface pollutant prediction."""

from __future__ import annotations

import numpy as np


def regression_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute RMSE, MAE, bias and Pearson R for model validation."""

    observed = np.asarray(y_true, dtype=float)
    predicted = np.asarray(y_pred, dtype=float)
    mask = ~(np.isnan(observed) | np.isnan(predicted))
    observed = observed[mask]
    predicted = predicted[mask]

    if observed.size == 0:
        raise ValueError("At least one valid observation/prediction pair is required")

    error = predicted - observed
    pearson_r = float(np.corrcoef(observed, predicted)[0, 1]) if observed.size > 1 else np.nan
    return {
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mae": float(np.mean(np.abs(error))),
        "bias": float(np.mean(error)),
        "pearson_r": pearson_r,
        "n": int(observed.size),
    }
