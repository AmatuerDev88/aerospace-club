# Aerospace Club · Engineering workspace

Measure carefully. Keep the evidence. Make the next team's work easier.

This is the shared engineering workspace for a high-school aerospace club. Our interests include balloons, rocketry, drones, avionics, telemetry, sensing, simulation, and data analysis. Hardware and mission choices are still open.

**Current status:** software foundation only. No flight system, hardware integration, flight readiness, or experimental results are claimed here.

## Start here

| You want to… | Go to… |
| --- | --- |
| Make your first contribution | [First meeting guide](docs/first-meeting.md) |
| Check a sensor or simulation log | [Telemetry tool](docs/telemetry.md) |
| Plan an experiment and preserve its evidence | [Test practice](docs/testing.md) |
| Propose the club's first project | [Project selection](docs/project-selection.md) |
| Understand technical choices | [Decision record](docs/decisions/0001-foundation.md) |
| See the next useful work | [Roadmap](ROADMAP.md) |

## Working code, without hardware assumptions

`aeroclub` checks a time-series CSV against a small JSON manifest, then produces a machine-readable report with units, descriptive statistics, timing gaps, and SHA-256 input fingerprints. It rejects ambiguous columns, non-finite values, missing measurements, and non-monotonic timestamps. It never fills gaps or silently repairs a recording.

Requires Python 3.11 or newer; no third-party runtime packages. From the repository root:

```sh
python -m unittest discover -s tests -v
python -m aeroclub --help
python -m aeroclub path/to/log.csv --manifest path/to/manifest.json --max-gap-s 0.5 > report.json
```

Use `py -3` instead of `python` on Windows if that is how Python is installed. The gap threshold above is an example analysis setting, not a club sampling requirement. Tests construct tiny artificial inputs in temporary directories solely to verify software behavior; there is no sample flight dataset.

## How we work

1. State the question and a measurable acceptance criterion before testing.
2. Record assumptions, units, instrument identity, calibration status, and software revision.
3. Preserve raw data. Put conversions and exclusions in a reproducible analysis.
4. Review the evidence, including failed tests and unresolved uncertainty.
5. Leave a short handover another student can follow.

Use issues for bounded work, pull requests for review, and [decision records](docs/decisions/0001-foundation.md) for choices that would be expensive to rediscover. Proposed processes are documented; repository branch protections and team roles still need to be configured by the club.

## Repository map

```text
aeroclub/        dependency-free telemetry validation and reporting
tests/           automated software tests (not hardware qualification)
docs/            onboarding, data contract, testing, project selection
templates/       project brief, test record, decision record
.github/         CI, issue forms, and pull-request checklist
```

Create a project directory only when a project is selected. Keep common tools here; split a project into its own repository when its access, releases, or build tooling need an independent lifecycle. Do not create empty subsystem folders to imply an architecture we have not chosen.

Read [CONTRIBUTING](CONTRIBUTING.md) before opening a PR. The software and original documentation are available under the [MIT license](LICENSE).
