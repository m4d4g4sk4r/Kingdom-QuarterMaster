// Types mirror the exact serialized shapes returned by src/kqm/webapp.py.
// Verified against the dataclasses in reconcile.py / recommend.py / service.py.

export type RewardKind =
  | "spray"
  | "playercard"
  | "title"
  | "buddy"
  | "skin"
  | "currency"
  | string;

export interface TierStatus {
  index: number; // 1-based
  reward_type: string; // raw, e.g. "Spray"
  reward_kind: RewardKind; // short key, e.g. "spray"
  reward_uuid: string;
  cost_kc: number;
  unlocked: boolean;
  owned: boolean | null; // tri-state: null = uncheckable
}

export interface AgentGearStatus {
  agent_uuid: string;
  agent_name: string;
  contract_uuid: string;
  recruited: boolean;
  progression_level_reached: number;
  tiers: TierStatus[];
  discrepancies: string[];
  // NOTE: unlocked_tiers / locked_tiers are Python @property and are NOT in the
  // JSON — derive them from `tiers` (see lib/agent.ts).
}

export interface RewardIndexEntry {
  name: string;
  icon_url: string | null;
}

/** Raw valorant-api agent object; only the first three keys exist in mock mode. */
export interface AgentStatic {
  uuid: string;
  displayName: string;
  isPlayableCharacter: boolean;
  displayIcon?: string;
  fullPortrait?: string;
  bustPortrait?: string;
  background?: string;
  backgroundGradientColors?: string[]; // 8-digit rrggbbaa
  [key: string]: unknown;
}

export interface Snapshot {
  agents: AgentGearStatus[];
  balance: number;
  client_version: string; // "mock" in mock mode
  shard: string;
  fetched_at: string; // ISO-8601 UTC
  reward_index: Record<string, RewardIndexEntry>;
  agents_static: Record<string, AgentStatic>;
}

export interface PlannedPurchase {
  agent_name: string;
  tier_index: number;
  reward_type: string;
  reward_kind: RewardKind;
  cost_kc: number;
  weight: number;
}

export interface Plan {
  purchases: PlannedPurchase[];
  total_cost: number;
  leftover_kc: number;
  near_cap_warning: boolean;
}

export interface RecommendResponse {
  balance: number;
  plan: Plan;
}

export interface GoalPlan {
  agent_name: string;
  needs_recruit: boolean;
  recruit_cost: number;
  purchases: PlannedPurchase[];
  total_cost: number;
  affordable_cost: number;
  affordable_purchases: PlannedPurchase[];
  remaining_needed: number;
  fully_affordable: boolean;
}

export interface GoalResponse {
  balance: number;
  plan: GoalPlan;
}

/** Structured error codes from webapp.py's _handle_known_error. */
export type ApiErrorCode =
  | "lockfile_not_found"
  | "local_api_unavailable"
  | "shard_detection_failed"
  | "schema_drift"
  | "riot_api_error"
  | "static_data_error"
  | "agent_not_found"
  | "network_error"
  | "unknown";

export class ApiError extends Error {
  code: ApiErrorCode;
  status: number;
  constructor(code: ApiErrorCode, message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.code = code;
    this.status = status;
  }
}

export const KC_CAP = 10_000;

/** The reward kinds the recommender weights, in ledger order. */
export const WEIGHTED_KINDS: RewardKind[] = [
  "buddy",
  "playercard",
  "skin",
  "title",
  "spray",
];
