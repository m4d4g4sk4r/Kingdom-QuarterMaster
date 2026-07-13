import type { RewardIndexEntry, RewardKind, TierStatus } from "../api/types";

const KIND_LABEL: Record<string, string> = {
  spray: "Spray",
  playercard: "Player Card",
  title: "Title",
  buddy: "Gun Buddy",
  skin: "Weapon Skin",
  currency: "Kingdom Credits",
};

export function kindLabel(kind: RewardKind): string {
  return KIND_LABEL[kind] ?? (kind ? kind[0].toUpperCase() + kind.slice(1) : "Reward");
}

export interface ResolvedReward {
  name: string;
  iconUrl: string | null;
  kindLabel: string;
}

/**
 * Resolve a tier's display name/icon from the snapshot's reward_index, falling
 * back to the reward kind when the uuid isn't indexed (skins, currency, and the
 * entire mock dataset). Best-effort by design — see DESIGN_BRIEF.md.
 */
export function resolveReward(
  tier: TierStatus,
  rewardIndex: Record<string, RewardIndexEntry>,
): ResolvedReward {
  const entry = rewardIndex[tier.reward_uuid];
  const label = kindLabel(tier.reward_kind);
  return {
    name: entry?.name?.trim() ? entry.name : label,
    iconUrl: entry?.icon_url ?? null,
    kindLabel: label,
  };
}
