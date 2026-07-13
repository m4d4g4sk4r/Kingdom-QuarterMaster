"""Fetches and caches static game data from valorant-api.com (no auth needed).

Cache is keyed by the current riotClientVersion so it invalidates automatically
after a game patch. Only reads/writes files under the user cache dir; never
touches player tokens or credentials.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import KINGDOM_CREDITS_UUID_FALLBACK, VALORANT_API_BASE, user_cache_dir


class StaticDataError(RuntimeError):
    """Raised when valorant-api.com returns something we don't understand."""


@dataclass
class StaticData:
    version: str
    agents_by_uuid: dict
    contracts: list
    kingdom_credits_uuid: str
    reward_index: dict  # reward_uuid -> {"name": str, "icon_url": str | None}


def _get_json(client, path: str) -> Any:
    resp = client.get(f"{VALORANT_API_BASE}{path}")
    resp.raise_for_status()
    body = resp.json()
    if "data" not in body:
        raise StaticDataError(
            f"valorant-api.com response for {path} missing 'data' key — "
            "the public API schema may have changed."
        )
    return body["data"]


def fetch_client_version(client) -> str:
    data = _get_json(client, "/version")
    version = data.get("riotClientVersion")
    if not version:
        raise StaticDataError("valorant-api.com /version response missing 'riotClientVersion'.")
    return version


def _cache_path(version: str) -> Path:
    safe_version = version.replace("/", "_")
    return user_cache_dir() / f"static_{safe_version}.json"


def _index_direct(items: list, icon_fields: tuple[str, ...]) -> dict:
    """Index items whose contract reward uuid matches their own top-level uuid."""
    index = {}
    for item in items:
        uuid = item.get("uuid")
        if not uuid:
            continue
        icon_url = next((item[f] for f in icon_fields if item.get(f)), None)
        index[uuid] = {"name": item.get("displayName", ""), "icon_url": icon_url}
    return index


def _index_buddies(buddies: list) -> dict:
    """Buddy contract rewards (EquippableCharmLevel) reference a charm *level*
    uuid, not the parent buddy uuid, so this flattens levels[] instead.
    """
    index = {}
    for buddy in buddies:
        name = buddy.get("displayName", "")
        buddy_icon = buddy.get("displayIcon")
        for level in buddy.get("levels", []):
            uuid = level.get("uuid")
            if not uuid:
                continue
            index[uuid] = {"name": name, "icon_url": level.get("displayIcon") or buddy_icon}
    return index


def _build_reward_index(client) -> dict:
    reward_index = {}
    reward_index.update(_index_direct(_get_json(client, "/sprays"), ("displayIcon", "fullIcon")))
    reward_index.update(
        _index_direct(_get_json(client, "/playercards"), ("displayIcon", "smallArt"))
    )
    reward_index.update(_index_direct(_get_json(client, "/playertitles"), ()))
    reward_index.update(_index_buddies(_get_json(client, "/buddies")))
    return reward_index


def load_static_data(client, force_refresh: bool = False) -> StaticData:
    """Fetch (or load from disk cache) agents/contracts/currencies/reward-icons.

    `client` is any object exposing `.get(url) -> response` with `.raise_for_status()`
    and `.json()` (an httpx.Client in production, a fake in tests).
    """
    version = fetch_client_version(client)
    cache_file = _cache_path(version)

    if not force_refresh and cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            return StaticData(
                version=cached["version"],
                agents_by_uuid=cached["agents_by_uuid"],
                contracts=cached["contracts"],
                kingdom_credits_uuid=cached["kingdom_credits_uuid"],
                reward_index=cached["reward_index"],
            )
        except (json.JSONDecodeError, OSError, KeyError):
            pass  # fall through to a live refetch (also picks up newly-added cache fields)

    agents = _get_json(client, "/agents?isPlayableCharacter=true")
    contracts = _get_json(client, "/contracts")
    currencies = _get_json(client, "/currencies")
    reward_index = _build_reward_index(client)

    agents_by_uuid = {a["uuid"]: a for a in agents}

    kc_uuid = KINGDOM_CREDITS_UUID_FALLBACK
    for currency in currencies:
        if currency.get("displayName") == "Kingdom Credits":
            kc_uuid = currency["uuid"]
            break

    data = StaticData(
        version=version,
        agents_by_uuid=agents_by_uuid,
        contracts=contracts,
        kingdom_credits_uuid=kc_uuid,
        reward_index=reward_index,
    )

    try:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(
            json.dumps(
                {
                    "version": data.version,
                    "agents_by_uuid": data.agents_by_uuid,
                    "contracts": data.contracts,
                    "kingdom_credits_uuid": data.kingdom_credits_uuid,
                    "reward_index": data.reward_index,
                }
            ),
            encoding="utf-8",
        )
    except OSError:
        pass  # caching is best-effort; a failure here shouldn't break the tool

    return data
