import { useMemo, useState } from "react";
import { useGoal, useRecommend, useSnapshot } from "../api/hooks";
import { ErrorScreen, LoadingScreen } from "../components/StateScreen";
import { StatusStamp } from "../components/StatusStamp";
import { KindGlyph } from "../components/KindGlyph";
import { useDebounced } from "../lib/useDebounced";
import { kc, tierNo } from "../lib/format";
import { kindLabel } from "../lib/reward";
import { WEIGHTED_KINDS, type PlannedPurchase } from "../api/types";

const DEFAULT_WEIGHTS: Record<string, number> = {
  buddy: 5,
  playercard: 4,
  skin: 3,
  title: 2,
  spray: 1,
};

type Mode = "value" | "goal";

function PurchaseRow({
  purchase,
  runningBalance,
  affordable,
}: {
  purchase: PlannedPurchase;
  runningBalance: number;
  affordable: boolean;
}) {
  return (
    <li
      className="flex items-center gap-3 border-b border-line px-4 py-3 last:border-b-0"
      style={affordable ? undefined : { opacity: 0.5 }}
    >
      <span
        className="shrink-0 text-muted"
        style={{ color: affordable ? "var(--color-amber)" : "var(--color-muted)" }}
      >
        <KindGlyph kind={purchase.reward_kind} />
      </span>
      <div className="min-w-0 flex-1">
        <div className="truncate text-sm text-paper">
          {purchase.agent_name}
          <span className="text-muted"> · {kindLabel(purchase.reward_kind)}</span>
        </div>
        <div className="tnum font-display text-[0.62rem] uppercase tracking-[0.14em] text-muted">
          Tier {tierNo(purchase.tier_index)} · weight {purchase.weight}
        </div>
      </div>
      <span className="tnum w-24 shrink-0 text-right text-sm text-paper">
        {kc(purchase.cost_kc)} <span className="text-muted">KC</span>
      </span>
      <span className="tnum hidden w-32 shrink-0 text-right text-xs text-muted sm:block">
        {affordable ? `balance → ${kc(runningBalance)}` : "—"}
      </span>
    </li>
  );
}

function WeightSliders({
  weights,
  onChange,
}: {
  weights: Record<string, number>;
  onChange: (kind: string, value: number) => void;
}) {
  return (
    <div className="border border-line bg-steel p-4">
      <div className="mb-3 font-display text-xs uppercase tracking-[0.18em] text-muted">
        Priority weights
      </div>
      <div className="grid grid-cols-1 gap-x-6 gap-y-3 sm:grid-cols-2 lg:grid-cols-3">
        {WEIGHTED_KINDS.map((kind) => (
          <label key={kind} className="flex items-center gap-3">
            <span className="w-24 shrink-0 text-xs text-paper">{kindLabel(kind)}</span>
            <input
              type="range"
              min={0}
              max={10}
              step={1}
              value={weights[kind] ?? 0}
              onChange={(e) => onChange(kind, Number(e.target.value))}
              className="h-1 flex-1 cursor-pointer appearance-none bg-line accent-amber"
              aria-label={`${kindLabel(kind)} weight`}
            />
            <span className="tnum w-5 text-right text-sm text-amber">
              {weights[kind] ?? 0}
            </span>
          </label>
        ))}
      </div>
    </div>
  );
}

function ValuePlan({ weights }: { weights: Record<string, number> }) {
  const { data, isPending, isError, error, refetch, isFetching } =
    useRecommend(weights);

  if (isPending) return <LoadingScreen label="Drafting requisition…" />;
  if (isError)
    return <ErrorScreen error={error} onRetry={() => refetch()} retrying={isFetching} />;

  const { plan, balance } = data;

  if (plan.purchases.length === 0) {
    return (
      <div className="border border-line bg-steel p-8 text-center">
        <StatusStamp label="Nothing to draft" tone="muted" size="lg" rotate={-2} />
        <p className="mt-6 text-paper">
          No affordable requisitions at the current budget and weights.
        </p>
      </div>
    );
  }

  let running = balance;
  const rows = plan.purchases.map((p) => {
    running -= p.cost_kc;
    return { p, running };
  });

  return (
    <div className="space-y-4">
      <section className="border border-line bg-plate">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-sm uppercase tracking-[0.2em] text-muted">
            Draft Requisition · Best Value
          </h2>
          {isFetching && (
            <span className="font-display text-[0.6rem] uppercase tracking-[0.16em] text-muted">
              Recomputing…
            </span>
          )}
        </div>
        <ol>
          {rows.map(({ p, running: r }) => (
            <PurchaseRow
              key={`${p.agent_name}-${p.tier_index}`}
              purchase={p}
              runningBalance={r}
              affordable
            />
          ))}
        </ol>
      </section>

      <PlanFooter
        totalCost={plan.total_cost}
        leftover={plan.leftover_kc}
        nearCap={plan.near_cap_warning}
      />
    </div>
  );
}

function PlanFooter({
  totalCost,
  leftover,
  nearCap,
}: {
  totalCost: number;
  leftover: number;
  nearCap: boolean;
}) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-4 border border-line bg-steel px-4 py-3">
      <div className="flex gap-8">
        <div>
          <div className="font-display text-[0.6rem] uppercase tracking-[0.16em] text-muted">
            Total draft
          </div>
          <div className="tnum text-lg text-paper">{kc(totalCost)} KC</div>
        </div>
        <div>
          <div className="font-display text-[0.6rem] uppercase tracking-[0.16em] text-muted">
            Leftover
          </div>
          <div className="tnum text-lg text-paper">{kc(leftover)} KC</div>
        </div>
      </div>
      {nearCap && (
        <StatusStamp label="Near ceiling" tone="oxide" rotate={-2} />
      )}
    </div>
  );
}

function GoalPlanView({
  agentName,
  weights,
}: {
  agentName: string;
  weights: Record<string, number>;
}) {
  const { data, isPending, isError, error, refetch, isFetching } = useGoal(
    agentName,
    weights,
  );

  if (isPending) return <LoadingScreen label="Costing full unlock…" />;
  if (isError)
    return <ErrorScreen error={error} onRetry={() => refetch()} retrying={isFetching} />;

  const { plan, balance } = data;
  const affordableKeys = new Set(
    plan.affordable_purchases.map((p) => `${p.agent_name}-${p.tier_index}`),
  );

  let running = balance - plan.recruit_cost;
  const rows = plan.purchases.map((p) => {
    const affordable = affordableKeys.has(`${p.agent_name}-${p.tier_index}`);
    if (affordable) running -= p.cost_kc;
    return { p, affordable, running };
  });

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-px border border-line bg-line sm:grid-cols-4">
        {[
          { label: "Total to finish", value: `${kc(plan.total_cost)} KC` },
          { label: "Affordable now", value: `${kc(plan.affordable_cost)} KC` },
          {
            label: "Shortfall",
            value: plan.fully_affordable ? "None" : `${kc(plan.remaining_needed)} KC`,
          },
          {
            label: "Recruit",
            value: plan.needs_recruit ? `${kc(plan.recruit_cost)} KC` : "Done",
          },
        ].map((s) => (
          <div key={s.label} className="bg-steel px-4 py-3">
            <div className="font-display text-[0.6rem] uppercase tracking-[0.16em] text-muted">
              {s.label}
            </div>
            <div className="tnum mt-1 text-base text-paper">{s.value}</div>
          </div>
        ))}
      </div>

      {plan.fully_affordable ? (
        <div className="flex items-center gap-3 border border-issued/40 bg-issued/5 px-4 py-3">
          <StatusStamp label="Fully affordable" tone="issued" rotate={-2} />
          <span className="text-sm text-paper/85">
            The whole contract fits inside the current budget.
          </span>
        </div>
      ) : (
        <div className="flex items-center gap-3 border border-amber/40 bg-amber/5 px-4 py-3">
          <StatusStamp label="Partial" tone="amber" rotate={2} />
          <span className="text-sm text-paper/85">
            Draft covers the affordable prefix; {kc(plan.remaining_needed)} KC more
            needed to finish.
          </span>
        </div>
      )}

      <section className="border border-line bg-plate">
        <div className="flex items-center justify-between border-b border-line px-4 py-3">
          <h2 className="text-sm uppercase tracking-[0.2em] text-muted">
            Full Unlock · {plan.agent_name}
          </h2>
          {plan.needs_recruit && (
            <span className="font-display text-[0.6rem] uppercase tracking-[0.16em] text-amber">
              Recruit first · {kc(plan.recruit_cost)} KC
            </span>
          )}
        </div>
        <ol>
          {rows.map(({ p, affordable, running: r }) => (
            <PurchaseRow
              key={`${p.agent_name}-${p.tier_index}`}
              purchase={p}
              runningBalance={r}
              affordable={affordable}
            />
          ))}
        </ol>
      </section>
    </div>
  );
}

export function Recommend() {
  const snapshot = useSnapshot();
  const [mode, setMode] = useState<Mode>("value");
  const [weights, setWeights] = useState<Record<string, number>>(DEFAULT_WEIGHTS);
  const [goalAgent, setGoalAgent] = useState<string>("");
  const debouncedWeights = useDebounced(weights, 250);

  const agentNames = useMemo(
    () => (snapshot.data ? snapshot.data.agents.map((a) => a.agent_name) : []),
    [snapshot.data],
  );

  if (snapshot.isPending) return <LoadingScreen />;
  if (snapshot.isError)
    return (
      <ErrorScreen
        error={snapshot.error}
        onRetry={() => snapshot.refetch()}
        retrying={snapshot.isFetching}
      />
    );

  const setWeight = (kind: string, value: number) =>
    setWeights((w) => ({ ...w, [kind]: value }));

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-sm uppercase tracking-[0.22em] text-muted">
          Requisition Planning
        </h1>
        <div className="flex gap-1">
          {(["value", "goal"] as Mode[]).map((m) => (
            <button
              key={m}
              type="button"
              onClick={() => setMode(m)}
              className={[
                "border px-3 py-1.5 font-display text-[0.68rem] uppercase tracking-[0.12em] transition-colors",
                mode === m
                  ? "border-amber text-amber"
                  : "border-line text-muted hover:text-paper",
              ].join(" ")}
            >
              {m === "value" ? "Best value" : "Goal · one agent"}
            </button>
          ))}
        </div>
      </div>

      <WeightSliders weights={weights} onChange={setWeight} />

      {mode === "value" ? (
        <ValuePlan weights={debouncedWeights} />
      ) : (
        <div className="space-y-4">
          <label className="flex flex-wrap items-center gap-3">
            <span className="font-display text-xs uppercase tracking-[0.16em] text-muted">
              Target agent
            </span>
            <select
              value={goalAgent}
              onChange={(e) => setGoalAgent(e.target.value)}
              className="border border-line bg-plate px-3 py-2 text-sm text-paper focus-visible:border-amber"
            >
              <option value="">Select an agent…</option>
              {agentNames.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
          </label>

          {goalAgent ? (
            <GoalPlanView agentName={goalAgent} weights={debouncedWeights} />
          ) : (
            <div className="border border-dashed border-line bg-steel/50 p-8 text-center text-sm text-muted">
              Pick an agent to draft a full-unlock requisition.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
