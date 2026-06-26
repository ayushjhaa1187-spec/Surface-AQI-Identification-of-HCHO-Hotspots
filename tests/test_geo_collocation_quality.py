from datetime import date, datetime

from surface_aqi_hcho.collocation import PointRecord, collocate_records, find_nearest_record
from surface_aqi_hcho.features import add_temporal_features, seasonal_label
from surface_aqi_hcho.geo import grid_cell_id, haversine_km, inside_bbox
from surface_aqi_hcho.quality import filter_valid_measurements, valid_value


def test_geo_helpers_cover_india_bbox_distance_and_grid_id():
    assert inside_bbox(28.61, 77.20)
    assert not inside_bbox(1.0, 77.20)
    assert round(haversine_km(28.61, 77.20, 28.62, 77.21), 1) == 1.5
    assert grid_cell_id(28.61, 77.20, resolution_degrees=0.1) == "lat0286_lon0772"


def test_quality_control_filters_invalid_measurements():
    filtered = filter_valid_measurements({"PM2.5": 45, "PM10": -1, "AOD": 0.5})

    assert filtered == {"PM2.5": 45.0, "AOD": 0.5}
    assert valid_value("HCHO", 0.0002)


def test_temporal_features_label_biomass_burning_seasons():
    assert seasonal_label(date(2024, 11, 5)) == "post_monsoon"
    assert add_temporal_features(date(2024, 4, 1))["season"] == "pre_monsoon"


def test_collocation_selects_nearest_valid_record():
    station = PointRecord("station", 28.61, 77.20, datetime(2024, 11, 5, 6), {"PM2.5": 45})
    near = PointRecord("near", 28.62, 77.21, datetime(2024, 11, 5, 7), {"HCHO": 0.0002})
    far = PointRecord("far", 20.0, 77.21, datetime(2024, 11, 5, 7), {"HCHO": 0.0003})

    match = find_nearest_record(station, [far, near])
    matches = collocate_records([station], [far, near])

    assert match is not None
    assert match.match.record_id == "near"
    assert len(matches) == 1
