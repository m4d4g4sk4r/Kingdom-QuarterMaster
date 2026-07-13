"""Single orchestration path shared by the CLI and the local web UI.

Performs the lockfile -> session -> shard -> static-data -> live-data ->
reconcile sequence exactly once. Callers (the CLI's main() and the FastAPI
app) are responsible for catching the auth/API/static-data exceptions this
raises and rendering them appropriately — this module doesn't swallow them.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import httpx

from .auth import detect_shard, fetch_local_session, read_lockfile
from .reconcile import AgentGearStatus, reconcile
from .riot_client import RiotClient
from .static_data import load_static_data

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"


@dataclass
class Snapshot:
    agents: list[AgentGearStatus]
    balance: int
    client_version: str
    shard: str
    fetched_at: str
    reward_index: dict = field(default_factory=dict)
    agents_static: dict = field(default_factory=dict)


def parse_weight_overrides(raw: list[str], base: dict) -> dict:
    """Shared by the CLI's --weight and the API's ?weight= query param.

    Each item looks like "kind=value", e.g. "buddy=10".
    """
    weights = dict(base)
    for item in raw:
        if "=" not in item:
            continue
        kind, _, value = item.partition("=")
        try:
            weights[kind.strip()] = float(value.strip())
        except ValueError:
            continue
    return weights


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_fixture(name: str):
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def _mock_owned_by_item_type_key() -> dict:
    owned_agents = _load_fixture("owned_agents.json")
    owned_sprays = _load_fixture("owned_sprays.json")

    def item_ids(payload):
        return {ent["ItemID"] for ent in payload["Entitlements"]}

    return {
        "agents": item_ids(owned_agents),
        "sprays": item_ids(owned_sprays),
        "playercards": set(),
        "titles": set(),
        "buddies": set(),
        "skins": set(),
    }


def _fetch_snapshot_mock() -> Snapshot:
    agents_by_uuid = {a["uuid"]: a for a in _load_fixture("static_agents.json")}
    static_contracts = _load_fixture("static_contracts.json")
    live_contracts = _load_fixture("contracts.json")
    wallet = _load_fixture("wallet.json")
    currencies = _load_fixture("static_currencies.json")
    owned = _mock_owned_by_item_type_key()

    kc_uuid = next(
        (c["uuid"] for c in currencies if c.get("displayName") == "Kingdom Credits"), None
    )
    balance = wallet["Balances"].get(kc_uuid, 0) if kc_uuid else 0

    agents = reconcile(agents_by_uuid, static_contracts, live_contracts, owned)

    return Snapshot(
        agents=agents,
        balance=balance,
        client_version="mock",
        shard="na",
        fetched_at=_now_iso(),
        reward_index={},
        agents_static=agents_by_uuid,
    )


def _fetch_snapshot_live(shard_override: str | None, force_refresh_static: bool) -> Snapshot:
    lockfile = read_lockfile()

    # verify=False is required for this one call: the Riot Client's local
    # API server uses a self-signed cert on 127.0.0.1. No other host is
    # ever contacted with verification disabled.
    with httpx.Client(verify=False, timeout=10.0) as local_client:
        session = fetch_local_session(local_client, lockfile)
        shard = shard_override or detect_shard(local_client, lockfile)

    with httpx.Client(timeout=15.0) as static_client:
        static_data = load_static_data(static_client, force_refresh=force_refresh_static)

    with httpx.Client(timeout=15.0) as pd_client:
        client = RiotClient(
            http_client=pd_client,
            shard=shard,
            session=session,
            lockfile=lockfile,
            client_version=static_data.version,
        )
        wallet = client.get_wallet()
        contracts_response = client.get_contracts()
        owned = client.get_all_owned_item_uuids()

    balance = wallet["Balances"].get(static_data.kingdom_credits_uuid, 0)
    agents = reconcile(static_data.agents_by_uuid, static_data.contracts, contracts_response, owned)

    return Snapshot(
        agents=agents,
        balance=balance,
        client_version=static_data.version,
        shard=shard,
        fetched_at=_now_iso(),
        reward_index=static_data.reward_index,
        agents_static=static_data.agents_by_uuid,
    )


def fetch_snapshot(
    shard_override: str | None = None,
    force_refresh_static: bool = False,
    mock: bool = False,
    demo: bool = False,
) -> Snapshot:
    if demo:
        # A fuller, self-contained roster for the web UI demo. Kept out of the
        # unit-test path (mock) so test fixtures stay minimal.
        from ._demo import build_demo_snapshot

        return build_demo_snapshot()
    if mock:
        return _fetch_snapshot_mock()
    return _fetch_snapshot_live(shard_override, force_refresh_static)
