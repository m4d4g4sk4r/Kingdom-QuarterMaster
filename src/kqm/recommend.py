"""Pure scoring/planning logic: greedy next-purchase ranking and goal mode.

No I/O — operates entirely on `AgentGearStatus` objects from reconcile.py.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from .config import DEFAULT_REWARD_WEIGHTS, KC_CAP_WARNING_THRESHOLD
from .reconcile import AgentGearStatus, TierStatus


@dataclass
class PlannedPurchase:
    agent_name: str
    tier_index: int
    reward_type: str
    reward_kind: str
    cost_kc: int
    weight: float


@dataclass
class Plan:
    purchases: list[PlannedPurchase] = field(default_factory=list)
    total_cost: int = 0
    leftover_kc: int = 0
    near_cap_warning: bool = False


@dataclass
class GoalPlan:
    agent_name: str
    needs_recruit: bool
    recruit_cost: int
    purchases: list[PlannedPurchase] = field(default_factory=list)
    total_cost: int = 0
    affordable_cost: int = 0
    affordable_purchases: list[PlannedPurchase] = field(default_factory=list)
    remaining_needed: int = 0
    fully_affordable: bool = False


def warn_near_cap(balance: int, threshold: int = KC_CAP_WARNING_THRESHOLD) -> bool:
    return balance >= threshold


def _weight_for(tier: TierStatus, weights: dict) -> float:
    return weights.get(tier.reward_kind, 0)


def greedy_plan(
    agent_statuses: list[AgentGearStatus],
    balance: int,
    weights: dict | None = None,
) -> Plan:
    """Greedily buy the best-value next-purchasable tier across all agents.

    A tier is "next-purchasable" for an agent only once all earlier locked
    tiers for that agent have been included in the plan (tiers must be
    bought sequentially).
    """
    weights = weights or DEFAULT_REWARD_WEIGHTS

    # Min-heap keyed by (-score, cost, tie-break) so heapq pops best score first.
    heap = []
    counter = 0

    def push_next(agent: AgentGearStatus, next_locked_idx: int):
        nonlocal counter
        locked = agent.locked_tiers
        if next_locked_idx >= len(locked):
            return
        tier = locked[next_locked_idx]
        w = _weight_for(tier, weights)
        cost = tier.cost_kc
        score = (w / cost) if cost > 0 else float("inf") if w > 0 else 0.0
        counter += 1
        heapq.heappush(heap, (-score, cost, counter, agent, tier, next_locked_idx))

    for agent in agent_statuses:
        push_next(agent, 0)

    remaining = balance
    purchases: list[PlannedPurchase] = []

    while heap:
        neg_score, cost, _, agent, tier, locked_idx = heapq.heappop(heap)
        if cost > remaining:
            continue  # can't afford this one; a cheaper/better one may still be in the heap
        remaining -= cost
        purchases.append(
            PlannedPurchase(
                agent_name=agent.agent_name,
                tier_index=tier.index,
                reward_type=tier.reward_type,
                reward_kind=tier.reward_kind,
                cost_kc=cost,
                weight=_weight_for(tier, weights),
            )
        )
        push_next(agent, locked_idx + 1)

    total_cost = balance - remaining
    return Plan(
        purchases=purchases,
        total_cost=total_cost,
        leftover_kc=remaining,
        near_cap_warning=warn_near_cap(balance),
    )


def goal_plan(
    agent_statuses: list[AgentGearStatus],
    target_agent_name: str,
    balance: int,
    weights: dict | None = None,
    recruit_cost: int = 0,
) -> GoalPlan | None:
    """Cheapest sequential path to fully unlock (and recruit, if needed) one agent."""
    weights = weights or DEFAULT_REWARD_WEIGHTS

    agent = next(
        (a for a in agent_statuses if a.agent_name.lower() == target_agent_name.lower()),
        None,
    )
    if agent is None:
        return None

    needs_recruit = not agent.recruited
    purchases: list[PlannedPurchase] = []
    for tier in agent.locked_tiers:
        purchases.append(
            PlannedPurchase(
                agent_name=agent.agent_name,
                tier_index=tier.index,
                reward_type=tier.reward_type,
                reward_kind=tier.reward_kind,
                cost_kc=tier.cost_kc,
                weight=_weight_for(tier, weights),
            )
        )

    total_cost = (recruit_cost if needs_recruit else 0) + sum(p.cost_kc for p in purchases)

    remaining = balance
    affordable: list[PlannedPurchase] = []
    affordable_cost = 0
    if needs_recruit:
        if recruit_cost <= remaining:
            remaining -= recruit_cost
            affordable_cost += recruit_cost
        else:
            remaining = 0  # can't even recruit; nothing else is purchasable in sequence
    for p in purchases:
        if p.cost_kc <= remaining:
            remaining -= p.cost_kc
            affordable_cost += p.cost_kc
            affordable.append(p)
        else:
            break  # sequential purchase requirement — stop at first unaffordable tier

    return GoalPlan(
        agent_name=agent.agent_name,
        needs_recruit=needs_recruit,
        recruit_cost=recruit_cost if needs_recruit else 0,
        purchases=purchases,
        total_cost=total_cost,
        affordable_cost=affordable_cost,
        affordable_purchases=affordable,
        # Shortfall vs. the player's actual balance, not vs. affordable_cost:
        # leftover balance after the affordable prefix still counts toward
        # the next (currently unaffordable) tier.
        remaining_needed=max(0, total_cost - balance),
        fully_affordable=affordable_cost >= total_cost,
    )
