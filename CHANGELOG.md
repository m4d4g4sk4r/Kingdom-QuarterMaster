# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] — Unreleased

### Added

- Initial project scaffolding: package layout, MIT license, dependency
  pins.
- Local Riot Client authentication (lockfile discovery, local token
  exchange, shard/region detection) and a read-only `pd.{shard}.a.pvp.net`
  client.
- Static game-data fetch and on-disk cache (agents, contracts,
  currencies) from valorant-api.com, keyed by client version.
- Pure reconciliation of live progression against static contract/tier
  data, with ownership-discrepancy detection.
- Greedy and goal-mode Kingdom Credit purchase recommendations.
- `kqm` CLI: `status`, `unlocked`, `locked`, and `recommend` (with
  `--goal` and `--weight` options), rendered with `rich`.
- Fixture-based unit test suite (20 tests, no network access required).
- CI: ruff lint + pytest across Python 3.10/3.11/3.12.
- Shared `service.fetch_snapshot()` orchestration path used by both the CLI
  and a new local-only FastAPI app (`kqm.webapp`), with a `--mock` mode that
  serves fixture data instead of live Riot data (no VALORANT install
  required).
- Reward name/icon resolution (`buddies`, `sprays`, `playercards`,
  `playertitles` from valorant-api.com) cached alongside existing static
  data.
- `kqm ui [--mock] [--port PORT]`: starts a `127.0.0.1`-only web API and
  opens it in the browser. Read-only, GET-only routes: `/api/snapshot`,
  `/api/recommend`, `/api/goal/{agent_name}`.
- Fixture-based tests for the service layer and web API (13 additional
  tests).
