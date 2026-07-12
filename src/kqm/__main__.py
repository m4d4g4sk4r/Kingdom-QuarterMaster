"""CLI entry point. Commands: status, locked, unlocked, recommend.

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
from .auth import (
    LocalApiUnavailableError,
    LockfileNotFoundError,
    ShardDetectionError,
    detect_shard,
    fetch_local_session,
    read_lockfile,
)
from .recommend import goal_plan, greedy_plan
from .reconcile import reconcile
from .render import render_goal_plan, render_greedy_plan, render_status, render_tier_list
from .riot_client import RiotApiError, RiotClient
from .static_data import StaticDataError, load_static_data

console = Console()


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="kqm",
        description=(
            "Kingdom Quartermaster: local, read-only Valorant agent gear "
            "(contract) tracker."
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

    sub.add_parser("status", help="Show a summary of unlocked/locked gear per agent.")
    sub.add_parser("locked", help="List all not-yet-unlocked gear per agent, with KC cost.")
    sub.add_parser("unlocked", help="List all already-unlocked gear per agent.")

    rec = sub.add_parser("recommend", help="Recommend purchases based on current KC balance.")
    rec.add_argument("--goal", help='Goal mode, e.g. "agent:Gekko"', default=None)
    rec.add_argument(
        "--weight",
        action="append",
        default=[],
        metavar="KIND=WEIGHT",
        help="Override a reward-type weight, e.g. --weight buddy=10. Repeatable.",
    )

    return parser


def _parse_weight_overrides(raw: list[str], base: dict) -> dict:
    weights = dict(base)
    for item in raw:
        if "=" not in item:
            continue
        kind, _, value = item.partition("=")
        try:
            weights[kind.strip()] = float(value.strip())
        except ValueError:
            continue
    return weights


def _build_client_and_session(shard_override: str | None):
    import httpx

    lockfile = read_lockfile()

    # verify=False is required for this one call: the Riot Client's local
    # API server uses a self-signed cert on 127.0.0.1. No other host is
    # ever contacted with verification disabled.
    with httpx.Client(verify=False, timeout=10.0) as local_client:
        session = fetch_local_session(local_client, lockfile)
        shard = shard_override or detect_shard(local_client, lockfile)

    return lockfile, session, shard


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    import httpx

    try:
        lockfile, session, shard = _build_client_and_session(args.shard)
    except LockfileNotFoundError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except LocalApiUnavailableError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)
    except ShardDetectionError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    try:
        with httpx.Client(timeout=15.0) as static_client:
            static_data = load_static_data(static_client, force_refresh=args.refresh_static)
    except StaticDataError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    try:
        with httpx.Client(timeout=15.0) as pd_client:
            client = RiotClient(
                http_client=pd_client,
                shard=shard,
                session=session,
                lockfile=lockfile,
                client_version=static_data.version,
            )
            wallet = client.get_wallet()
            contracts_response = client.get_contracts()
            owned = client.get_all_owned_item_uuids()
    except RiotApiError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    balance = wallet["Balances"].get(static_data.kingdom_credits_uuid, 0)

    agents = reconcile(
        static_data.agents_by_uuid, static_data.contracts, contracts_response, owned
    )

    user_config = config.UserConfig.load()

    if args.command == "status":
        render_status(console, agents, balance)
    elif args.command == "locked":
        render_tier_list(console, agents, "Locked Gear", locked=True)
    elif args.command == "unlocked":
        render_tier_list(console, agents, "Unlocked Gear", locked=False)
    elif args.command == "recommend":
        weights = _parse_weight_overrides(args.weight, user_config.reward_weights)
        if args.goal:
            if not args.goal.startswith("agent:"):
                console.print('[red]--goal must look like "agent:<name>"[/red]')
                sys.exit(1)
            target = args.goal.split(":", 1)[1]
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

