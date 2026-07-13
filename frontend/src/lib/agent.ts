import type { AgentGearStatus, AgentStatic, TierStatus } from "../api/types";

/** valorant-api gradient colors are 8-digit rrggbbaa; convert to #rrggbb + alpha. */
export function rgba(hex8: string): string {
  const h = hex8.replace(/^#/, "").padEnd(8, "f");
  const r = parseInt(h.slice(0, 2), 16);
  const g = parseInt(h.slice(2, 4), 16);
  const b = parseInt(h.slice(4, 6), 16);
  const a = parseInt(h.slice(6, 8), 16) / 255;
  return `rgba(${r}, ${g}, ${b}, ${a})`;
}

/** The single most saturated stop of an agent's gradient — the identity color. */
export function agentAccent(agentStatic?: AgentStatic): string | null {
  const cols = agentStatic?.backgroundGradientColors;
  if (!cols || cols.length === 0) return null;
  return rgba(cols[0]);
}

/** A soft top-to-bottom wash for a header band, clipped low so chrome stays grey. */
export function agentWash(agentStatic?: AgentStatic): string | undefined {
  const cols = agentStatic?.backgroundGradientColors;
  if (!cols || cols.length === 0) return undefined;
  const a = rgba(cols[0]);
  const b = cols[2] ? rgba(cols[2]) : a;
  return `linear-gradient(120deg, ${a}, ${b} 55%, transparent)`;
}

export const unlockedTiers = (a: AgentGearStatus): TierStatus[] =>
  a.tiers.filter((t) => t.unlocked);

export const lockedTiers = (a: AgentGearStatus): TierStatus[] =>
  a.tiers.filter((t) => !t.unlocked);

/**
 * Tiers unlock sequentially, so exactly one locked tier is actionable: the
 * lowest-index locked tier. Returns null when the contract is complete.
 */
export function nextTier(a: AgentGearStatus): TierStatus | null {
  const locked = lockedTiers(a);
  if (locked.length === 0) return null;
  return locked.reduce((lo, t) => (t.index < lo.index ? t : lo));
}

export const remainingCost = (a: AgentGearStatus): number =>
  lockedTiers(a).reduce((sum, t) => sum + t.cost_kc, 0);

export interface AgentProgress {
  unlocked: number;
  total: number;
  fraction: number;
  complete: boolean;
}

export function progress(a: AgentGearStatus): AgentProgress {
  const total = a.tiers.length;
  const unlocked = unlockedTiers(a).length;
  return {
    unlocked,
    total,
    fraction: total === 0 ? 0 : unlocked / total,
    complete: total > 0 && unlocked === total,
  };
}
