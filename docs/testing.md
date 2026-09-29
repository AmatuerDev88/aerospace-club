# From a question to defensible evidence

Use [the test-record template](../templates/test-record.md) for actual experiments. Keep planned criteria separate from observations. Mark every unknown as unknown; an empty results section should say **not run**.

## A first, hardware-independent exercise

**Question:** Can another member reproduce the telemetry tool's validation behavior from a clean checkout?

**Method:** Record the Git commit, operating system, and Python version. Run `python -m unittest discover -s tests -v`, then `python -m aeroclub --help`. Review the test that rejects non-monotonic timestamps. Explain why silently sorting a log could hide a device clock reset.

**Acceptance criterion:** the test process exits zero and CLI help exits zero. Attach the actual command output and have a second member reproduce it. This verifies software behavior only. It is a proposed club exercise; execution by the club has not been claimed.

## Before a physical experiment

Define the variable being measured, units, reference, required range, and acceptable error. List the instrument, its calibration status, environment, mounting, and the planned comparison method. Separate repeatability from accuracy: repeated agreement does not prove a correct absolute reading.

Write numerical pass/fail criteria and stop conditions before collecting data. Identify credible hazards, controls, the responsible supervisor, and who can stop the test. Physical testing needs school authorization and a project-specific review. This workspace contains no flight or launch procedure.

## During and after

Record run IDs and configuration changes. Preserve every raw run, including bad ones, and explain exclusions in a derived analysis. Never overwrite the original to fix units, timestamps, or outliers. Record time synchronization assumptions and uncertainty sources before interpreting differences between instruments.

Use a local layout such as:

```text
local-data/<run-id>/raw/       original device exports
local-data/<run-id>/derived/   converted CSV and reports
local-data/<run-id>/record.md setup, method, observations, and review
```

`local-data/` is ignored by Git to prevent accidental publishing; it is not a backup. Maintain an approved shared backup with controlled access. Before intentionally publishing a dataset elsewhere in the repo, remove personal information, precise sensitive locations, credentials, and radio identifiers that should not be public; verify consent and redistribution rights. Link public evidence from the test record only after review.

Close the loop with a conclusion that names which criterion passed, failed, or remains undetermined. Include measurement uncertainty, anomalies, and the next discriminating experiment. A graph alone is not a conclusion.
