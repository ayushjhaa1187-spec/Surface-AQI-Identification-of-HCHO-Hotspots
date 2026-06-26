"""Spatio-temporal collocation helpers for satellite, CPCB and meteorological records."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Iterable, Mapping

from surface_aqi_hcho.geo import haversine_km


@dataclass(frozen=True)
class PointRecord:
    """A lightweight point observation used for collocation."""

    record_id: str
    latitude: float
    longitude: float
    timestamp: datetime
    values: Mapping[str, float | str]


@dataclass(frozen=True)
class CollocatedRecord:
    """A station record paired with its nearest satellite/reanalysis record."""

    station: PointRecord
    match: PointRecord
    distance_km: float
    time_difference_minutes: float


def find_nearest_record(
    target: PointRecord,
    candidates: Iterable[PointRecord],
    max_distance_km: float = 25.0,
    max_time_difference: timedelta = timedelta(hours=3),
) -> CollocatedRecord | None:
    """Find the nearest candidate satisfying distance and time windows."""

    best: CollocatedRecord | None = None
    for candidate in candidates:
        time_difference = abs(candidate.timestamp - target.timestamp)
        if time_difference > max_time_difference:
            continue

        distance = haversine_km(
            target.latitude,
            target.longitude,
            candidate.latitude,
            candidate.longitude,
        )
        if distance > max_distance_km:
            continue

        time_minutes = time_difference.total_seconds() / 60
        record = CollocatedRecord(target, candidate, distance, time_minutes)
        if best is None or (record.distance_km, record.time_difference_minutes) < (
            best.distance_km,
            best.time_difference_minutes,
        ):
            best = record

    return best


def collocate_records(
    stations: Iterable[PointRecord],
    candidates: Iterable[PointRecord],
    max_distance_km: float = 25.0,
    max_time_difference: timedelta = timedelta(hours=3),
) -> list[CollocatedRecord]:
    """Collocate each station record with the nearest satellite/reanalysis record."""

    candidate_list = list(candidates)
    matches: list[CollocatedRecord] = []
    for station in stations:
        match = find_nearest_record(station, candidate_list, max_distance_km, max_time_difference)
        if match is not None:
            matches.append(match)
    return matches
