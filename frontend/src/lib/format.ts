/** Kingdom Credits — grouped, no decimals. */
export function kc(n: number): string {
  return n.toLocaleString("en-US", { maximumFractionDigits: 0 });
}

/** Zero-padded tier index, e.g. 3 -> "03". */
export function tierNo(n: number): string {
  return String(n).padStart(2, "0");
}

/** Human "time since" from an ISO timestamp, for the stale-data readout. */
export function ago(iso: string): string {
  const then = new Date(iso).getTime();
  if (Number.isNaN(then)) return "unknown";
  const secs = Math.max(0, Math.floor((Date.now() - then) / 1000));
  if (secs < 45) return "just now";
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins} min ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs} hr ago`;
  const days = Math.floor(hrs / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}
