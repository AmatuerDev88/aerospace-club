# Offline telemetry contract · version 1

This contract is an analysis boundary, not a wire protocol or firmware requirement. An adapter can later export a device's native records into this format. Preserve that original recording separately.

## Inputs

The CSV is UTF-8 (an optional BOM is accepted), with a header containing `time_s` and exactly the channels declared in the manifest. Column order is free. Each row is one synchronized sample, all fields numeric and finite. No blank rows or missing values. Timestamps are nonnegative elapsed seconds from a documented run origin and strictly increase. A restart or clock reset belongs in a separate run.

The companion JSON has exactly these five fields. The following is a **format illustration for a future bench recording**, not a claim that this sensor or recording exists:

```json
{
  "schema_version": 1,
  "run_id": "bench-check-001",
  "source": "measured",
  "description": "Replace with the actual setup, clock origin, conversion method, and test-record reference before use.",
  "channels": {
    "supply_voltage": "V"
  }
}
```

Create a manifest alongside your own recording. Use `measured` only for observations, `simulation` for model outputs, and `test-fixture` for artificial software inputs. Source labels are self-reported; the tool cannot verify them. No example measurement values are supplied.

Channel names must match the CSV exactly. Units are explicit strings: prefer `V`, `A`, `Pa`, `K`, `m`, `m/s`, and `1` for dimensionless quantities. Units are labels, not machine-verified dimensional types. Document frames, sign conventions, sensor placement, conversions, and calibration in the test record. A field called altitude needs a reference datum; acceleration needs axes and a statement about whether gravity is included.

For asynchronous sensors, export separate per-stream logs. Do not manufacture simultaneous measurements by forward filling. A later alignment tool should make interpolation and timebase assumptions explicit.

## Running the tool

Run from the repository root (no installation required):

```sh
python -m aeroclub path/to/log.csv --manifest path/to/manifest.json --max-gap-s 0.5 > report.json
```

Exit status `0` means the format was accepted; warnings and timing gaps still need review. Exit status `2` means invalid inputs, inaccessible files, or incorrect CLI arguments. Errors go to stderr and successful JSON to stdout. Shell redirection may create an empty report file on failure: check the exit status before consuming it. Never redirect output onto either input file.

The optional positive `--max-gap-s` is chosen from the experiment's sampling requirement. Intervals strictly greater than it are reported; equality is accepted. Omitting it explicitly disables gap detection. `after_sample` uses one-based sample numbering, excluding the header. A long interval does not establish packet loss without device sequence numbers and a timing model.

The report includes sample count, min/max/arithmetic mean per channel, elapsed duration and min/median/max sample intervals. A one-sample run has null interval statistics. No standard deviation, uncertainty, spectral analysis, calibration correction, or flight-performance metrics are inferred. The mean weights samples equally; for irregular sampling it is **not a time-weighted mean**.

## Reproducibility and limits

SHA-256 fingerprints identify the exact bytes read for both inputs. Record the tool's Git commit with your report; report version describes the JSON structure, not the implementation revision. Hashes detect changed inputs, not authentic measurements. Keep original data read-only by convention, including failed runs.

The tool loads the complete log into memory and uses Python floating-point numbers. It is intended for small bench recordings, not live telemetry, large archives, or control loops. Very large values that make derived statistics non-finite are rejected. It does not check physical plausibility, sensor accuracy, timestamp accuracy, or unit consistency. A passing report is not experimental acceptance or authorization to operate hardware.

When extending the contract, add a decision record and reject unsupported versions. Do not silently change column meanings. Useful future adapters depend on real device exports and documented clock behavior.
