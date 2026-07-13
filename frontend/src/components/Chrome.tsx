import { type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { useSnapshot } from "../api/hooks";
import { ago, kc } from "../lib/format";
import { KC_CAP } from "../api/types";
import { KingdomMark } from "./KingdomMark";

const NAV = [
  { to: "/", label: "Manifest", end: true },
  { to: "/recommend", label: "Requisition", end: false },
];

function LiveDot({ mock }: { mock: boolean }) {
  return (
    <span className="inline-flex items-center gap-2 font-display text-[0.65rem] uppercase tracking-[0.18em] text-muted">
      <span
        className="inline-block h-2 w-2"
        style={{
          background: mock ? "var(--color-muted)" : "var(--color-issued)",
          boxShadow: mock ? "none" : "0 0 8px var(--color-issued)",
        }}
      />
      {mock ? "Mock line" : "Live line"}
    </span>
  );
}

export function Chrome({ children }: { children: ReactNode }) {
  const { data, isFetching, refetch } = useSnapshot();
  const queryClient = useQueryClient();
  const mock = data?.client_version === "mock";
  const balance = data?.balance;
  const nearCap = balance != null && balance >= 9000;

  const refetchAll = () => {
    // re-read the live line for every view
    queryClient.invalidateQueries();
    refetch();
  };

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-20 border-b border-line bg-ink/95 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3 sm:px-6">
          <NavLink to="/" className="flex items-center gap-3">
            <KingdomMark />
            <span className="leading-tight">
              <span className="block font-display text-sm font-bold uppercase tracking-[0.2em] text-paper">
                Kingdom
              </span>
              <span className="block font-display text-[0.6rem] uppercase tracking-[0.34em] text-amber">
                Quartermaster
              </span>
            </span>
          </NavLink>

          <nav className="ml-4 flex items-center gap-1">
            {NAV.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                end={n.end}
                className={({ isActive }) =>
                  [
                    "border px-3 py-1.5 font-display text-xs uppercase tracking-[0.16em] transition-colors",
                    isActive
                      ? "border-amber text-amber"
                      : "border-transparent text-muted hover:border-line hover:text-paper",
                  ].join(" ")
                }
              >
                {n.label}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-4">
            {balance != null && (
              <div className="hidden items-baseline gap-2 sm:flex">
                <span className="font-display text-[0.6rem] uppercase tracking-[0.2em] text-muted">
                  Budget
                </span>
                <span
                  className="tnum text-sm font-semibold"
                  style={{ color: nearCap ? "var(--color-oxide)" : "var(--color-amber)" }}
                >
                  {kc(balance)}
                </span>
                <span className="tnum text-xs text-muted">/ {kc(KC_CAP)}</span>
              </div>
            )}
            <LiveDot mock={mock} />
          </div>
        </div>

        {data && (
          <div className="border-t border-line/60 bg-steel/40">
            <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-1.5 sm:px-6">
              <span className="tnum text-[0.66rem] text-muted">
                Manifest read {ago(data.fetched_at)} · {mock ? "fixture data" : `shard ${data.shard.toUpperCase()}`}
              </span>
              <button
                type="button"
                onClick={refetchAll}
                disabled={isFetching}
                className="font-display text-[0.62rem] uppercase tracking-[0.16em] text-muted transition-colors hover:text-amber disabled:opacity-50"
              >
                {isFetching ? "Re-fetching…" : "↻ Re-fetch"}
              </button>
            </div>
          </div>
        )}
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6 sm:px-6 sm:py-8">{children}</main>

      <footer className="mx-auto max-w-6xl px-4 pb-10 pt-4 sm:px-6">
        <p className="border-t border-line pt-4 text-[0.7rem] leading-relaxed text-muted">
          Read-only requisition terminal · plans are drafts, never transactions ·
          not affiliated with Riot Games.
        </p>
      </footer>
    </div>
  );
}
