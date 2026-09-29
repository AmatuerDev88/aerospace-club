"""Strict, offline time-series analysis. No inference of physical validity."""

import csv
import hashlib
import io
import json
import math
import statistics
from pathlib import Path


class DataError(ValueError):
    """An input violates the documented data contract."""


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise DataError(f"duplicate manifest key: {key}")
        obj[key] = value
    return obj


def _finite(value, context):
    try:
        number = float(value)
    except (ValueError, TypeError, OverflowError) as exc:
        raise DataError(f"{context}: expected a finite number") from exc
    if not math.isfinite(number):
        raise DataError(f"{context}: expected a finite number")
    return number


def _manifest(raw):
    try:
        obj = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=_unique_object)
    except (UnicodeError, ValueError) as exc:
        raise DataError(f"invalid manifest: {exc}") from exc
    keys = {"schema_version", "run_id", "source", "description", "channels"}
    if not isinstance(obj, dict) or set(obj) != keys:
        raise DataError("manifest must contain exactly: " + ", ".join(sorted(keys)))
    if type(obj["schema_version"]) is not int or obj["schema_version"] != 1:
        raise DataError("schema_version must be integer 1")
    for key in ("run_id", "description"):
        if not isinstance(obj[key], str) or not obj[key].strip():
            raise DataError(f"{key} must be a non-empty string")
    if obj["source"] not in ("measured", "simulation", "test-fixture"):
        raise DataError("source must be measured, simulation, or test-fixture")
    channels = obj["channels"]
    if not isinstance(channels, dict) or not channels:
        raise DataError("channels must be a non-empty object mapping column names to units")
    for name, unit in channels.items():
        if not name.strip() or name != name.strip() or name == "time_s":
            raise DataError("channel names must be non-blank, trimmed, and not time_s")
        if not isinstance(unit, str) or not unit.strip() or unit != unit.strip():
            raise DataError(f"channel {name}: unit must be a non-empty, trimmed string")
    return obj


def analyze(csv_path, manifest_path, max_gap_s=None):
    """Return a JSON-serializable report, or raise DataError/OSError.

    Reads each input once so hashes identify precisely the bytes analyzed.
    Memory use is proportional to input size; intended for small bench logs.
    """
    if max_gap_s is not None:
        max_gap_s = _finite(max_gap_s, "max_gap_s")
        if max_gap_s <= 0:
            raise DataError("max_gap_s must be positive")
    manifest_bytes = Path(manifest_path).read_bytes()
    manifest = _manifest(manifest_bytes)
    csv_bytes = Path(csv_path).read_bytes()
    try:
        csv_text = csv_bytes.decode("utf-8-sig")
    except UnicodeError as exc:
        raise DataError("CSV must be UTF-8") from exc
    reader = csv.reader(io.StringIO(csv_text, newline=""), strict=True)
    channels = manifest["channels"]
    samples = {name: [] for name in channels}
    times = []
    try:
        header = next(reader, None)
        if header is None or len(header) != len(set(header)):
            raise DataError("CSV is empty or has duplicate column names")
        if set(header) != {"time_s", *channels}:
            raise DataError("CSV header must match time_s and manifest channels exactly")
        for row in reader:
            line = reader.line_num
            if len(row) != len(header):
                raise DataError(f"line {line}: expected {len(header)} fields, got {len(row)}")
            values = {key: _finite(value, f"line {line}, {key}") for key, value in zip(header, row)}
            timestamp = values.pop("time_s")
            if timestamp < 0 or (times and timestamp <= times[-1]):
                raise DataError(f"line {line}: time_s must be nonnegative and strictly increasing")
            times.append(timestamp)
            for name, value in values.items():
                samples[name].append(value)
    except csv.Error as exc:
        raise DataError(f"invalid CSV near line {reader.line_num}: {exc}") from exc
    if not times:
        raise DataError("CSV must contain at least one sample")
    intervals = [b - a for a, b in zip(times, times[1:])]
    duration = times[-1] - times[0]
    gaps = [
        {"after_sample": i + 1, "start_time_s": times[i], "duration_s": dt}
        for i, dt in enumerate(intervals)
        if max_gap_s is not None and dt > max_gap_s
    ]
    warnings = []
    if len(times) == 1:
        warnings.append("one sample: timing statistics are unavailable")
    if max_gap_s is None:
        warnings.append("no max_gap_s supplied: gap detection was not performed")
    if gaps:
        warnings.append("gaps exceed the selected threshold; missing samples were not inferred")
    try:
        stats = {
            name: {"unit": channels[name], "min": min(values), "max": max(values),
                   "mean": statistics.mean(values)}
            for name, values in samples.items()
        }
        report = {
            "report_version": 1,
            "provenance": manifest,
            "inputs": {"csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
                       "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest()},
            "samples": len(times),
            "timing": {"start_time_s": times[0], "end_time_s": times[-1],
                       "duration_s": duration,
                       "min_interval_s": min(intervals) if intervals else None,
                       "median_interval_s": statistics.median(intervals) if intervals else None,
                       "max_interval_s": max(intervals) if intervals else None,
                       "max_gap_s": max_gap_s, "gaps": gaps},
            "channels": stats,
            "warnings": warnings,
        }
        json.dumps(report, allow_nan=False)
    except (OverflowError, ValueError) as exc:
        raise DataError("numeric range exceeds supported report precision") from exc
    return report
