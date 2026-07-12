"""Constants and user-configurable settings.

Values here are verified against https://valapidocs.techchrism.me/ and
https://valorant-api.com/ as of the time this tool was written. Riot patches
can change any of these without notice — see README "API notes".
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

VALORANT_API_BASE = "https://valorant-api.com/v1"

# Item-type category UUIDs for the local `store/v1/entitlements/{puuid}/{itemTypeId}`
# endpoint. Source: https://valapidocs.techchrism.me/endpoint/owned-items
ITEM_TYPE_IDS = {
    "agents": "01bb38e1-da47-4e6a-9b3d-945fe4655707",
    "contracts": "f85cb6f7-33e5-4dc8-b609-ec7212301948",
    "sprays": "d5f120f8-ff8c-4aac-92ea-f2b5acbe9475",
    "buddies": "dd3bf334-87f3-40bd-b043-682a57a8dc3a",
    "playercards": "3f296c07-64c3-494c-923b-fe692a4fa1bd",
    "skins": "e7c63390-eda7-46e0-bb7a-a6abdacd2433",
    "skin_variants": "3ad1b2b2-acdb-4524-852f-954a76ddae0a",
    "titles": "de7caa6b-adf7-4588-bbd1-143831e786c6",
}

# Fallback Kingdom Credits currency UUID. Resolved by display name "Kingdom
# Credits" from /v1/currencies at runtime; this is only used if that lookup
# fails.
KINGDOM_CREDITS_UUID_FALLBACK = "85ca954a-41f2-ce94-9b45-8ca3dd39a00d"

# Maps a contract level `reward.type` string (from valorant-api.com contracts)
# to a short internal reward-kind key used for weighting.
REWARD_TYPE_MAP = {
    "Spray": "spray",
    "PlayerCard": "playercard",
    "Title": "title",
    "EquippableCharmLevel": "buddy",
    "EquippableSkinLevel": "skin",
    "Currency": "currency",
}

DEFAULT_REWARD_WEIGHTS = {
    "buddy": 5,
    "playercard": 4,
    "title": 2,
    "spray": 1,
    "skin": 3,
    "currency": 0,
}

# NOT exposed by any documented endpoint as of writing. This is a best-effort
# constant — verify in-game and override via config/CLI if it drifts.
AGENT_RECRUIT_COST_KC = 8000

# Kingdom Credits wallet cap; balance sitting at/near this wastes future
# earnings, so the recommender warns near this threshold.
KC_CAP = 10000
KC_CAP_WARNING_THRESHOLD = 9000

SHARD_CHOICES = ("na", "eu", "ap", "kr", "pbe")


def user_config_dir() -> Path:
    from platformdirs import user_config_dir as _ucd

    return Path(_ucd("kingdom-quartermaster"))


def user_cache_dir() -> Path:
    from platformdirs import user_cache_dir as _uc

    return Path(_uc("kingdom-quartermaster"))


@dataclass
class UserConfig:
    """User-overridable settings, loaded from config.json in the user config dir.

    Never stores tokens, passwords, or usernames.
    """

    shard: str | None = None
    reward_weights: dict = field(default_factory=lambda: dict(DEFAULT_REWARD_WEIGHTS))
    agent_recruit_cost_kc: int = AGENT_RECRUIT_COST_KC

    @classmethod
    def load(cls, path: Path | None = None) -> UserConfig:
        path = path or (user_config_dir() / "config.json")
        if not path.exists():
            return cls()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return cls()
        cfg = cls()
        cfg.shard = data.get("shard", cfg.shard)
        weights = dict(cfg.reward_weights)
        weights.update(data.get("reward_weights", {}))
        cfg.reward_weights = weights
        cfg.agent_recruit_cost_kc = data.get("agent_recruit_cost_kc", cfg.agent_recruit_cost_kc)
        return cfg

    def save(self, path: Path | None = None) -> None:
        path = path or (user_config_dir() / "config.json")
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "shard": self.shard,
            "reward_weights": self.reward_weights,
            "agent_recruit_cost_kc": self.agent_recruit_cost_kc,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
