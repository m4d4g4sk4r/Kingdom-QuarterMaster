# Contributing to Kingdom Quartermaster

## Setup

```bash
py -3 -m venv .venv
./.venv/Scripts/activate     # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -e ".[dev]"
```

## Before opening a PR

```bash
ruff check .
ruff format --check .
pytest -v
```

All three are also run by CI on every push and pull request against `main`.
If `ruff format --check` fails, run `ruff format .` locally and commit the
result.

## Ground rules

This project has a few constraints that are considered non-negotiable,
regardless of how convenient it'd be to relax them:

- **Read-only, always.** No code path may issue a `POST`, `PUT`, `DELETE`,
  or any other mutating request to a Riot player endpoint. This tool only
  ever reads wallet, contract, and inventory state.
- **Lockfile auth only.** Never add a code path that asks for (or stores)
  a username or password. All authentication goes through the local Riot
  Client lockfile.
- **No telemetry.** The only network destinations this tool talks to are
  Riot's own local/player endpoints and valorant-api.com. Don't add
  analytics, crash reporting, or any third-party network call.
- **Keep `reconcile.py` and `recommend.py` pure.** Both modules currently
  do no I/O and are fully covered by fixture-based unit tests with no
  network access. If you touch them, keep it that way -- I/O belongs in
  `riot_client.py`, `static_data.py`, or `auth.py`.
- **Document API drift.** This tool depends on undocumented Riot client
  endpoints and valorant-api.com's public schema. If you discover a field
  name, response shape, or endpoint has changed, update the "API notes"
  section of the README as part of the same PR that fixes it -- future
  maintainers will need that context after the next game patch.

## Reporting API drift you can't fix yet

If VALORANT patches something and you don't have time to fix it, opening
an issue describing exactly what changed (endpoint, field, old shape vs.
new shape) is still very useful -- see the README's "API notes" section
for the level of detail that's helpful.
