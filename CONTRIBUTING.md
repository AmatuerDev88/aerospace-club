# Contributing

Small, reviewable changes are welcome. Open an issue describing the problem, expected behavior, and evidence before a substantial change. Discuss hardware or contract changes before implementing them.

## Local loop

```sh
git switch -c describe-your-change
python -m unittest discover -s tests -v
python -m aeroclub --help
git diff --check
```

Use Python 3.11+ and the standard library unless a real requirement justifies a dependency. Add regression tests for meaningful changes to parsing, calculations, or CLI behavior. State what you tested; never report an unrun check as passed. Include units and references for engineering calculations.

Open a pull request with the problem, changed behavior, verification, and limitations. Ask another member to review changes to measurement meanings, units, or test criteria. This is the proposed workflow; an owner must configure GitHub's enforcement separately.

## Public content

Publish only material the club is entitled to share. Keep credentials, student contact details, precise sensitive locations, and unreviewed raw recordings out of commits and issues. `.gitignore` is convenience, not a security boundary. Review `git diff --cached` before committing. Do not copy vendor documentation or datasets without checking their redistribution terms.

Use labels such as proposed, simulated, measured, and verified precisely. Keep negative results and uncertainty visible. Give contributors credit with their consent. Be respectful, welcome beginner questions, and challenge claims through evidence rather than personal criticism. Raise interpersonal concerns privately with the club's faculty sponsor.

## Maintainer setup and handover

After the first CI run, configure the default branch to require the test checks and a peer review if the team's access permits it. Avoid sharing an account. Add a second maintainer, agree on a private contact route, and transfer to a school-approved organization when appropriate. Review these choices each term. Do not publish student names or school branding without agreement.
