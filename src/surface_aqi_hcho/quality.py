"""Quality-control helpers for pollutant and satellite columns."""

from __future__ import annotations

from math import isnan
from typing import Mapping

DEFAULT_VALID_RANGES: dict[str, tuple[float, float]] = {
    "PM2.5": (0, 1000),
    "PM10": (0, 1500),
    "NO2": (0, 1000),
    "SO2": (0, 4000),
    "CO": (0, 100),
    "O3": (0, 1200),
    "NH3": (0, 3000),
    "HCHO": (-0.001, 0.1),
    "AOD": (0, 5),
}


def valid_value(name: str, value: float, ranges: Mapping[str, tuple[float, float]] | None = None) -> bool:
    """Return whether a value is finite and inside the configured physical range."""

    if value is None or isnan(float(value)):
        return False
    valid_ranges = ranges or DEFAULT_VALID_RANGES
    if name not in valid_ranges:
        return True
    low, high = valid_ranges[name]
    return low <= float(value) <= high


def filter_valid_measurements(
    measurements: Mapping[str, float],
    ranges: Mapping[str, tuple[float, float]] | None = None,
) -> dict[str, float]:
    """Drop invalid measurements while preserving valid pollutant/predictor values."""

    return {
        name: float(value)
        for name, value in measurements.items()
        if valid_value(name, float(value), ranges)
    }
