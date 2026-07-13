/**
 * Interim Kingdom Corporation monogram — an angular quartermaster's stamp.
 * Phase 3 replaces this with the finished logo asset.
 */
export function KingdomMark({ size = 30 }: { size?: number }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden
    >
      {/* beveled shield plate */}
      <path
        d="M4 4h24v16l-12 8L4 20z"
        stroke="var(--color-amber)"
        strokeWidth="1.6"
      />
      {/* chevrons — quartermaster rank */}
      <path
        d="M10 12l6 4 6-4M10 16l6 4 6-4"
        stroke="var(--color-paper)"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  );
}
