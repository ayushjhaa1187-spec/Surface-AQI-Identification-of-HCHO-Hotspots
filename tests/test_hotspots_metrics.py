import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")

from surface_aqi_hcho.hotspots import correlate_fire_hcho, detect_hotspots
from surface_aqi_hcho.metrics import regression_metrics


def test_detect_hotspots_flags_extreme_hcho_values():
    frame = pd.DataFrame(
        {
            "month": [10] * 6,
            "hcho_column": [1.0, 1.1, 1.0, 1.2, 1.1, 4.0],
        }
    )

    result = detect_hotspots(frame, zscore_threshold=1.5, quantile_threshold=0.80)

    assert result["is_hcho_hotspot"].tolist() == [False, False, False, False, False, True]


def test_correlate_fire_hcho_returns_positive_relationship():
    frame = pd.DataFrame({"hcho_column": [1.0, 2.0, 3.0], "fire_count": [2, 4, 6]})

    result = correlate_fire_hcho(frame)

    assert result["n"] == 3
    assert result["pearson_r"] == 1.0


def test_regression_metrics():
    result = regression_metrics(np.array([1, 2, 3]), np.array([1, 2, 4]))

    assert result["n"] == 3
    assert round(result["rmse"], 3) == 0.577
    assert round(result["mae"], 3) == 0.333
