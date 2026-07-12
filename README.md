# Kingdom Quartermaster

> *Kingdom Corporation keeps the ledger. The Quartermaster issues the gear.*

A local, **read-only** CLI that tracks your VALORANT agent gear: which
contract rewards you've already unlocked, which are still locked and what
each remaining tier costs in Kingdom Credits (KC), and — given your current
KC balance — which purchases give you the most value right now.

[![CI](https://github.com/m4d4g4sk4r/Kingdom-QuarterMaster/actions/workflows/ci.yml/badge.svg)](https://github.com/m4d4g4sk4r/Kingdom-QuarterMaster/actions/workflows/ci.yml)

> **This project is not endorsed by or affiliated with Riot Games. It uses
> unofficial, undocumented client APIs, is read-only, and may stop working
> after any game patch. Use at your own risk.**

## What it does

- `kqm status` — summary of unlocked/locked tier counts per agent, current
  KC balance, and any ownership discrepancies found.
- `kqm unlocked` — every already-unlocked gear reward, per agent.
- `kqm locked` — every not-yet-unlocked gear reward, per agent, with its KC
  cost.
- `kqm recommend` — greedy purchase plan that maximizes reward value per KC
  spent, given your current balance and reward-type weights.
- `kqm recommend --goal agent:<name>` — cheapest path to fully unlock (and
  recruit, if needed) one specific agent's gear.

It never purchases, activates, or modifies anything — every request it
makes is an HTTP `GET`.

```
          Agent Gear Status (example)
  Agent     Recruited   Progress   Locked KC remaining
  Gekko     yes         7/10       27,500
  Jett      yes         10/10      0
  Vyse      no          0/10       8,000 + 46,000

  Kingdom Credits balance: 9,200 / 10,000
  ! You're near the KC cap — earnings past 10,000 are wasted.
```

## Requirements

- The **Riot Client** (or VALORANT) must be **running** on the same
  machine — it never asks for your username or password, and never talks
  to any remote Riot login server. See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
  for exactly how that works.
- Windows is the primary supported platform.
- Python 3.10+

## Install

Use a virtual environment so the pinned dependency versions in
`pyproject.toml` are what actually get installed:

```bash
py -3 -m venv .venv
./.venv/Scripts/activate     # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -e .
```

This installs the `kqm` command.

## Run

```bash
kqm status
kqm locked
kqm unlocked
kqm recommend
kqm recommend --goal agent:Gekko
kqm recommend --weight buddy=10 --weight spray=0
```

If shard/region auto-detection fails, pass it explicitly:

```bash
kqm --shard na status
```

Static game data is cached on disk per game version; force a refetch with
`--refresh-static` if something looks stale.

## Configuration

A JSON config file at the platform's standard user-config directory
(e.g. `%APPDATA%\kingdom-quartermaster\config.json` on Windows) can set:

```json
{
  "shard": "na",
  "reward_weights": { "buddy": 5, "playercard": 4, "title": 2, "spray": 1 },
  "agent_recruit_cost_kc": 8000
}
```

Default reward-type weights: `buddy=5, playercard=4, skin=3, title=2,
spray=1`. Higher weight = that reward type is worth more to you, and the
recommender ranks tiers by `weight / KC cost`. Per-run overrides:
`--weight kind=value` (repeatable).

No token, password, or username is ever written to this file or any other
file on disk — only static game-data cache and these preferences.

## Architecture

```
src/kqm/
  __main__.py     CLI entry (status, locked, unlocked, recommend)
  auth.py         lockfile discovery, local token fetch, shard detection
  riot_client.py  GET-only pd.pvp.net client, 401-retry-once
  static_data.py  valorant-api.com fetch + on-disk cache (by client version)
  reconcile.py    pure: live progression + static tiers -> per-agent model
  recommend.py    pure: greedy plan / goal-mode plan
  render.py       rich tables
tests/               unit tests for reconcile.py and recommend.py, fixture-based, no network
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how local auth works
and notes on the undocumented Riot API this tool depends on.

## Testing

```bash
py -3 -m venv .venv
./.venv/Scripts/activate     # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -e ".[dev]"
pytest
```

`reconcile.py` and `recommend.py` are pure functions with no I/O, tested
entirely against hand-crafted fixture JSON in `tests/fixtures/` — no
network access is used or required to run the test suite.

## Hard constraints this tool follows

- Read-only: no purchase, activate-contract, or any `POST`/`PUT` to any
  Riot player endpoint exists anywhere in this codebase.
- No username/password handling anywhere — lockfile auth only.
- No telemetry or analytics. The only network destinations are Riot's own
  local/player endpoints and valorant-api.com.

## Credits

- [valorant-api.com](https://valorant-api.com/) — public static game data.
- [valapidocs.techchrism.me](https://valapidocs.techchrism.me/) — community
  documentation of the unofficial client API.

MIT licensed. Not a Riot Games product.
