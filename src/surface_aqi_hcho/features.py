"""Feature engineering for AQI prediction and HCHO hotspot attribution."""

from __future__ import annotations

from datetime import date


def seasonal_label(day: date) -> str:
    """Return an India-focused seasonal label for a date."""

    month = day.month
    if month in (3, 4, 5):
        return "pre_monsoon"
    if month in (6, 7, 8, 9):
        return "monsoon"
    if month in (10, 11):
        return "post_monsoon"
    return "winter"


def add_temporal_features(day: date) -> dict[str, int | str]:
    """Create reusable calendar features for model training or aggregation."""

    return {
        "year": day.year,
        "month": day.month,
        "day_of_year": day.timetuple().tm_yday,
        "season": seasonal_label(day),
    }
