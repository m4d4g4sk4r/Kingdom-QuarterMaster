import { Link, useParams } from "react-router-dom";
import { useSnapshot } from "../api/hooks";
import { ErrorScreen, LoadingScreen } from "../components/StateScreen";
import { StatusStamp } from "../components/StatusStamp";
import { KindGlyph } from "../components/KindGlyph";
import { agentAccent, agentWash, nextTier, progress, remainingCost } from "../lib/agent";
import { resolveReward } from "../lib/reward";
import { kc, tierNo } from "../lib/format";
import type { AgentGearStatus, RewardIndexEntry, TierStatus } from "../api/types";

function TierRow({
  tier,
  isNext,
  rewardIndex,
}: {
  tier: TierStatus;
  isNext: boolean;
  rewardIndex: Record<string, RewardIndexEntry>;
}) {
  const r = resolveReward(tier, rewardIndex);
  const issued = tier.unlocked;
  const missingEntitlement = tier.unlocked && tier.owned === false;

  return (
    <li
      className="relative flex items-center gap-4 border-b border-line px-4 py-3 last:border-b-0"
      style={
        isNext
          ? { background: "rgba(230,162,60,0.06)", boxShadow: "inset 3px 0 0 var(--color-amber)" }
          : undefined
      }
    >
      <span
        className="tnum w-7 shrink-0 font-display text-sm"
        style={{ color: isNext ? "var(--color-amber)" : "var(--color-muted)" }}
      >
        {tierNo(tier.index)}
      </span>

      <span
        className="shrink-0"
        style={{
          color: issued
            ? "var(--color-issued)"
            : isNext
              ? "var(--color-amber)"
              : "var(--color-muted)",
        }}
      >
        <KindGlyph kind={tier.reward_kind} />
      </span>

      <div className="min-w-0 flex-1">
        <div className="truncate text-sm text-paper">{r.name}</div>
        <div className="font-display text-[0.62rem] uppercase tracking-[0.14em] text-muted">
          {r.kindLabel}
          {missingEntitlement && (
            <span className="text-oxide"> · not in entitlements</span>
          )}
          {tier.owned === null && !issued && (
            <span className="text-muted"> · ownership uncheckable</span>
          )}
        </div>
      </div>

      <span className="tnum w-24 shrink-0 text-right text-sm text-paper">
        {kc(tier.cost_kc)} <span className="text-muted">KC</span>
      </span>

      <span className="w-32 shrink-0 text-right">
        {issued ? (
          <StatusStamp label="Issued" tone="issued" size="sm" rotate={-2} animate={false} />
        ) : isNext ? (
          <StatusStamp label="Authorize" tone="amber" size="sm" rotate={2} />
        ) : (
          <StatusStamp label="Pending req." tone="muted" size="sm" rotate={-1} animate={false} />
        )}
      </span>
    </li>
  );
}

function Detail({
  agent,
  agentStatic,
  rewardIndex,
}: {
  agent: AgentGearStatus;
  agentStatic?: import("../api/types").AgentStatic;
  rewardIndex: Record<string, RewardIndexEntry>;
}) {
  const accent = agentAccent(agentStatic) ?? "var(--color-line)";
  const wash = agentWash(agentStatic);
  const portrait = agentStatic?.fullPortrait ?? agentStatic?.displayIcon;
  const prog = progress(agent);
  const next = nextTier(agent);
  const remaining = remainingCost(agent);

  return (
    <div className="space-y-6">
      <Link
        to="/"
        className="inline-flex items-center gap-2 font-display text-xs uppercase tracking-[0.16em] text-muted hover:text-paper"
      >
        ‹ Manifest
      </Link>

      {/* header band */}
      <header className="relative overflow-hidden border border-line bg-steel">
        <span aria-hidden className="absolute inset-0 opacity-50" style={{ background: wash }} />
        <span aria-hidden className="absolute left-0 top-0 h-full w-1.5" style={{ background: accent }} />
        <div className="relative flex items-center gap-5 p-5 sm:p-6">
          {portrait && (
            <img
              src={portrait}
              alt=""
              className="h-24 w-24 shrink-0 border border-line bg-ink object-cover"
            />
          )}
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-3">
              <h1 className="text-3xl text-paper">{agent.agent_name}</h1>
              {agent.recruited ? (
                <StatusStamp label="Recruited" tone="issued" rotate={-2} />
              ) : (
                <StatusStamp label="Not recruited" tone="amber" rotate={2} />
              )}
            </div>
            <p className="tnum mt-2 text-xs text-muted">
              Contract {agent.contract_uuid} · progression level{" "}
              {agent.progression_level_reached}
            </p>
          </div>

          <div className="ml-auto hidden text-right sm:block">
            <div className="tnum text-4xl font-semibold text-paper">
              {prog.unlocked}
              <span className="text-lg text-muted">/{prog.total}</span>
            </div>
            <div className="font-display text-[0.6rem] uppercase tracking-[0.18em] text-muted">
              Tiers issued
            </div>
            {!prog.complete && (
              <div className="tnum mt-2 text-sm text-amber">
                {kc(remaining)} KC to finish
              </div>
            )}
          </div>
        </div>
      </header>

      {agent.discrepancies.length > 0 && (
        <div className="border border-oxide/50 bg-oxide/5 p-4">
          <div className="mb-2 flex items-center gap-3">
            <StatusStamp label="Discrepancy" tone="oxide" size="sm" rotate={-2} />
            <span className="font-display text-xs uppercase tracking-[0.14em] text-muted">
              Manifest notes — {agent.discrepancies.length}
            </span>
          </div>
          <ul className="space-y-1 text-sm text-paper/85">
            {agent.discrepancies.map((d, i) => (
              <li key={i} className="flex gap-2">
                <span className="text-oxide">›</span>
                {d}
              </li>
            ))}
          </ul>
        </div>
      )}

      <section className="border border-line bg-plate">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-sm uppercase tracking-[0.2em] text-muted">
            Requisition Track
          </h2>
          {next && (
            <span className="font-display text-[0.62rem] uppercase tracking-[0.14em] text-amber">
              Next authorization · tier {tierNo(next.index)}
            </span>
          )}
        </div>
        <ol>
          {agent.tiers.map((t) => (
            <TierRow
              key={t.index}
              tier={t}
              isNext={next?.index === t.index}
              rewardIndex={rewardIndex}
            />
          ))}
        </ol>
      </section>
    </div>
  );
}

export function AgentDetail() {
  const { agentName = "" } = useParams();
  const { data, isPending, isError, error, refetch, isFetching } = useSnapshot();

  if (isPending) return <LoadingScreen />;
  if (isError)
    return <ErrorScreen error={error} onRetry={() => refetch()} retrying={isFetching} />;

  const agent = data.agents.find(
    (a) => a.agent_name.toLowerCase() === agentName.toLowerCase(),
  );

  if (!agent) {
    return (
      <div className="space-y-6">
        <Link
          to="/"
          className="inline-flex items-center gap-2 font-display text-xs uppercase tracking-[0.16em] text-muted hover:text-paper"
        >
          ‹ Manifest
        </Link>
        <div className="border border-line bg-steel p-8 text-center">
          <StatusStamp label="No record" tone="muted" size="lg" rotate={-3} />
          <p className="mt-6 text-paper">
            No agent named “{agentName}” is on the current manifest.
          </p>
        </div>
      </div>
    );
  }

  return (
    <Detail
      agent={agent}
      agentStatic={data.agents_static[agent.agent_uuid]}
      rewardIndex={data.reward_index}
    />
  );
}
