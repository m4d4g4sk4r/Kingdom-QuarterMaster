import type { RewardKind } from "../api/types";

/**
 * Minimal line glyphs per reward kind — used when reward_index has no icon
 * (skins, currency, all of mock mode). Institutional, single-stroke, currentColor.
 */
export function KindGlyph({
  kind,
  size = 18,
}: {
  kind: RewardKind;
  size?: number;
}) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.6,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };

  switch (kind) {
    case "spray":
      return (
        <svg {...common}>
          <path d="M9 3h3v4H9z" />
          <path d="M12 5h3M12 3h2" />
          <rect x="7" y="7" width="7" height="14" rx="1" />
          <path d="M9 11h3" />
        </svg>
      );
    case "playercard":
      return (
        <svg {...common}>
          <rect x="3" y="5" width="18" height="14" rx="1" />
          <path d="M7 9h4v6H7zM14 9h4M14 12h4M14 15h2" />
        </svg>
      );
    case "title":
      return (
        <svg {...common}>
          <path d="M4 7h16M8 7v10M12 7v10M16 7v10M6 17h4M14 17h4" />
        </svg>
      );
    case "buddy":
      return (
        <svg {...common}>
          <circle cx="9" cy="9" r="4" />
          <path d="M9 13v4M7 20h4M12 6l7-3M17 4l3 1-1 3" />
        </svg>
      );
    case "skin":
      return (
        <svg {...common}>
          <path d="M3 14h11l5-5-2-2-9 9M3 14v4h4M6 14l3 3" />
        </svg>
      );
    case "currency":
      return (
        <svg {...common}>
          <circle cx="12" cy="12" r="8" />
          <path d="M9 15h4.5a2 2 0 0 0 0-4H10a2 2 0 0 1 0-4h4" />
        </svg>
      );
    default:
      return (
        <svg {...common}>
          <rect x="4" y="4" width="16" height="16" rx="1" />
          <path d="M8 8h8v8H8z" />
        </svg>
      );
  }
}
