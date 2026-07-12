"""Pure functions joining static contract definitions with a player's live
progression/entitlements into a per-agent unlocked/locked gear model.

Nothing in this module performs I/O — it only transforms already-fetched
data, which makes it straightforward to unit test against fixtures.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .config import REWARD_TYPE_MAP

# Maps our internal reward_kind -> the owned-items itemType key (config.ITEM_TYPE_IDS)
# used to check ownership. Rewards with no entry here (e.g. "currency") can't
# be ownership-checked and are skipped for discrepancy purposes.
REWARD_KIND_TO_ITEM_TYPE_KEY = {
    "spray": "sprays",
    "playercard": "playercards",
    "title": "titles",
    "buddy": "buddies",
    "skin": "skins",
}


@dataclass
class TierStatus:
    index: int  # 1-based position within the agent's flattened contract
    reward_type: str  # raw valorant-api.com reward.type, e.g. "Spray"
    reward_kind: str  # short internal key, e.g. "spray"
    reward_uuid: str
    cost_kc: int
    unlocked: bool
    owned: bool | None  # None when ownership can't be checked for this reward kind


@dataclass
class AgentGearStatus:
    agent_uuid: str
    agent_name: str
    contract_uuid: str
    recruited: bool
    progression_level_reached: int
    tiers: list[TierStatus] = field(default_factory=list)
    discrepancies: list[str] = field(default_factory=list)

    @property
    def unlocked_tiers(self) -> list[TierStatus]:
        return [t for t in self.tiers if t.unlocked]

    @property
    def locked_tiers(self) -> list[TierStatus]:
        return [t for t in self.tiers if not t.unlocked]


def _flatten_levels(contract_content: dict) -> list[dict]:
    levels = []
    for chapter in contract_content.get("chapters", []):
        levels.extend(chapter.get("levels", []))
    return levels


def reconcile(
    agents_by_uuid: dict,
    static_contracts: list,
    live_contracts_response: dict,
    owned_by_item_type_key: dict,
) -> list[AgentGearStatus]:
    """Build per-agent gear status.

    agents_by_uuid: static agent uuid -> agent dict (needs "displayName")
    static_contracts: raw list from valorant-api.com /v1/contracts
    live_contracts_response: raw dict from pd.../contracts/v1/contracts/{puuid}
    owned_by_item_type_key: dict like {"sprays": {uuid, ...}, "agents": {...}, ...}
        using the same keys as config.ITEM_TYPE_IDS
    """
    live_by_contract_id = {
        c["ContractDefinitionID"]: c for c in live_contracts_response.get("Contracts", [])
    }
    owned_agent_uuids = owned_by_item_type_key.get("agents", set())

    results: list[AgentGearStatus] = []

    for contract in static_contracts:
        content = contract.get("content", {})
        if content.get("relationType") != "Agent":
            continue

        agent_uuid = content.get("relationUuid")
        agent = agents_by_uuid.get(agent_uuid)
        if agent is None:
            continue  # static data drift: contract points to an unknown agent

        levels = _flatten_levels(content)
        live = live_by_contract_id.get(contract["uuid"])
        progression_level_reached = live["ProgressionLevelReached"] if live else 0

        status = AgentGearStatus(
            agent_uuid=agent_uuid,
            agent_name=agent.get("displayName", "Unknown Agent"),
            contract_uuid=contract["uuid"],
            # Default/starter agents (e.g. Brimstone, Jett, Phoenix, Sage, Sova) are
            # granted without a store entitlement record, so entitlement presence
            # alone false-negatives on them. Any contract progression is also
            # treated as proof of recruitment. Known caveat: a brand-new account
            # that owns a starter agent but hasn't played a single contract level
            # yet will still show that agent as not recruited.
            recruited=(agent_uuid in owned_agent_uuids) or (progression_level_reached > 0),
            progression_level_reached=progression_level_reached,
        )

        for i, level in enumerate(levels, start=1):
            reward = level.get("reward", {})
            raw_type = reward.get("type", "")
            reward_kind = REWARD_TYPE_MAP.get(raw_type, raw_type.lower())
            reward_uuid = reward.get("uuid", "")
            unlocked = i <= progression_level_reached

            owned = None
            item_type_key = REWARD_KIND_TO_ITEM_TYPE_KEY.get(reward_kind)
            if item_type_key is not None:
                owned_set = owned_by_item_type_key.get(item_type_key, set())
                owned = reward_uuid in owned_set

            tier = TierStatus(
                index=i,
                reward_type=raw_type,
                reward_kind=reward_kind,
                reward_uuid=reward_uuid,
                cost_kc=level.get("doughCost", 0),
                unlocked=unlocked,
                owned=owned,
            )
            status.tiers.append(tier)

            if owned is True and not unlocked:
                status.discrepancies.append(
                    f"Tier {i} ({raw_type}) is owned but not marked unlocked by "
                    "contract progression."
                )
            if owned is False and unlocked:
                status.discrepancies.append(
                    f"Tier {i} ({raw_type}) is marked unlocked but not found in owned entitlements."
                )

        results.append(status)

    return results
