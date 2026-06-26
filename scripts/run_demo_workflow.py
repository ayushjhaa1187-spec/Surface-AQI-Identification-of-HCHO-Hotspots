"""Run a small no-download demonstration of the AQI/HCHO workflow.

This script uses in-memory sample values so contributors can verify the core
project logic before connecting CPCB, Sentinel-5P, INSAT-3D, FIRMS or reanalysis
data sources.
"""

from __future__ import annotations

from datetime import date, datetime

from surface_aqi_hcho.aqi import calculate_aqi
from surface_aqi_hcho.collocation import PointRecord, collocate_records
from surface_aqi_hcho.features import add_temporal_features
from surface_aqi_hcho.geo import inside_bbox
from surface_aqi_hcho.quality import filter_valid_measurements


def main() -> None:
    station_values = filter_valid_measurements({"PM2.5": 45, "PM10": 260, "NO2": 25})
    print("AQI:", calculate_aqi(station_values))
    print("Temporal features:", add_temporal_features(date(2024, 11, 5)))
    print("Inside India bbox:", inside_bbox(28.61, 77.20))

    station = PointRecord("cpcb_delhi", 28.61, 77.20, datetime(2024, 11, 5, 6), station_values)
    satellite = PointRecord("s5p_pixel", 28.62, 77.21, datetime(2024, 11, 5, 7), {"HCHO": 0.0002})
    print("Collocations:", collocate_records([station], [satellite]))


if __name__ == "__main__":
    main()
