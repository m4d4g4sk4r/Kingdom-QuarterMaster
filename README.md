# Kingdom Quartermaster

> *Kingdom Corporation keeps the ledger. The Quartermaster issues the gear.*

A local, **read-only** CLI **and web UI** that tracks your VALORANT agent
gear: which contract rewards you've already unlocked, which are still locked
and what each remaining tier costs in Kingdom Credits (KC), and — given your
current KC balance — which purchases give you the most value right now.

[![CI](https://github.com/m4d4g4sk4r/Kingdom-QuarterMaster/actions/workflows/ci.yml/badge.svg)](https://github.com/m4d4g4sk4r/Kingdom-QuarterMaster/actions/workflows/ci.yml)

<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="Kingdom Quartermaster — the requisition terminal dashboard" width="900">
</p>
<p align="center"><sub><code>kqm ui</code> — the requisition terminal: your operating budget, and every agent's gear contract on one manifest.</sub></p>

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
- `kqm recommend --goal <name>` — cheapest path to fully unlock (and
  recruit, if needed) one specific agent's gear.
- `kqm ui` — opens a local, `127.0.0.1`-only **web UI** (the "Kingdom
  Requisition Terminal") in your browser: a dashboard with your KC
  authorization gauge and agent manifest, a per-agent contract track, and a
  requisition planner with live priority weights and goal mode. Add `--mock`
  to serve bundled fixture data, so you can try it without VALORANT running.

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

## The requisition terminal

The web UI (`kqm ui`) is styled as an in-world Kingdom Corporation supply
depot: the chrome stays a disciplined gunmetal grey, and colour enters only
where an agent does. Everything is read-only — plans are drafted, never
purchased. (Screenshots below use `kqm ui --mock`, so no VALORANT is
needed to look around.)

<table>
  <tr>
    <td width="50%" valign="top">
      <a href="docs/screenshots/agent-detail.png"><img src="docs/screenshots/agent-detail.png" alt="Agent detail — the 10-tier requisition track"></a>
      <p><b>Agent detail.</b> The contract as a ten-tier requisition track:
      what's been <em>issued</em>, the single tier cleared for
      <em>authorization</em> next, and what's still <em>pending</em> — with
      ownership discrepancies flagged as manifest notes.</p>
    </td>
    <td width="50%" valign="top">
      <a href="docs/screenshots/planner-best-value.png"><img src="docs/screenshots/planner-best-value.png" alt="Requisition planner — best value"></a>
      <p><b>Best-value planner.</b> A draft requisition ordered by value per
      credit, with the running balance drawn down line by line. Tune the
      priority weights and it re-drafts live.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="docs/screenshots/planner-goal.png"><img src="docs/screenshots/planner-goal.png" alt="Requisition planner — goal mode"></a>
      <p><b>Goal mode.</b> Cost out a single agent's full unlock: total to
      finish, what's affordable now, the shortfall, and whether they still
      need recruiting.</p>
    </td>
    <td width="50%" valign="top">
      <a href="docs/screenshots/filter-not-recruited.png"><img src="docs/screenshots/filter-not-recruited.png" alt="Manifest filtered to not-recruited agents"></a>
      <p><b>Filter the manifest.</b> Sort by closest-to-done or most locked
      value, or filter down to just the agents you haven't recruited yet.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <a href="docs/screenshots/offline-state.png"><img src="docs/screenshots/offline-state.png" alt="Offline state — the line is severed"></a>
      <p><b>Every state has a home.</b> When VALORANT isn't running or the
      line drops, you get a clear, in-character screen telling you exactly
      what to do — never a blank page or a raw stack trace.</p>
    </td>
    <td width="50%" valign="top">
      <br>
      <p>The full design direction — palette, type, the "colour only where an
      agent does" rule — is written up in
      <a href="frontend/DESIGN_BRIEF.md">frontend/DESIGN_BRIEF.md</a>.</p>
    </td>
  </tr>
</table>

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

This installs the `kqm` command. For the local web UI (`kqm ui`), install
the extra dependencies too: `pip install -e ".[ui]"`.

## Run

```bash
kqm status
kqm locked
kqm unlocked
kqm recommend
kqm recommend --goal Gekko
kqm recommend --weight buddy=10 --weight spray=0
kqm ui                # opens http://127.0.0.1:8420, live data
kqm ui --mock         # same, but with fixture data — no VALORANT required
```

The UI is a bundled static build served by the same process, so `kqm ui`
needs no Node at runtime. It also serves interactive API docs at `/docs`
(Swagger UI) and `/redoc`.

### Developing the web UI

The frontend lives in `frontend/` (Vite + React + TypeScript + Tailwind).
Node is only needed to *build* it, never to run it.

```bash
cd frontend
npm install
npm run dev     # Vite dev server on :5173, proxies /api to 127.0.0.1:8420
# in another terminal, from the repo root:
kqm ui --mock   # serves the API the dev server proxies to
```

To refresh the bundle that `kqm ui` serves:

```bash
cd frontend && npm run build   # outputs to src/kqm/webui/
```

The design direction is documented in
[frontend/DESIGN_BRIEF.md](frontend/DESIGN_BRIEF.md).

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
  __main__.py     CLI entry (status, locked, unlocked, recommend, ui)
  auth.py         lockfile discovery, local token fetch, shard detection
  riot_client.py  GET-only pd.pvp.net client, 401-retry-once
  static_data.py  valorant-api.com fetch + on-disk cache (by client version)
  reconcile.py    pure: live progression + static tiers -> per-agent model
  recommend.py    pure: greedy plan / goal-mode plan
  render.py       rich tables
  service.py      fetch_snapshot() - shared orchestration for CLI + web API,
                   with a --mock mode backed by tests/fixtures/
  webapp.py       127.0.0.1-only FastAPI app (GET-only) used by `kqm ui`;
                   serves the built SPA + JSON API on one origin
  webui/          built web UI (generated by `frontend` build; package data)
frontend/            Vite + React + Tailwind source for the web UI (dev/build only)
tests/               unit tests for reconcile.py, recommend.py, service.py and
                     webapp.py, fixture-based, no network
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
