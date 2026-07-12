import json
from pathlib import Path

import pytest

from kqm.reconcile import reconcile

FIXTURES = Path(__file__).parent / "fixtures"


def load(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def agents_by_uuid():
    return {a["uuid"]: a for a in load("static_agents.json")}


@pytest.fixture
def static_contracts():
    return load("static_contracts.json")


@pytest.fixture
def live_contracts():
    return load("contracts.json")


@pytest.fixture
def owned_by_item_type_key():
    owned_agents = load("owned_agents.json")
    owned_sprays = load("owned_sprays.json")

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


def test_reconcile_produces_one_status_per_agent_contract(
    agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key
):
    result = reconcile(agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key)
    names = {s.agent_name for s in result}
    assert names == {"Gekko", "Fade"}


def test_tier_unlock_boundary_matches_progression_level_reached(
    agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key
):
    result = reconcile(agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key)
    gekko = next(s for s in result if s.agent_name == "Gekko")

    # ProgressionLevelReached = 3 in fixture -> tiers 1-3 unlocked, 4+ locked
    assert [t.index for t in gekko.unlocked_tiers] == [1, 2, 3]
    assert [t.index for t in gekko.locked_tiers] == [4, 5, 6, 7, 8, 9, 10]


def test_locked_tier_cost_uses_dough_cost_field(
    agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key
):
    result = reconcile(agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key)
    gekko = next(s for s in result if s.agent_name == "Gekko")
    tier4 = next(t for t in gekko.tiers if t.index == 4)
    assert tier4.cost_kc == 3000
    assert tier4.reward_kind == "buddy"


def test_agent_with_no_live_contract_entry_defaults_to_zero_progression(
    agents_by_uuid, static_contracts, owned_by_item_type_key
):
    live_contracts_missing_fade = {
        "Contracts": [
            c
            for c in load("contracts.json")["Contracts"]
            if c["ContractDefinitionID"] != "7ab88318-4707-407a-9723-fb897d3e9ea1"
        ]
    }
    result = reconcile(
        agents_by_uuid, static_contracts, live_contracts_missing_fade, owned_by_item_type_key
    )
    fade = next(s for s in result if s.agent_name == "Fade")
    assert fade.progression_level_reached == 0
    assert all(not t.unlocked for t in fade.tiers)


def test_recruited_flag_from_owned_agents(
    agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key
):
    result = reconcile(agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key)
    gekko = next(s for s in result if s.agent_name == "Gekko")
    fade = next(s for s in result if s.agent_name == "Fade")
    assert gekko.recruited is True
    assert fade.recruited is False


def test_recruited_flag_true_via_progression_even_without_owned_entitlement(
    agents_by_uuid, static_contracts, owned_by_item_type_key
):
    # Default/starter agents (e.g. Brimstone, Jett, Phoenix, Sage, Sova) never
    # get a store entitlement record, so contract progression alone must also
    # count as proof of recruitment. Fade isn't in owned_by_item_type_key["agents"]
    # here, but has progressed past level 0.
    live_contracts_fade_progressed = {
        "Contracts": [
            c if c["ContractDefinitionID"] != "7ab88318-4707-407a-9723-fb897d3e9ea1"
            else {**c, "ProgressionLevelReached": 2}
            for c in load("contracts.json")["Contracts"]
        ]
    }
    result = reconcile(
        agents_by_uuid, static_contracts, live_contracts_fade_progressed, owned_by_item_type_key
    )
    fade = next(s for s in result if s.agent_name == "Fade")
    assert fade.recruited is True


def test_discrepancy_detected_for_owned_but_locked_reward(
    agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key
):
    # fixture: spray-gekko-2 is tier 5 (locked, since ProgressionLevelReached=3)
    # but is present in owned_sprays.json
    result = reconcile(agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key)
    gekko = next(s for s in result if s.agent_name == "Gekko")
    assert any("Tier 5" in d for d in gekko.discrepancies)


def test_known_reward_kind_with_empty_owned_set_is_false_not_none(
    agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key
):
    result = reconcile(agents_by_uuid, static_contracts, live_contracts, owned_by_item_type_key)
    gekko = next(s for s in result if s.agent_name == "Gekko")
    skin_tier = next(t for t in gekko.tiers if t.reward_kind == "skin")
    assert skin_tier.owned is False  # "skins" key present but empty set -> False, not None


def test_currency_reward_kind_has_no_ownership_check(
    agents_by_uuid, live_contracts, owned_by_item_type_key
):
    contracts_with_currency_reward = [
        {
            "uuid": "currency-contract-1",
            "content": {
                "relationType": "Agent",
                "relationUuid": "e370fa57-4757-3604-3648-499e1f642d3f",
                "chapters": [
                    {
                        "levels": [
                            {
                                "reward": {"type": "Currency", "uuid": "vp-reward", "amount": 100},
                                "doughCost": 500,
                            }
                        ]
                    }
                ],
            },
        }
    ]
    result = reconcile(
        agents_by_uuid, contracts_with_currency_reward, live_contracts, owned_by_item_type_key
    )
    gekko = result[0]
    assert gekko.tiers[0].reward_kind == "currency"
    assert gekko.tiers[0].owned is None
