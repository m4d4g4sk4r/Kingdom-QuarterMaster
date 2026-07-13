import { useMemo, useState } from "react";
import { useSnapshot } from "../api/hooks";
import { AuthorizationGauge } from "../components/AuthorizationGauge";
import { AgentCard } from "../components/AgentCard";
import { ErrorScreen, LoadingScreen } from "../components/StateScreen";
import { progress, remainingCost } from "../lib/agent";
import type { AgentGearStatus } from "../api/types";

type SortKey = "closest" | "value";
type FilterKey = "all" | "unrecruited";

const SORTS: { key: SortKey; label: string }[] = [
  { key: "closest", label: "Closest to done" },
  { key: "value", label: "Most locked value" },
];

const FILTERS: { key: FilterKey; label: string }[] = [
  { key: "all", label: "All agents" },
  { key: "unrecruited", label: "Not recruited" },
];

function arrangeAgents(
  agents: AgentGearStatus[],
  sort: SortKey,
  filter: FilterKey,
): AgentGearStatus[] {
  const filtered =
    filter === "unrecruited" ? agents.filter((a) => !a.recruited) : agents;
  const copy = [...filtered];
  switch (sort) {
    case "closest":
      return copy.sort((a, b) => {
        const pa = progress(a);
        const pb = progress(b);
        // complete last, otherwise highest fraction first
        if (pa.complete !== pb.complete) return pa.complete ? 1 : -1;
        return pb.fraction - pa.fraction;
      });
    case "value":
      return copy.sort((a, b) => remainingCost(b) - remainingCost(a));
  }
}

export function Dashboard() {
  const { data, isPending, isError, error, refetch, isFetching } = useSnapshot();
  const [sort, setSort] = useState<SortKey>("closest");
  const [filter, setFilter] = useState<FilterKey>("all");

  const agents = useMemo(
    () => (data ? arrangeAgents(data.agents, sort, filter) : []),
    [data, sort, filter],
  );

  if (isPending) return <LoadingScreen />;
  if (isError)
    return <ErrorScreen error={error} onRetry={() => refetch()} retrying={isFetching} />;

  const totalLocked = data.agents.reduce((s, a) => s + remainingCost(a), 0);
  const outfitted = data.agents.filter((a) => progress(a).complete).length;

  return (
    <div className="space-y-8">
      <AuthorizationGauge balance={data.balance} />

      {/* manifest summary strip */}
      <div className="grid grid-cols-2 gap-px border border-line bg-line sm:grid-cols-4">
        {[
          { label: "Agents on file", value: String(data.agents.length) },
          { label: "Fully outfitted", value: `${outfitted}/${data.agents.length}` },
          { label: "Locked value", value: `${totalLocked.toLocaleString()} KC` },
          { label: "Region", value: data.shard.toUpperCase() },
        ].map((s) => (
          <div key={s.label} className="bg-steel px-4 py-3">
            <div className="font-display text-[0.6rem] uppercase tracking-[0.18em] text-muted">
              {s.label}
            </div>
            <div className="tnum mt-1 text-lg text-paper">{s.value}</div>
          </div>
        ))}
      </div>

      <section>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-x-6 gap-y-3">
          <h2 className="text-sm uppercase tracking-[0.22em] text-muted">
            Agent Manifest
            <span className="tnum ml-3 text-paper/60">
              {agents.length}
              {filter !== "all" && (
                <span className="text-muted"> of {data.agents.length}</span>
              )}
            </span>
          </h2>

          <div className="flex flex-wrap items-center gap-x-5 gap-y-2">
            <div className="flex items-center gap-2">
              <span className="font-display text-[0.58rem] uppercase tracking-[0.16em] text-muted">
                Show
              </span>
              <div className="flex gap-1">
                {FILTERS.map((f) => (
                  <button
                    key={f.key}
                    type="button"
                    onClick={() => setFilter(f.key)}
                    className={[
                      "border px-3 py-1.5 font-display text-[0.68rem] uppercase tracking-[0.12em] transition-colors",
                      filter === f.key
                        ? "border-amber text-amber"
                        : "border-line text-muted hover:text-paper",
                    ].join(" ")}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="font-display text-[0.58rem] uppercase tracking-[0.16em] text-muted">
                Sort
              </span>
              <div className="flex gap-1">
                {SORTS.map((s) => (
                  <button
                    key={s.key}
                    type="button"
                    onClick={() => setSort(s.key)}
                    className={[
                      "border px-3 py-1.5 font-display text-[0.68rem] uppercase tracking-[0.12em] transition-colors",
                      sort === s.key
                        ? "border-amber text-amber"
                        : "border-line text-muted hover:text-paper",
                    ].join(" ")}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {agents.length === 0 ? (
          <div className="border border-dashed border-line bg-steel/50 p-10 text-center text-sm text-muted">
            Every agent on file is recruited — no outstanding recruitments.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {agents.map((a) => (
              <AgentCard
                key={a.agent_uuid}
                agent={a}
                agentStatic={data.agents_static[a.agent_uuid]}
              />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
