from kqm.recommend import goal_plan, greedy_plan, warn_near_cap
from kqm.reconcile import AgentGearStatus, TierStatus

WEIGHTS = {"buddy": 5, "playercard": 4, "title": 2, "spray": 1, "skin": 3, "currency": 0}


def make_agent(name, recruited, tiers):
    """tiers: list of (index, reward_kind, cost_kc, unlocked)"""
    status = AgentGearStatus(
        agent_uuid=f"{name}-uuid",
        agent_name=name,
        contract_uuid=f"{name}-contract",
        recruited=recruited,
        progression_level_reached=sum(1 for t in tiers if t[3]),
    )
    for idx, kind, cost, unlocked in tiers:
        status.tiers.append(
            TierStatus(
                index=idx,
                reward_type=kind.capitalize(),
                reward_kind=kind,
                reward_uuid=f"{name}-{idx}",
                cost_kc=cost,
                unlocked=unlocked,
                owned=None,
            )
        )
    return status


def test_greedy_plan_picks_best_value_first():
    # Two different agents' first (only currently purchasable) tier compete:
    # buddy: weight 5 / cost 1000 = 0.005 (best)
    # spray: weight 1 / cost 1000 = 0.001
    agent_a = make_agent("Fade", True, [(1, "spray", 1000, False)])
    agent_b = make_agent("Gekko", True, [(1, "buddy", 1000, False)])
    plan = greedy_plan([agent_a, agent_b], balance=1000, weights=WEIGHTS)
    assert len(plan.purchases) == 1
    assert plan.purchases[0].reward_kind == "buddy"
    assert plan.total_cost == 1000
    assert plan.leftover_kc == 0


def test_greedy_plan_respects_sequential_tier_order():
    # tier 2 (buddy) has better value/cost than tier 1 (spray), but tier 1
    # must be bought first since tiers are sequential for a single agent.
    agent = make_agent(
        "Gekko",
        True,
        [
            (1, "spray", 500, False),
            (2, "buddy", 500, False),
        ],
    )
    plan = greedy_plan([agent], balance=500, weights=WEIGHTS)
    assert len(plan.purchases) == 1
    assert plan.purchases[0].reward_kind == "spray"  # tier 1, even though lower weight


def test_greedy_plan_skips_unaffordable_and_takes_cheaper_alternative():
    agent_a = make_agent("Gekko", True, [(1, "buddy", 5000, False)])
    agent_b = make_agent("Fade", True, [(1, "spray", 500, False)])
    plan = greedy_plan([agent_a, agent_b], balance=500, weights=WEIGHTS)
    assert len(plan.purchases) == 1
    assert plan.purchases[0].agent_name == "Fade"
    assert plan.leftover_kc == 0


def test_greedy_plan_zero_balance_returns_empty_plan():
    agent = make_agent("Gekko", True, [(1, "buddy", 1000, False)])
    plan = greedy_plan([agent], balance=0, weights=WEIGHTS)
    assert plan.purchases == []
    assert plan.total_cost == 0
    assert plan.leftover_kc == 0


def test_greedy_plan_only_considers_locked_tiers():
    agent = make_agent(
        "Gekko",
        True,
        [
            (1, "buddy", 1000, True),  # already unlocked
            (2, "spray", 1000, False),
        ],
    )
    plan = greedy_plan([agent], balance=1000, weights=WEIGHTS)
    assert len(plan.purchases) == 1
    assert plan.purchases[0].reward_kind == "spray"


def test_goal_plan_sums_sequential_locked_tiers():
    agent = make_agent(
        "Gekko",
        True,
        [
            (1, "spray", 1000, True),
            (2, "buddy", 3000, False),
            (3, "title", 1500, False),
        ],
    )
    plan = goal_plan([agent], "Gekko", balance=10_000, weights=WEIGHTS, recruit_cost=8000)
    assert plan is not None
    assert plan.needs_recruit is False
    assert plan.total_cost == 4500
    assert plan.fully_affordable is True
    assert plan.remaining_needed == 0


def test_goal_plan_includes_recruit_cost_when_not_recruited():
    agent = make_agent("Fade", False, [(1, "spray", 1000, False)])
    plan = goal_plan([agent], "Fade", balance=20_000, weights=WEIGHTS, recruit_cost=8000)
    assert plan.needs_recruit is True
    assert plan.total_cost == 9000
    assert plan.fully_affordable is True


def test_goal_plan_partial_affordability_stops_at_first_unaffordable_tier():
    agent = make_agent(
        "Gekko",
        True,
        [
            (1, "spray", 1000, False),
            (2, "buddy", 3000, False),
        ],
    )
    plan = goal_plan([agent], "Gekko", balance=1500, weights=WEIGHTS, recruit_cost=8000)
    assert plan.affordable_cost == 1000
    assert len(plan.affordable_purchases) == 1
    assert plan.fully_affordable is False
    assert plan.remaining_needed == 4000 - 1500


def test_goal_plan_unknown_agent_returns_none():
    agent = make_agent("Gekko", True, [(1, "spray", 1000, False)])
    plan = goal_plan([agent], "NotAnAgent", balance=1000, weights=WEIGHTS, recruit_cost=8000)
    assert plan is None


def test_goal_plan_case_insensitive_name_match():
    agent = make_agent("Gekko", True, [(1, "spray", 1000, False)])
    plan = goal_plan([agent], "gekko", balance=1000, weights=WEIGHTS, recruit_cost=8000)
    assert plan is not None
    assert plan.agent_name == "Gekko"


def test_warn_near_cap_thresholds():
    assert warn_near_cap(9500, threshold=9000) is True
    assert warn_near_cap(9000, threshold=9000) is True
    assert warn_near_cap(8999, threshold=9000) is False
