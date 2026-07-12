"""Local-only authentication via the Riot Client lockfile.

This module never handles a username or password typed by the user — it
only reads the lockfile Riot Client itself writes to disk while running,
and uses it to call two local-only endpoints on 127.0.0.1. Nothing here
ever contacts a remote Riot auth server.
"""
from __future__ import annotations

import base64
import contextlib
import os
import re
from dataclasses import dataclass
from pathlib import Path

from .config import SHARD_CHOICES

DEFAULT_LOCKFILE_PATH = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "Riot Games"
    / "Riot Client"
    / "Config"
    / "lockfile"
)
DEFAULT_SHOOTERGAME_LOG_PATH = (
    Path(os.environ.get("LOCALAPPDATA", ""))
    / "VALORANT"
    / "Saved"
    / "Logs"
    / "ShooterGame.log"
)

_SHARD_LOG_RE = re.compile(
    r"https://glz-(?P<region>[a-z0-9]+)-1\.(?P<shard>[a-z0-9]+)\.a\.pvp\.net"
)


class LockfileNotFoundError(RuntimeError):
    """Riot Client / VALORANT doesn't appear to be running."""


class ShardDetectionError(RuntimeError):
    """Couldn't determine the player's shard automatically."""


class LocalApiUnavailableError(RuntimeError):
    """The Riot Client lockfile exists but its local API didn't respond as expected —
    usually because the client is still starting up, or isn't fully logged in yet.
    """


@dataclass
class LockfileInfo:
    name: str
    pid: int
    port: int
    password: str
    protocol: str


@dataclass
class LocalSession:
    puuid: str
    access_token: str
    entitlements_token: str


def read_lockfile(path: Path | None = None) -> LockfileInfo:
    lockfile_path = path or DEFAULT_LOCKFILE_PATH
    if not lockfile_path.exists():
        raise LockfileNotFoundError(
            "Couldn't find the Riot Client lockfile. Make sure the Riot Client "
            "or VALORANT is running, then try again.\n"
            f"(looked in: {lockfile_path})"
        )
    raw = lockfile_path.read_text(encoding="utf-8").strip()
    parts = raw.split(":")
    if len(parts) != 5:
        raise LockfileNotFoundError(
            "The Riot Client lockfile has an unexpected format — Riot may have "
            "changed it after a patch."
        )
    name, pid, port, password, protocol = parts
    return LockfileInfo(
        name=name, pid=int(pid), port=int(port), password=password, protocol=protocol
    )


def _local_auth_header(password: str) -> str:
    token = base64.b64encode(f"riot:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def fetch_local_session(client, lockfile: LockfileInfo) -> LocalSession:
    """`client` is an httpx.Client-like object; caller is responsible for
    passing verify=False (or an equivalent) since this is a self-signed
    localhost cert used only for this one call.
    """
    url = f"https://127.0.0.1:{lockfile.port}/entitlements/v1/token"
    try:
        resp = client.get(url, headers={"Authorization": _local_auth_header(lockfile.password)})
        resp.raise_for_status()
        body = resp.json()
    except Exception as e:
        raise LocalApiUnavailableError(
            "Couldn't get a token from the Riot Client's local API "
            f"({e}). Make sure Riot Client/VALORANT is fully started and you're "
            "logged in, then try again."
        ) from e
    try:
        return LocalSession(
            puuid=body["subject"],
            access_token=body["accessToken"],
            entitlements_token=body["token"],
        )
    except KeyError as e:
        raise RuntimeError(
            "Local entitlements token response is missing an expected field "
            f"({e}) — Riot may have changed the API after a patch."
        ) from e


def detect_shard_via_region_locale(client, lockfile: LockfileInfo) -> str | None:
    """Try the local `GET /riotclient/region-locale` endpoint first."""
    url = f"https://127.0.0.1:{lockfile.port}/riotclient/region-locale"
    with contextlib.suppress(Exception):
        resp = client.get(url, headers={"Authorization": _local_auth_header(lockfile.password)})
        resp.raise_for_status()
        body = resp.json()
        region = body.get("region")
        if region in SHARD_CHOICES:
            return region
    return None


def detect_shard_via_log(log_path: Path | None = None) -> str | None:
    path = log_path or DEFAULT_SHOOTERGAME_LOG_PATH
    if not path.exists():
        return None
    with contextlib.suppress(OSError):
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = _SHARD_LOG_RE.search(text)
        if match:
            shard = match.group("shard")
            if shard in SHARD_CHOICES:
                return shard
    return None


def detect_shard(client, lockfile: LockfileInfo, log_path: Path | None = None) -> str:
    shard = detect_shard_via_region_locale(client, lockfile)
    if shard:
        return shard
    shard = detect_shard_via_log(log_path)
    if shard:
        return shard
    raise ShardDetectionError(
        "Couldn't automatically detect your shard/region. Pass --shard explicitly "
        f"(one of: {', '.join(SHARD_CHOICES)})."
    )
