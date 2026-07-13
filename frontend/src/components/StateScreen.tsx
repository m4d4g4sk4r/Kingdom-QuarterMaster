import { ApiError, type ApiErrorCode } from "../api/types";
import { StatusStamp, type StampTone } from "./StatusStamp";

interface StateCopy {
  stamp: string;
  tone: StampTone;
  title: string;
  body: string;
  hint?: string;
}

const COPY: Record<ApiErrorCode, StateCopy> = {
  lockfile_not_found: {
    stamp: "Terminal offline",
    tone: "oxide",
    title: "The requisition line is down",
    body: "The Riot Client isn't running, so there's nothing to read.",
    hint: "Start VALORANT (or the Riot Client) on this machine, then re-fetch.",
  },
  local_api_unavailable: {
    stamp: "Terminal offline",
    tone: "oxide",
    title: "Can't reach the local client",
    body: "The Riot Client is present but isn't answering its local port yet.",
    hint: "Give it a moment after launch, then re-fetch.",
  },
  network_error: {
    stamp: "Line severed",
    tone: "oxide",
    title: "Can't reach the requisition server",
    body: "The local Kingdom Quartermaster server isn't responding.",
    hint: "Make sure `kqm ui` is still running, then re-fetch.",
  },
  shard_detection_failed: {
    stamp: "Region unknown",
    tone: "oxide",
    title: "Couldn't determine your region",
    body: "The shard/region couldn't be detected automatically.",
    hint: "Start the app with an explicit region, e.g. `kqm --shard na ui`.",
  },
  schema_drift: {
    stamp: "Format changed",
    tone: "oxide",
    title: "The manifest format changed",
    body: "Riot altered the API after a patch; some readings can't be parsed.",
    hint: "This usually needs a tool update. Try `--refresh-static`, then re-fetch.",
  },
  riot_api_error: {
    stamp: "Upstream fault",
    tone: "oxide",
    title: "Riot's servers returned an error",
    body: "The player-data endpoint responded with a fault.",
    hint: "Usually transient — re-fetch in a moment.",
  },
  static_data_error: {
    stamp: "Catalog fault",
    tone: "oxide",
    title: "Couldn't load the gear catalog",
    body: "Static game data (names, icons, costs) failed to load.",
    hint: "Check your connection, then re-fetch. `--refresh-static` forces a reload.",
  },
  agent_not_found: {
    stamp: "No record",
    tone: "muted",
    title: "No such agent on file",
    body: "That agent isn't in the current manifest.",
  },
  unknown: {
    stamp: "Fault",
    tone: "oxide",
    title: "Something went wrong",
    body: "An unexpected error occurred while reading the manifest.",
    hint: "Re-fetch, or restart `kqm ui`.",
  },
};

export function LoadingScreen({ label = "Reading manifest…" }: { label?: string }) {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-5 text-center">
      <div className="flex gap-[3px]" aria-hidden>
        {Array.from({ length: 5 }, (_, i) => (
          <span
            key={i}
            className="h-6 w-1.5 bg-amber"
            style={{
              opacity: 0.3,
              animation: `stamp-set 900ms ${i * 120}ms ease-in-out infinite alternate`,
            }}
          />
        ))}
      </div>
      <p className="font-display text-sm uppercase tracking-[0.22em] text-muted">
        {label}
      </p>
    </div>
  );
}

export function ErrorScreen({
  error,
  onRetry,
  retrying,
}: {
  error: unknown;
  onRetry?: () => void;
  retrying?: boolean;
}) {
  const code: ApiErrorCode =
    error instanceof ApiError ? error.code : "unknown";
  const copy = COPY[code] ?? COPY.unknown;
  const detail = error instanceof Error ? error.message : String(error);

  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="w-full max-w-lg border border-line bg-steel p-8">
        <StatusStamp label={copy.stamp} tone={copy.tone} size="lg" rotate={-3} />
        <h1 className="mt-6 text-2xl text-paper">{copy.title}</h1>
        <p className="mt-3 text-sm leading-relaxed text-paper/80">{copy.body}</p>
        {copy.hint && (
          <p className="mt-4 border-l-2 border-amber pl-3 text-sm leading-relaxed text-muted">
            {copy.hint}
          </p>
        )}
        <p className="tnum mt-6 border-t border-line pt-3 text-xs text-muted">
          {code} · {detail}
        </p>
        {onRetry && (
          <button
            type="button"
            onClick={onRetry}
            disabled={retrying}
            className="mt-6 border border-amber px-4 py-2 font-display text-xs uppercase tracking-[0.18em] text-amber transition-colors hover:bg-amber hover:text-ink disabled:opacity-50"
          >
            {retrying ? "Re-fetching…" : "Re-fetch"}
          </button>
        )}
      </div>
    </div>
  );
}
