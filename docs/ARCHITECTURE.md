# Architecture & API notes

This document covers how Kingdom Quartermaster authenticates locally and the
undocumented-API quirks it depends on. It's aimed at contributors and anyone
auditing the code — day-to-day usage only needs the main [README](../README.md).

## How authentication works

1. Reads `%LocalAppData%\Riot Games\Riot Client\Config\lockfile`
   (`name:pid:port:password:protocol`).
2. Calls the **local-only** endpoint
   `GET https://127.0.0.1:{port}/entitlements/v1/token` with HTTP Basic
   auth (`riot:{password}`) to get a short-lived access token and
   entitlements JWT. TLS verification is disabled *only* for this one
   localhost call, because Riot Client's local API uses a self-signed
   certificate.
3. Detects shard/region via the local endpoint
   `GET https://127.0.0.1:{port}/riotclient/region-locale`, falling back to
   regexing `glz-{region}-1.{shard}.a.pvp.net` out of
   `%LocalAppData%\VALORANT\Saved\Logs\ShooterGame.log` if that fails, and
   finally to the `--shard` flag.
4. Uses the resulting bearer token + entitlements JWT to call
   `pd.{shard}.a.pvp.net` (wallet, contracts, owned items) — all `GET`.
5. Tokens are held in memory only for the duration of one run and are
   never written to disk.

## API notes

This tool's endpoints and field names were verified against
[valapidocs.techchrism.me](https://valapidocs.techchrism.me/) and
[valorant-api.com](https://valorant-api.com/) at time of writing. A few
things worth flagging for anyone maintaining this after a patch:

- **KC cost field is `doughCost`, not `dougCost`.** Kingdom Credits are
  internally named "Dough" (see `assetPath` on the currency:
  `.../Currency_Dough_DataAsset`), so `valorant-api.com/v1/contracts`
  level objects use `doughCost` / `isPurchasableWithDough`. There's also a
  parallel `vpCost` / `isPurchasableWithVP` for the VP-purchasable path
  some tiers support.
- **Kingdom Credits currency UUID** is resolved by matching
  `displayName == "Kingdom Credits"` in `/v1/currencies` at runtime; the
  literal `85ca954a-41f2-ce94-9b45-8ca3dd39a00d` is kept only as a
  fallback in `config.py` in case that lookup ever fails.
- **Wallet balances** are a flat `{ "Balances": { <currencyUuid>: amount } }`
  map — there's no dedicated "KC balance" field, you have to know the UUID.
- **Agent recruit cost (8,000 KC)** is *not* exposed by any documented
  endpoint. It's shipped as a best-effort constant
  (`config.AGENT_RECRUIT_COST_KC`) — override it in your config file if it
  turns out to be wrong or Riot changes it.
- **Shard detection**: the local `GET /riotclient/region-locale` endpoint
  is preferred over log-scraping because it's structured JSON and doesn't
  depend on the player having recently launched a match (which is when the
  `glz-*` URL typically appears in the log).
- **Owned-items response shape**: `GET /store/v1/entitlements/{puuid}/{itemTypeId}`
  returns a flat `{ "ItemTypeID": ..., "Entitlements": [...] }` object, *not*
  the `EntitlementsByTypes`-wrapped array that valapidocs' TypeScript type
  documents. Confirmed against a live response; `riot_client.py` reads the
  flat shape and raises `SchemaDriftError` if `Entitlements` is missing.
- If any live response is missing an expected field, this tool raises a
  `SchemaDriftError` with a message pointing at a likely post-patch API
  change, instead of a raw stack trace.
- **"Recruited" detection**: an agent is considered recruited if either its
  uuid appears in the `agents` owned-entitlements set *or* its contract has
  any progression (`ProgressionLevelReached > 0`). This is because default/
  starter agents (Brimstone, Jett, Phoenix, Sage, Sova as of writing) are
  granted without ever generating a store entitlement record — entitlement
  presence alone false-negatives on them. Known caveat: a brand-new account
  that owns a starter agent but hasn't completed a single contract level yet
  will still show that agent as not recruited, since neither signal is true
  yet.
