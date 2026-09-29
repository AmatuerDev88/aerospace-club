"""Command-line interface; stdout contains only a report on success."""

import argparse
import json
import sys

from . import __version__
from .telemetry import DataError, analyze


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate and summarize an offline telemetry CSV.")
    parser.add_argument("csv", help="UTF-8 CSV to analyze")
    parser.add_argument("--manifest", required=True, help="version 1 JSON data manifest")
    parser.add_argument("--max-gap-s", type=float, help="report intervals strictly above this positive threshold")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)
    try:
        report = analyze(args.csv, args.manifest, args.max_gap_s)
    except (DataError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
