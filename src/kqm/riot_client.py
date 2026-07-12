"""GET-only client for pd.{shard}.a.pvp.net.

Deliberately exposes no way to issue a POST/PUT/DELETE to a Riot player
endpoint — only `get_wallet`, `get_contracts`, and `get_owned_items` exist,
and each of them issues exactly one `client.get(...)` call.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass

from .auth import LocalSession, LockfileInfo, fetch_local_session
from .config import ITEM_TYPE_IDS

PD_BASE_TEMPLATE = "https://pd.{shard}.a.pvp.net"

CLIENT_PLATFORM_BLOB = base64.b64encode(
    json.dumps(
        {
            "platformType": "PC",
            "platformOS": "Windows",
            "platformOSVersion": "10.0.19042.1.256.64bit",
            "platformChipset": "Unknown",
        }
    ).encode("utf-8")
).decode("ascii")


class RiotApiError(RuntimeError):
    """Raised for auth failures we can't resolve, or unexpected response shapes."""


class SchemaDriftError(RiotApiError):
    """The response didn't have the fields we expected — likely a post-patch API change."""

    def __init__(self, context: str, missing_key: str):
        super().__init__(
            f"{context}: response is missing expected field '{missing_key}'. "
            "Riot may have changed the API after a patch."
        )


@dataclass
class RiotClient:
    http_client: object  # httpx.Client
    shard: str
    session: LocalSession
    lockfile: LockfileInfo
    client_version: str

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.session.access_token}",
            "X-Riot-Entitlements-JWT": self.session.entitlements_token,
            "X-Riot-ClientVersion": self.client_version,
            "X-Riot-ClientPlatform": CLIENT_PLATFORM_BLOB,
        }

    def _base(self) -> str:
        return PD_BASE_TEMPLATE.format(shard=self.shard)

    def _refresh_session(self) -> None:
        self.session = fetch_local_session(self.http_client, self.lockfile)

    def _get(self, path: str, context: str) -> dict:
        url = f"{self._base()}{path}"
        resp = self.http_client.get(url, headers=self._headers())
        if resp.status_code == 401:
            # Local token may have expired; refresh once and retry.
            self._refresh_session()
            resp = self.http_client.get(url, headers=self._headers())
        try:
            resp.raise_for_status()
        except Exception as e:
            raise RiotApiError(f"{context}: request failed ({e}).") from e
        try:
            return resp.json()
        except (json.JSONDecodeError, ValueError) as e:
            raise SchemaDriftError(context, "<valid JSON body>") from e

    def get_wallet(self) -> dict:
        body = self._get(f"/store/v1/wallet/{self.session.puuid}", "Wallet")
        if "Balances" not in body:
            raise SchemaDriftError("Wallet", "Balances")
        return body

    def get_contracts(self) -> dict:
        body = self._get(f"/contracts/v1/contracts/{self.session.puuid}", "Contracts")
        if "Contracts" not in body:
            raise SchemaDriftError("Contracts", "Contracts")
        return body

    def get_owned_items(self, item_type_key: str) -> dict:
        """Returns the raw per-itemType response: `{"ItemTypeID": ..., "Entitlements": [...]}`.

        Note: this is flat, not wrapped in an "EntitlementsByTypes" array —
        the valapidocs TypeScript type documents a wrapper that the live API
        doesn't actually return for this endpoint (confirmed against a real
        response). See README "API notes".
        """
        item_type_id = ITEM_TYPE_IDS[item_type_key]
        body = self._get(
            f"/store/v1/entitlements/{self.session.puuid}/{item_type_id}",
            f"Owned items ({item_type_key})",
        )
        if "Entitlements" not in body:
            raise SchemaDriftError(f"Owned items ({item_type_key})", "Entitlements")
        return body

    def get_all_owned_item_uuids(self) -> dict:
        """Returns {item_type_key: set(item_uuid, ...)} for every known category."""
        result = {}
        for key in ITEM_TYPE_IDS:
            body = self.get_owned_items(key)
            ids = {ent["ItemID"] for ent in body["Entitlements"]}
            result[key] = ids
        return result
