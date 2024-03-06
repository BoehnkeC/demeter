"""Docker entry point of application."""

from __future__ import annotations

import argparse

import demeter_main

SCRATCH_IN = r"/scratch/in"
SCRATCH_OUT = r"/scratch/out"


def check_directories(in_dir, out_dir):
    if in_dir is not None:
        in_dir = in_dir

    else:
        in_dir = SCRATCH_IN

    if out_dir is not None:
        out_dir = out_dir

    else:
        out_dir = SCRATCH_OUT

    return in_dir, out_dir


def run() -> int:
    """Encapsulate entry point for CLI."""
    args = parse_commandline_args()

    in_dir, out_dir = check_directories(args.in_dir, args.out_dir)

    with demeter_main.Demeter(
        in_dir=in_dir, out_dir=out_dir, start_date=args.start_date, end_date=args.end_date
    ) as demeter:
        demeter.execute(aoi=args.aoi_data)

    return 0


def parse_commandline_args(args: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Fetch and apply Sentinel-2 data for burnt area mapping.")
    parser.add_argument(
        "--aoi_data",
        help="Path to AOI.[GEOJSON, SHP, GPKG], AOI geometry as WKT, Polygon or Multipolygon.",
        metavar="AOI",
        required=True,
    )
    parser.add_argument(
        "--start_date",
        help="Begin of the event, as YYYY-MM-DD, like 2020-11-01",
        metavar="YYYY-MM-DD",
        required=True,
    )
    parser.add_argument(
        "--end_date",
        help="End of the event, as YYYY-MM-DD, like 2020-11-02",
        metavar="YYYY-MM-DD",
        required=True,
    )
    parser.add_argument(
        "--in_dir",
        help="Path to input directory.",
        metavar="IN",
        required=False,
    )
    parser.add_argument(
        "--out_dir",
        help="Path to output directory.",
        metavar="OUT",
        required=False,
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    run()
