from surface_aqi_hcho.aqi import calculate_aqi, calculate_pollutant_sub_index


def test_pm25_sub_index_satisfactory_range():
    sub_index = calculate_pollutant_sub_index("PM2.5", 45)

    assert round(sub_index) == 75


def test_overall_aqi_uses_dominant_pollutant():
    result = calculate_aqi({"PM2.5": 45, "PM10": 260, "NO2": 25})

    assert result["aqi"] == 210
    assert result["category"] == "Poor"
    assert result["dominant_pollutant"] == "PM10"
