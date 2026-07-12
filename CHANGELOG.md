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
