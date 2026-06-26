import json

from surface_aqi_hcho.cli import run


def test_cli_aqi_subcommand_outputs_json(capsys):
    exit_code = run(["aqi", "--json", '{"PM2.5": 45, "PM10": 260}'])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["aqi"] == 210
    assert output["dominant_pollutant"] == "PM10"


def test_cli_inside_india_outputs_boolean(capsys):
    exit_code = run(["inside-india", "--lat", "28.61", "--lon", "77.20"])

    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output == {"inside_india_bbox": True}
