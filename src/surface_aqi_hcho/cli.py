"""Command line helpers for quick AQI calculations."""

from __future__ import annotations

import argparse
import json

from surface_aqi_hcho.aqi import calculate_aqi


def main() -> None:
    parser = argparse.ArgumentParser(description="Surface AQI and HCHO workflow utilities")
    parser.add_argument(
        "--aqi-json",
        help='JSON object of pollutant concentrations, for example: {"PM2.5": 45, "NO2": 30}',
    )
    args = parser.parse_args()

    if args.aqi_json:
        print(json.dumps(calculate_aqi(json.loads(args.aqi_json)), indent=2, sort_keys=True))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
