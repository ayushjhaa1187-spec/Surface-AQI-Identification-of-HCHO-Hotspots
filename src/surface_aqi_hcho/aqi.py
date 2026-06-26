"""Indian National Air Quality Index helper functions.

The breakpoints below follow the Central Pollution Control Board AQI structure for
common pollutants. They are intended for daily aggregated concentrations except CO
and O3, which are conventionally evaluated on shorter averaging windows before AQI
aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isnan
from typing import Mapping


@dataclass(frozen=True)
class Breakpoint:
    concentration_low: float
    concentration_high: float
    index_low: int
    index_high: int


AQI_BREAKPOINTS: dict[str, tuple[Breakpoint, ...]] = {
    "PM2.5": (
        Breakpoint(0, 30, 0, 50),
        Breakpoint(31, 60, 51, 100),
        Breakpoint(61, 90, 101, 200),
        Breakpoint(91, 120, 201, 300),
        Breakpoint(121, 250, 301, 400),
        Breakpoint(251, 500, 401, 500),
    ),
    "PM10": (
        Breakpoint(0, 50, 0, 50),
        Breakpoint(51, 100, 51, 100),
        Breakpoint(101, 250, 101, 200),
        Breakpoint(251, 350, 201, 300),
        Breakpoint(351, 430, 301, 400),
        Breakpoint(431, 600, 401, 500),
    ),
    "NO2": (
        Breakpoint(0, 40, 0, 50),
        Breakpoint(41, 80, 51, 100),
        Breakpoint(81, 180, 101, 200),
        Breakpoint(181, 280, 201, 300),
        Breakpoint(281, 400, 301, 400),
        Breakpoint(401, 800, 401, 500),
    ),
    "SO2": (
        Breakpoint(0, 40, 0, 50),
        Breakpoint(41, 80, 51, 100),
        Breakpoint(81, 380, 101, 200),
        Breakpoint(381, 800, 201, 300),
        Breakpoint(801, 1600, 301, 400),
        Breakpoint(1601, 3200, 401, 500),
    ),
    "CO": (
        Breakpoint(0, 1, 0, 50),
        Breakpoint(1.1, 2, 51, 100),
        Breakpoint(2.1, 10, 101, 200),
        Breakpoint(10.1, 17, 201, 300),
        Breakpoint(17.1, 34, 301, 400),
        Breakpoint(34.1, 50, 401, 500),
    ),
    "O3": (
        Breakpoint(0, 50, 0, 50),
        Breakpoint(51, 100, 51, 100),
        Breakpoint(101, 168, 101, 200),
        Breakpoint(169, 208, 201, 300),
        Breakpoint(209, 748, 301, 400),
        Breakpoint(749, 1000, 401, 500),
    ),
    "NH3": (
        Breakpoint(0, 200, 0, 50),
        Breakpoint(201, 400, 51, 100),
        Breakpoint(401, 800, 101, 200),
        Breakpoint(801, 1200, 201, 300),
        Breakpoint(1201, 1800, 301, 400),
        Breakpoint(1801, 2400, 401, 500),
    ),
}

AQI_CATEGORIES: tuple[tuple[int, int, str], ...] = (
    (0, 50, "Good"),
    (51, 100, "Satisfactory"),
    (101, 200, "Moderate"),
    (201, 300, "Poor"),
    (301, 400, "Very Poor"),
    (401, 500, "Severe"),
)


def calculate_pollutant_sub_index(pollutant: str, concentration: float) -> float | None:
    """Return the AQI sub-index for one pollutant concentration.

    Parameters
    ----------
    pollutant:
        Pollutant key such as ``PM2.5``, ``PM10``, ``NO2``, ``SO2``, ``CO``, ``O3`` or
        ``NH3``.
    concentration:
        Pollutant concentration in the units expected by the CPCB AQI breakpoints.
    """

    if concentration is None or isnan(float(concentration)) or concentration < 0:
        return None

    breakpoints = AQI_BREAKPOINTS[pollutant.upper()]
    for breakpoint in breakpoints:
        if breakpoint.concentration_low <= concentration <= breakpoint.concentration_high:
            return _linear_sub_index(concentration, breakpoint)

    return 500.0


def calculate_aqi(concentrations: Mapping[str, float]) -> dict[str, float | str | None]:
    """Calculate overall AQI as the maximum valid pollutant sub-index."""

    sub_indices: dict[str, float] = {}
    for pollutant, concentration in concentrations.items():
        key = pollutant.upper()
        if key in AQI_BREAKPOINTS:
            sub_index = calculate_pollutant_sub_index(key, float(concentration))
            if sub_index is not None:
                sub_indices[key] = sub_index

    if not sub_indices:
        return {"aqi": None, "category": None, "dominant_pollutant": None}

    dominant_pollutant = max(sub_indices, key=sub_indices.get)
    aqi = round(sub_indices[dominant_pollutant])
    return {
        "aqi": aqi,
        "category": categorize_aqi(aqi),
        "dominant_pollutant": dominant_pollutant,
        **{f"{pollutant}_sub_index": value for pollutant, value in sub_indices.items()},
    }


def categorize_aqi(aqi: float) -> str:
    """Convert an AQI number to its Indian AQI category."""

    for low, high, category in AQI_CATEGORIES:
        if low <= aqi <= high:
            return category
    return "Severe"


def _linear_sub_index(concentration: float, breakpoint: Breakpoint) -> float:
    return (
        (breakpoint.index_high - breakpoint.index_low)
        / (breakpoint.concentration_high - breakpoint.concentration_low)
        * (concentration - breakpoint.concentration_low)
        + breakpoint.index_low
    )
