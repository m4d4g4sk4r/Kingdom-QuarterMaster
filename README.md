# Kingdom Quartermaster

> *Kingdom Corporation keeps the ledger. The Quartermaster issues the gear.*

A local, **read-only** CLI that will track your VALORANT agent gear: which
contract rewards you've unlocked, which are still locked, and what they
cost in Kingdom Credits (KC).

> **This project is not endorsed by or affiliated with Riot Games. It uses
> unofficial, undocumented client APIs, is read-only, and may stop working
> after any game patch. Use at your own risk.**

## Status

Early scaffolding — not yet functional. Follow the commit history for progress.

## Hard constraints this tool will always follow

- Read-only: no purchase, activate-contract, or any `POST`/`PUT` to any
  Riot player endpoint will ever exist in this codebase.
- No username/password handling — lockfile auth only.
- No telemetry or analytics.

MIT licensed. Not a Riot Games product.
