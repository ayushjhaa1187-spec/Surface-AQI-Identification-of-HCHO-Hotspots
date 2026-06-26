"""Command line helpers for AQI, validation metrics and geospatial checks."""

from __future__ import annotations

import argparse
import json
from datetime import date
from typing import Sequence

from surface_aqi_hcho.aqi import calculate_aqi
from surface_aqi_hcho.features import add_temporal_features
from surface_aqi_hcho.geo import inside_bbox


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI parser used by both console scripts and tests."""

    parser = argparse.ArgumentParser(description="Surface AQI and HCHO workflow utilities")
    parser.add_argument(
        "--aqi-json",
        help="Backward-compatible shortcut for `aqi --json`.",
    )

    subparsers = parser.add_subparsers(dest="command", required=False)

    aqi_parser = subparsers.add_parser("aqi", help="Calculate AQI from pollutant JSON")
    aqi_parser.add_argument(
        "--json",
        required=True,
        help='Pollutant concentrations, for example: {"PM2.5": 45, "NO2": 30}',
    )

    bbox_parser = subparsers.add_parser("inside-india", help="Check if a point is inside India bbox")
    bbox_parser.add_argument("--lat", type=float, required=True)
    bbox_parser.add_argument("--lon", type=float, required=True)

    time_parser = subparsers.add_parser("temporal-features", help="Print model calendar features")
    time_parser.add_argument("--date", required=True, help="Date in YYYY-MM-DD format")

    return parser


def run(argv: Sequence[str] | None = None) -> int:
    """Execute the CLI and return a process-style exit code."""

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.aqi_json:
        print(json.dumps(calculate_aqi(json.loads(args.aqi_json)), indent=2, sort_keys=True))
        return 0
    if args.command == "aqi":
        print(json.dumps(calculate_aqi(json.loads(args.json)), indent=2, sort_keys=True))
        return 0
    if args.command == "inside-india":
        print(json.dumps({"inside_india_bbox": inside_bbox(args.lat, args.lon)}, sort_keys=True))
        return 0
    if args.command == "temporal-features":
        parsed_date = date.fromisoformat(args.date)
        print(json.dumps(add_temporal_features(parsed_date), indent=2, sort_keys=True))
        return 0

    parser.print_help()
    return 0


def main() -> None:
    """Console-script entry point."""

    raise SystemExit(run())


if __name__ == "__main__":
    main()
