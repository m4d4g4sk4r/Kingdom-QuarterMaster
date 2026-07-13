import {
  ApiError,
  type ApiErrorCode,
  type GoalResponse,
  type RecommendResponse,
  type Snapshot,
} from "./types";

async function request<T>(path: string): Promise<T> {
  let resp: Response;
  try {
    resp = await fetch(path, { headers: { Accept: "application/json" } });
  } catch {
    // Server unreachable (kqm ui not running, or connection dropped).
    throw new ApiError(
      "network_error",
      "Can't reach the local requisition server.",
      0,
    );
  }

  if (!resp.ok) {
    let code: ApiErrorCode = "unknown";
    let message = `Request failed (${resp.status}).`;
    try {
      const body = await resp.json();
      if (body?.error) {
        code = (body.error.code as ApiErrorCode) ?? "unknown";
        message = body.error.message ?? message;
      }
    } catch {
      /* non-JSON error body — keep defaults */
    }
    throw new ApiError(code, message, resp.status);
  }

  return (await resp.json()) as T;
}

export function getSnapshot(): Promise<Snapshot> {
  return request<Snapshot>("/api/snapshot");
}

/** weights: kind -> value; sent as repeated ?weight=kind=value params. */
export function getRecommend(
  weights?: Record<string, number>,
): Promise<RecommendResponse> {
  const params = new URLSearchParams();
  if (weights) {
    for (const [kind, value] of Object.entries(weights)) {
      params.append("weight", `${kind}=${value}`);
    }
  }
  const qs = params.toString();
  return request<RecommendResponse>(`/api/recommend${qs ? `?${qs}` : ""}`);
}

export function getGoal(
  agentName: string,
  weights?: Record<string, number>,
): Promise<GoalResponse> {
  const params = new URLSearchParams();
  if (weights) {
    for (const [kind, value] of Object.entries(weights)) {
      params.append("weight", `${kind}=${value}`);
    }
  }
  const qs = params.toString();
  return request<GoalResponse>(
    `/api/goal/${encodeURIComponent(agentName)}${qs ? `?${qs}` : ""}`,
  );
}
