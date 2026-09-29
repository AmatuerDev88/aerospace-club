"""Artificial software inputs only: no experimental or flight measurements."""

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from aeroclub.telemetry import DataError, analyze


class TelemetryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.csv = Path(self.temp.name) / "fixture.csv"
        self.manifest = Path(self.temp.name) / "manifest.json"
        self.metadata = {"schema_version": 1, "run_id": "unit-test",
                         "source": "test-fixture", "description": "Artificial software test input",
                         "channels": {"signal": "1"}}
        self.write_manifest()

    def write_manifest(self):
        self.manifest.write_text(json.dumps(self.metadata), encoding="utf-8")

    def run_data(self, content, gap=1):
        self.csv.write_text(content, encoding="utf-8", newline="")
        return analyze(self.csv, self.manifest, gap)

    def test_statistics_and_gap_boundary(self):
        report = self.run_data("time_s,signal\n0,2\n1,4\n3,6\n")
        self.assertEqual(report["channels"]["signal"], {"unit": "1", "min": 2, "max": 6, "mean": 4})
        self.assertEqual(report["timing"]["median_interval_s"], 1.5)
        self.assertEqual(report["timing"]["duration_s"], 3)
        self.assertEqual(report["timing"]["gaps"], [{"after_sample": 2, "start_time_s": 1, "duration_s": 2}])
        self.assertEqual(report["inputs"]["csv_sha256"], hashlib.sha256(self.csv.read_bytes()).hexdigest())
        self.assertEqual(report["inputs"]["manifest_sha256"], hashlib.sha256(self.manifest.read_bytes()).hexdigest())

    def test_one_sample(self):
        report = self.run_data("signal,time_s\n2,0\n", None)
        self.assertIsNone(report["timing"]["median_interval_s"])
        self.assertEqual(len(report["warnings"]), 2)

    def test_bad_rows(self):
        for content in ("", "time_s,signal\n", "time_s,signal,signal\n0,1,2\n",
                        "time_s,other\n0,1\n", "time_s,signal\n0,\n",
                        "time_s,signal\n0,NaN\n", "time_s,signal\n0,inf\n",
                        "time_s,signal\n-1,2\n", "time_s,signal\n0,2\n0,3\n",
                        "time_s,signal\n1,2\n0,3\n", "time_s,signal\n0,2,3\n",
                        "time_s,signal\n\n", 'time_s,signal\n0,"2\n'):
            with self.subTest(content=content), self.assertRaises(DataError):
                self.run_data(content)

    def test_bad_gap_thresholds(self):
        for gap in (0, -1, float("nan"), float("inf")):
            with self.subTest(gap=gap), self.assertRaises(DataError):
                self.run_data("time_s,signal\n0,2\n", gap)

    def test_manifest_validation(self):
        for key, value in (("schema_version", True), ("source", "flight"),
                           ("channels", {}), ("channels", {"time_s": "s"}),
                           ("channels", {"signal": ""}), ("description", "")):
            original = self.metadata[key]
            self.metadata[key] = value
            self.write_manifest()
            with self.subTest(key=key, value=value), self.assertRaises(DataError):
                self.run_data("time_s,signal\n0,2\n")
            self.metadata[key] = original

    def test_duplicate_manifest_key(self):
        self.manifest.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        with self.assertRaises(DataError):
            self.run_data("time_s,signal\n0,2\n")

    def test_utf8_bom_and_crlf(self):
        report = self.run_data("\ufefftime_s,signal\r\n0,2\r\n1,4\r\n")
        self.assertEqual(report["samples"], 2)

    def test_multiple_channels_and_reordered_header(self):
        self.metadata["channels"]["second"] = "V"
        self.write_manifest()
        report = self.run_data("second,signal,time_s\n10,2,0\n20,4,1\n")
        self.assertEqual(report["channels"]["second"]["mean"], 15)

    def test_invalid_encoding(self):
        self.csv.write_bytes(b"\xff")
        with self.assertRaises(DataError):
            analyze(self.csv, self.manifest)

    def test_cli_success_and_error(self):
        self.run_data("time_s,signal\n0,2\n1,4\n")
        command = [sys.executable, "-m", "aeroclub", str(self.csv), "--manifest", str(self.manifest)]
        good = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)["samples"], 2)
        self.csv.write_text("bad", encoding="utf-8")
        bad = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertEqual(bad.stdout, "")
        self.assertIn("error:", bad.stderr)


if __name__ == "__main__":
    unittest.main()
