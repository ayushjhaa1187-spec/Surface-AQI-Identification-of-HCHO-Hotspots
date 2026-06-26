"""Geospatial helper functions for India-focused satellite and station workflows."""

from __future__ import annotations

from math import asin, cos, radians, sin, sqrt

INDIA_BBOX = {"west": 68.0, "south": 6.0, "east": 98.0, "north": 38.0}
EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance between two latitude/longitude points in kilometers."""

    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def inside_bbox(lat: float, lon: float, bbox: dict[str, float] | None = None) -> bool:
    """Return whether a point falls within the configured India bounding box."""

    bounds = bbox or INDIA_BBOX
    return bounds["south"] <= lat <= bounds["north"] and bounds["west"] <= lon <= bounds["east"]


def grid_cell_id(lat: float, lon: float, resolution_degrees: float = 0.1) -> str:
    """Build a stable grid-cell identifier for gridded satellite products."""

    lat_idx = int(lat / resolution_degrees)
    lon_idx = int(lon / resolution_degrees)
    return f"lat{lat_idx:04d}_lon{lon_idx:04d}"
