/**
 * Kingdom Corporation quartermaster crest — an amber crown (Kingdom) over
 * paper-white rank chevrons (Quartermaster). Matches docs/logo.svg and the
 * amber `kqm --help` banner. See DESIGN_BRIEF.md.
 */
export function KingdomMark({ size = 32 }: { size?: number }) {
  return (
    <svg
      width={(size * 88) / 96}
      height={size}
      viewBox="0 0 88 96"
      fill="none"
      aria-hidden
    >
      {/* crest plate */}
      <path
        d="M44 5 L78 18 L78 47 L44 91 L10 47 L10 18 Z"
        stroke="var(--color-amber)"
        strokeWidth="2.6"
        fill="var(--color-amber)"
        fillOpacity="0.06"
        strokeLinejoin="round"
      />
      {/* crown — Kingdom */}
      <path
        d="M26 33 L34 23 L39 31 L44 21 L49 31 L54 23 L62 33"
        stroke="var(--color-amber)"
        strokeWidth="2.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <path d="M26 33 H62" stroke="var(--color-amber)" strokeWidth="2.6" strokeLinecap="round" />
      {/* rank chevrons — Quartermaster */}
      <path
        d="M28 48 L44 59 L60 48"
        stroke="var(--color-paper)"
        strokeWidth="2.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      <path
        d="M28 59 L44 70 L60 59"
        stroke="var(--color-paper)"
        strokeWidth="2.6"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}
