"""Rich-table rendering for CLI output. No business logic lives here."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .config import KC_CAP
from .recommend import GoalPlan, Plan
from .reconcile import AgentGearStatus


def render_status(console: Console, agents: list[AgentGearStatus], balance: int) -> None:
    table = Table(title="Agent Gear Status")
    table.add_column("Agent")
    table.add_column("Recruited")
    table.add_column("Unlocked")
    table.add_column("Locked")
    table.add_column("Next Tier Cost (KC)")

    for agent in sorted(agents, key=lambda a: a.agent_name):
        locked = agent.locked_tiers
        next_cost = str(locked[0].cost_kc) if locked else "-"
        table.add_row(
            agent.agent_name,
            "yes" if agent.recruited else "no",
            str(len(agent.unlocked_tiers)),
            str(len(locked)),
            next_cost,
        )

    console.print(table)
    console.print(f"\n[bold]Kingdom Credits balance:[/bold] {balance:,} / {KC_CAP:,}")

    discrepancies = [(a.agent_name, d) for a in agents for d in a.discrepancies]
    if discrepancies:
        console.print("\n[yellow]Discrepancies found:[/yellow]")
        for name, d in discrepancies:
            console.print(f"  - {name}: {d}")


def render_tier_list(
    console: Console, agents: list[AgentGearStatus], title: str, locked: bool
) -> None:
    table = Table(title=title)
    table.add_column("Agent")
    table.add_column("Tier")
    table.add_column("Reward Type")
    if locked:
        table.add_column("Cost (KC)")

    for agent in sorted(agents, key=lambda a: a.agent_name):
        tiers = agent.locked_tiers if locked else agent.unlocked_tiers
        for tier in tiers:
            row = [agent.agent_name, str(tier.index), tier.reward_type]
            if locked:
                row.append(str(tier.cost_kc))
            table.add_row(*row)

    console.print(table)


def render_greedy_plan(console: Console, plan: Plan, balance: int) -> None:
    table = Table(title="Recommended Purchases")
    table.add_column("Agent")
    table.add_column("Tier")
    table.add_column("Reward Type")
    table.add_column("Cost (KC)")

    for p in plan.purchases:
        table.add_row(p.agent_name, str(p.tier_index), p.reward_type, str(p.cost_kc))

    console.print(table)
    console.print(
        f"\n[bold]Total cost:[/bold] {plan.total_cost:,} KC   "
        f"[bold]Leftover:[/bold] {plan.leftover_kc:,} KC"
    )
    if plan.near_cap_warning:
        console.print(
            Panel(
                f"Your balance ({balance:,} KC) is near the {KC_CAP:,} KC cap — "
                "any further earnings will be wasted until you spend some down.",
                style="bold red",
                title="Near cap warning",
            )
        )


def render_goal_plan(console: Console, plan: GoalPlan, balance: int) -> None:
    console.print(f"[bold]Goal:[/bold] fully unlock {plan.agent_name}'s gear")
    if plan.needs_recruit:
        console.print(f"  Requires recruiting {plan.agent_name} first: {plan.recruit_cost:,} KC")

    table = Table(title=f"{plan.agent_name} — remaining tiers")
    table.add_column("Tier")
    table.add_column("Reward Type")
    table.add_column("Cost (KC)")
    table.add_column("Affordable now?")

    affordable_indices = {p.tier_index for p in plan.affordable_purchases}
    for p in plan.purchases:
        table.add_row(
            str(p.tier_index),
            p.reward_type,
            str(p.cost_kc),
            "yes" if p.tier_index in affordable_indices else "no",
        )
    console.print(table)

    console.print(f"\n[bold]Total KC needed:[/bold] {plan.total_cost:,}")
    console.print(f"[bold]Affordable now with {balance:,} KC:[/bold] {plan.affordable_cost:,}")
    if plan.fully_affordable:
        console.print("[green]You can fully complete this goal right now.[/green]")
    else:
        console.print(
            f"[yellow]You need {plan.remaining_needed:,} more KC to finish this goal.[/yellow]"
        )
