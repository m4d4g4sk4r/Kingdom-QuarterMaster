"""Local-only FastAPI app exposing the same read-only data as the CLI.

Every route is a GET. Binds to 127.0.0.1 only (see run_ui) — this is never
meant to be reachable from anywhere but the machine running it.
"""

from __future__ import annotations

from dataclasses import asdict

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse

from . import config
from .auth import LocalApiUnavailableError, LockfileNotFoundError, ShardDetectionError
from .recommend import goal_plan, greedy_plan
from .riot_client import RiotApiError, SchemaDriftError
from .service import fetch_snapshot, parse_weight_overrides
from .static_data import StaticDataError

# Order matters: SchemaDriftError is a RiotApiError subclass, but both are
# registered explicitly with FastAPI so each gets its own status/code rather
# than falling back to the parent's.
_ERROR_STATUS = {
    LockfileNotFoundError: 503,
    LocalApiUnavailableError: 503,
    ShardDetectionError: 400,
    SchemaDriftError: 502,
    RiotApiError: 502,
    StaticDataError: 502,
}

_ERROR_CODE = {
    LockfileNotFoundError: "lockfile_not_found",
    LocalApiUnavailableError: "local_api_unavailable",
    ShardDetectionError: "shard_detection_failed",
    SchemaDriftError: "schema_drift",
    RiotApiError: "riot_api_error",
    StaticDataError: "static_data_error",
}


async def _handle_known_error(request, exc: Exception) -> JSONResponse:
    exc_type = type(exc)
    status_code = _ERROR_STATUS[exc_type]
    code = _ERROR_CODE[exc_type]
    content = {"error": {"code": code, "message": str(exc)}}
    return JSONResponse(status_code=status_code, content=content)


def create_app(
    mock: bool = False,
    shard_override: str | None = None,
    force_refresh_static: bool = False,
) -> FastAPI:
    app = FastAPI(title="Kingdom Quartermaster")

    def _snapshot():
        return fetch_snapshot(
            shard_override=shard_override,
            force_refresh_static=force_refresh_static,
            mock=mock,
        )

    for exc_type in _ERROR_STATUS:
        app.add_exception_handler(exc_type, _handle_known_error)

    @app.get("/")
    def root():
        return {
            "status": "ok",
            "message": "Kingdom Quartermaster local API. See /api/snapshot, "
            "/api/recommend, /api/goal/{agent_name}.",
        }

    @app.get("/api/snapshot")
    def get_snapshot():
        return asdict(_snapshot())

    @app.get("/api/recommend")
    def get_recommend(weight: list[str] = Query(default=[])):  # noqa: B008
        snapshot = _snapshot()
        user_config = config.UserConfig.load()
        weights = parse_weight_overrides(weight, user_config.reward_weights)
        plan = greedy_plan(snapshot.agents, snapshot.balance, weights=weights)
        return {"balance": snapshot.balance, "plan": asdict(plan)}

    @app.get("/api/goal/{agent_name:path}")
    def get_goal(agent_name: str, weight: list[str] = Query(default=[])):  # noqa: B008
        snapshot = _snapshot()
        user_config = config.UserConfig.load()
        weights = parse_weight_overrides(weight, user_config.reward_weights)
        plan = goal_plan(
            snapshot.agents,
            agent_name,
            snapshot.balance,
            weights=weights,
            recruit_cost=user_config.agent_recruit_cost_kc,
        )
        if plan is None:
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "code": "agent_not_found",
                        "message": f'No agent named "{agent_name}" found.',
                    }
                },
            )
        return {"balance": snapshot.balance, "plan": asdict(plan)}

    return app


def run_ui(
    mock: bool = False,
    port: int = 8420,
    shard_override: str | None = None,
    force_refresh_static: bool = False,
) -> None:
    import threading
    import webbrowser

    import uvicorn

    app = create_app(
        mock=mock, shard_override=shard_override, force_refresh_static=force_refresh_static
    )
    url = f"http://127.0.0.1:{port}"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
