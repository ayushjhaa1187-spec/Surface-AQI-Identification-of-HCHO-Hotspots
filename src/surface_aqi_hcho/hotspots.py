"""HCHO hotspot detection and fire relationship utilities."""

from __future__ import annotations

import numpy as np
import pandas as pd


def detect_hotspots(
    frame: pd.DataFrame,
    value_column: str = "hcho_column",
    group_columns: tuple[str, ...] = ("month",),
    zscore_threshold: float = 2.0,
    quantile_threshold: float = 0.90,
) -> pd.DataFrame:
    """Flag HCHO hotspots using grouped z-score and quantile thresholds.

    A row is considered a hotspot when its value is greater than or equal to the
    selected group quantile and its standardized anomaly is greater than or equal
    to ``zscore_threshold``. Grouping by month supports seasonal baselines.
    """

    if value_column not in frame.columns:
        raise ValueError(f"Missing value column: {value_column}")

    result = frame.copy()
    grouped = result.groupby(list(group_columns), dropna=False)[value_column]
    result["hcho_group_mean"] = grouped.transform("mean")
    result["hcho_group_std"] = grouped.transform("std").replace(0, np.nan)
    result["hcho_zscore"] = (result[value_column] - result["hcho_group_mean"]) / result[
        "hcho_group_std"
    ]
    result["hcho_quantile_threshold"] = grouped.transform(lambda values: values.quantile(quantile_threshold))
    result["is_hcho_hotspot"] = (
        (result[value_column] >= result["hcho_quantile_threshold"])
        & (result["hcho_zscore"] >= zscore_threshold)
    )
    return result


def correlate_fire_hcho(
    frame: pd.DataFrame,
    hcho_column: str = "hcho_column",
    fire_column: str = "fire_count",
) -> dict[str, float | int]:
    """Return Pearson correlation between fire counts and HCHO columns."""

    valid = frame[[hcho_column, fire_column]].dropna()
    if len(valid) < 2:
        return {"n": len(valid), "pearson_r": np.nan}

    return {"n": len(valid), "pearson_r": float(valid[hcho_column].corr(valid[fire_column]))}
