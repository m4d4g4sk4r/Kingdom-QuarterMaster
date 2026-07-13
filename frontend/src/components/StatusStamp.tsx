import type { CSSProperties } from "react";

export type StampTone = "amber" | "issued" | "oxide" | "muted";

const TONE: Record<StampTone, string> = {
  amber: "var(--color-amber)",
  issued: "var(--color-issued)",
  oxide: "var(--color-oxide)",
  muted: "var(--color-muted)",
};

/**
 * The signature element: a rubber-stamp status mark. Angular hairline box,
 * uppercase Chakra Petch, tracked, faintly rotated and ink-set on mount.
 * See DESIGN_BRIEF.md.
 */
export function StatusStamp({
  label,
  tone = "muted",
  rotate = -2,
  size = "md",
  animate = true,
  title,
}: {
  label: string;
  tone?: StampTone;
  rotate?: number;
  size?: "sm" | "md" | "lg";
  animate?: boolean;
  title?: string;
}) {
  const color = TONE[tone];
  const pad =
    size === "lg"
      ? "0.34rem 0.7rem"
      : size === "sm"
        ? "0.12rem 0.4rem"
        : "0.22rem 0.55rem";
  const font = size === "lg" ? "0.9rem" : size === "sm" ? "0.62rem" : "0.72rem";

  const style: CSSProperties = {
    color,
    borderColor: color,
    padding: pad,
    fontSize: font,
    // token consumed by the stamp-set keyframe
    ["--stamp-rot" as string]: `${rotate}deg`,
    transform: `rotate(${rotate}deg)`,
    boxShadow: `inset 0 0 0 1px ${color}22`,
    background: `${color}0f`,
    animation: animate ? "stamp-set 320ms cubic-bezier(0.2,0.8,0.2,1) both" : undefined,
  };

  return (
    <span
      title={title}
      style={style}
      className="inline-flex select-none items-center border font-display font-bold uppercase leading-none tracking-[0.16em]"
    >
      {label}
    </span>
  );
}
