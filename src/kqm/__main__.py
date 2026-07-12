"""CLI entry point. Commands: status, locked, unlocked, recommend, ui.

This tool is strictly read-only: every network call it makes is a GET to
either 127.0.0.1 (local Riot Client), pd.{shard}.a.pvp.net (Riot's player
data endpoints), or valorant-api.com (public static game data). It never
prompts for a username or password.
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from . import config
from .auth import LocalApiUnavailableError, LockfileNotFoundError, ShardDetectionError
from .recommend import goal_plan, greedy_plan
from .render import render_goal_plan, render_greedy_plan, render_status, render_tier_list
from .riot_client import RiotApiError
from .service import fetch_snapshot, parse_weight_overrides
from .static_data import StaticDataError

console = Console()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kqm",
        description=(
            "Kingdom Quartermaster: local, read-only Valorant agent gear (contract) tracker."
        ),
    )
    parser.add_argument(
        "--shard",
        choices=config.SHARD_CHOICES,
        default=None,
        help="Override auto-detected shard/region (na, eu, ap, kr, pbe).",
    )
    parser.add_argument(
        "--refresh-static",
        action="store_true",
        help="Force-refetch static game data instead of using the on-disk cache.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="Show a summary of unlocked/locked tier counts per agent.")
    sub.add_parser("locked", help="List all not-yet-unlocked gear per agent, with KC cost.")
    sub.add_parser("unlocked", help="List all already-unlocked gear per agent.")

    rec = sub.add_parser("recommend", help="Recommend purchases based on current KC balance.")
    rec.add_argument(
        "--goal", help='Agent name to plan a full unlock for, e.g. "Gekko"', default=None
    )
    rec.add_argument(
        "--weight",
        action="append",
        default=[],
        metavar="KIND=WEIGHT",
        help="Override a reward-type weight, e.g. --weight buddy=10. Repeatable.",
    )

    ui = sub.add_parser("ui", help="Start the local web UI (opens your browser).")
    ui.add_argument(
        "--mock",
        action="store_true",
        help="Serve fixture data instead of live Riot data — no VALORANT required.",
    )
    ui.add_argument(
        "--port", type=int, default=8420, help="Port to serve the local UI on (default: 8420)."
    )

    return parser


def _fetch_snapshot_or_exit(args: argparse.Namespace):
    try:
        return fetch_snapshot(shard_override=args.shard, force_refresh_static=args.refresh_static)
    except (
        LockfileNotFoundError,
        LocalApiUnavailableError,
        ShardDetectionError,
        StaticDataError,
        RiotApiError,
    ) as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.command == "ui":
        from .webapp import run_ui

        run_ui(
            mock=args.mock,
            port=args.port,
            shard_override=args.shard,
            force_refresh_static=args.refresh_static,
        )
        return

    snapshot = _fetch_snapshot_or_exit(args)
    agents = snapshot.agents
    balance = snapshot.balance

    user_config = config.UserConfig.load()

    if args.command == "status":
        render_status(console, agents, balance)
    elif args.command == "locked":
        render_tier_list(console, agents, "Locked Gear", locked=True)
    elif args.command == "unlocked":
        render_tier_list(console, agents, "Unlocked Gear", locked=False)
    elif args.command == "recommend":
        weights = parse_weight_overrides(args.weight, user_config.reward_weights)
        if args.goal:
            target = args.goal
            plan = goal_plan(
                agents,
                target,
                balance,
                weights=weights,
                recruit_cost=user_config.agent_recruit_cost_kc,
            )
            if plan is None:
                console.print(f'[red]No agent named "{target}" found.[/red]')
                sys.exit(1)
            render_goal_plan(console, plan, balance)
        else:
            plan = greedy_plan(agents, balance, weights=weights)
            render_greedy_plan(console, plan, balance)


if __name__ == "__main__":
    main()
