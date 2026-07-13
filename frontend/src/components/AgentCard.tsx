import { Link } from "react-router-dom";
import type { AgentGearStatus, AgentStatic } from "../api/types";
import { agentAccent, nextTier, progress, remainingCost } from "../lib/agent";
import { kc } from "../lib/format";
import { StatusStamp } from "./StatusStamp";

export function AgentCard({
  agent,
  agentStatic,
}: {
  agent: AgentGearStatus;
  agentStatic?: AgentStatic;
}) {
  const accent = agentAccent(agentStatic) ?? "var(--color-line)";
  const portrait = agentStatic?.fullPortrait ?? agentStatic?.displayIcon;
  const prog = progress(agent);
  const next = nextTier(agent);
  const remaining = remainingCost(agent);

  return (
    <Link
      to={`/agent/${encodeURIComponent(agent.agent_name)}`}
      className="group relative flex flex-col overflow-hidden border border-line bg-plate transition-colors hover:border-muted focus-visible:border-amber"
    >
      {/* left-edge manifest stripe — the agent's identity color */}
      <span
        aria-hidden
        className="absolute left-0 top-0 h-full w-1"
        style={{ background: accent }}
      />

      <div className="flex items-start justify-between gap-2 p-4 pl-5">
        <div>
          <h3 className="text-lg text-paper">{agent.agent_name}</h3>
          <p className="tnum mt-0.5 text-xs text-muted">
            Contract {agent.contract_uuid.slice(0, 8)}
          </p>
        </div>
        {!agent.recruited ? (
          <StatusStamp label="Not recruited" tone="amber" rotate={2} size="sm" />
        ) : prog.complete ? (
          <StatusStamp label="In stock" tone="issued" rotate={-2} size="sm" />
        ) : (
          <span className="tnum font-display text-sm text-paper">
            {prog.unlocked}
            <span className="text-muted">/{prog.total}</span>
          </span>
        )}
      </div>

      {/* portrait band with clipped gradient wash */}
      <div className="relative mx-5 mb-4 h-28 overflow-hidden border border-line bg-ink">
        <span
          aria-hidden
          className="absolute inset-0 opacity-40"
          style={{ background: `linear-gradient(120deg, ${accent}, transparent 70%)` }}
        />
        {portrait ? (
          <img
            src={portrait}
            alt=""
            loading="lazy"
            className="absolute -right-4 bottom-0 h-32 w-auto object-contain opacity-90 transition-transform duration-300 group-hover:scale-105"
          />
        ) : null}
      </div>

      {/* progress rail */}
      <div className="mt-auto px-5 pb-4">
        <div className="flex h-1.5 overflow-hidden bg-ink" aria-hidden>
          <span
            className="h-full transition-[width] duration-500"
            style={{
              width: `${prog.fraction * 100}%`,
              background: prog.complete ? "var(--color-issued)" : accent,
            }}
          />
        </div>
        <div className="mt-3 flex items-baseline justify-between">
          {prog.complete ? (
            <span className="font-display text-xs uppercase tracking-[0.14em] text-issued">
              Fully outfitted
            </span>
          ) : next ? (
            <>
              <span className="font-display text-xs uppercase tracking-[0.12em] text-muted">
                {agent.recruited ? "Next tier" : "To recruit + finish"}
              </span>
              <span className="tnum text-sm text-paper">
                {kc(agent.recruited ? next.cost_kc : remaining)}{" "}
                <span className="text-muted">KC</span>
              </span>
            </>
          ) : null}
        </div>
        {agent.recruited && !prog.complete && (
          <p className="tnum mt-1 text-right text-xs text-muted">
            {kc(remaining)} KC to finish
          </p>
        )}
      </div>
    </Link>
  );
}
