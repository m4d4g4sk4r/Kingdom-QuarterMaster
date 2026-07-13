"""A richer, self-contained demo dataset for `kqm ui --mock`.

This is deliberately separate from ``tests/fixtures`` (which stays minimal and
faithful for unit tests). It exists only to make the web UI look real when
there's no VALORANT install to read — a fuller agent roster with varied
progression, a couple of recruitment gaps, and one ownership discrepancy, so
the dashboard, sorts, filters, and planner all have something to show.

Reward names/icons are intentionally left unresolved (reward_index is empty),
exactly as in mock mode — the UI falls back to the reward kind.
"""

from __future__ import annotations

from datetime import datetime, timezone

from .reconcile import AgentGearStatus, TierStatus

_MEDIA = "https://media.valorant-api.com/agents"

# The standard Kingdom gear-contract shape: 10 tiers, fixed kinds and costs
# (total 21,000 KC). (index, reward_type, reward_kind, cost_kc)
_TEMPLATE: list[tuple[int, str, str, int]] = [
    (1, "Spray", "spray", 1000),
    (2, "PlayerCard", "playercard", 2000),
    (3, "Title", "title", 1500),
    (4, "EquippableCharmLevel", "buddy", 3000),
    (5, "Spray", "spray", 1000),
    (6, "PlayerCard", "playercard", 2000),
    (7, "Spray", "spray", 1000),
    (8, "Title", "title", 1500),
    (9, "EquippableCharmLevel", "buddy", 3000),
    (10, "EquippableSkinLevel", "skin", 5000),
]

_DEMO_BALANCE = 7850


# (name, uuid, gradient, recruited, unlocked_count, has_discrepancy)
_ROSTER: list[tuple[str, str, list[str], bool, int, bool]] = [
    (
        "Jett",
        "add6443a-41bd-e414-f6ad-e58d267f4e95",
        ["25607aff", "0f1923ff", "0f1923ff", "25607aff"],
        True,
        10,
        False,
    ),
    (
        "Chamber",
        "22697a3d-45bf-8dd7-4fec-84a9e28c69d7",
        ["20435bff", "0f1923ff", "372d2bff", "0f192300"],
        True,
        10,
        False,
    ),
    (
        "Sova",
        "320b2a48-4d9b-a075-30f1-1f93a9b638fa",
        ["355285ff", "0f1923ff", "101c47ff", "0f192300"],
        True,
        9,
        False,
    ),
    (
        "Raze",
        "f94c3b30-42be-e959-889c-5aa313dba261",
        ["742e1eff", "0f1923ff", "2c5942ff", "0f192300"],
        True,
        7,
        False,
    ),
    (
        "Gekko",
        "e370fa57-4757-3604-3648-499e1f642d3f",
        ["371c5cff", "0f1923ff", "3a2656ff", "0f192300"],
        True,
        6,
        True,
    ),
    (
        "Killjoy",
        "1e58de9c-4950-5125-93e9-a0aee9f98746",
        ["522162ff", "0f1923ff", "413950ff", "0f192300"],
        True,
        5,
        False,
    ),
    (
        "Phoenix",
        "eb93336a-449b-9c1b-0a54-a891f7921d69",
        ["74321cff", "0f1923ff", "262423ff", "0f192300"],
        True,
        3,
        False,
    ),
    (
        "Sage",
        "569fdd95-4d10-43ab-ca70-79becc718b46",
        ["1f5148ff", "0f1923ff", "102d23ff", "0f192300"],
        True,
        2,
        False,
    ),
    (
        "Neon",
        "bb2a4828-46eb-8cd1-e765-15848195d751",
        ["413476ff", "0f1923ff", "38328eff", "0f192300"],
        False,
        0,
        False,
    ),
    (
        "Fade",
        "dade69b4-4f5a-8528-247b-219e5a1facd6",
        ["1d2846ff", "0f1923ff", "18344cff", "0f192300"],
        False,
        0,
        False,
    ),
]


def _agent_static(name: str, uuid: str, gradient: list[str]) -> dict:
    return {
        "uuid": uuid,
        "displayName": name,
        "isPlayableCharacter": True,
        "displayIcon": f"{_MEDIA}/{uuid}/displayicon.png",
        "fullPortrait": f"{_MEDIA}/{uuid}/fullportrait.png",
        "background": f"{_MEDIA}/{uuid}/background.png",
        "backgroundGradientColors": gradient,
    }


def _build_tiers(uuid: str, unlocked_count: int, has_discrepancy: bool) -> tuple[list, list]:
    tiers: list[TierStatus] = []
    discrepancies: list[str] = []

    for index, reward_type, reward_kind, cost in _TEMPLATE:
        unlocked = index <= unlocked_count
        owned = unlocked

        if has_discrepancy:
            # Two unlocked tiers missing from entitlements, and one owned tier
            # the contract hasn't marked unlocked — the three classic mismatches.
            if index in (2, 3) and unlocked:
                owned = False
                discrepancies.append(
                    f"Tier {index} ({reward_type}) is marked unlocked but not "
                    f"found in owned entitlements."
                )
            elif index == unlocked_count + 1:
                owned = True
                discrepancies.append(
                    f"Tier {index} ({reward_type}) is owned but not marked "
                    f"unlocked by contract progression."
                )

        tiers.append(
            TierStatus(
                index=index,
                reward_type=reward_type,
                reward_kind=reward_kind,
                reward_uuid=f"{uuid}-tier-{index}",
                cost_kc=cost,
                unlocked=unlocked,
                owned=owned,
            )
        )

    return tiers, discrepancies


def build_demo_snapshot():
    # Imported here to avoid an import cycle at module load (service imports
    # this module lazily).
    from .service import Snapshot

    agents: list[AgentGearStatus] = []
    agents_static: dict = {}

    for name, uuid, gradient, recruited, unlocked_count, has_disc in _ROSTER:
        agents_static[uuid] = _agent_static(name, uuid, gradient)
        tiers, discrepancies = _build_tiers(uuid, unlocked_count, has_disc)
        agents.append(
            AgentGearStatus(
                agent_uuid=uuid,
                agent_name=name,
                contract_uuid=f"{uuid[:8]}-demo-contract",
                recruited=recruited,
                progression_level_reached=unlocked_count if recruited else 0,
                tiers=tiers,
                discrepancies=discrepancies,
            )
        )

    return Snapshot(
        agents=agents,
        balance=_DEMO_BALANCE,
        client_version="mock",
        shard="na",
        fetched_at=datetime.now(timezone.utc).isoformat(),
        reward_index={},
        agents_static=agents_static,
    )
