import { KC_CAP } from "../api/types";
import { kc } from "../lib/format";

const NEAR_CAP = 9000; // hazard zone begins here

/**
 * The dashboard hero: KC operating budget as a segmented authorization meter
 * toward the 10,000 ceiling, with a hard oxide hazard band near the cap so
 * "credits past the ceiling are forfeit" is impossible to miss.
 */
export function AuthorizationGauge({ balance }: { balance: number }) {
  const clamped = Math.max(0, Math.min(balance, KC_CAP));
  const fraction = clamped / KC_CAP;
  const nearCap = balance >= NEAR_CAP;
  const over = balance > KC_CAP;
  const segments = 40;
  const litExact = fraction * segments;
  const hazardStart = Math.round((NEAR_CAP / KC_CAP) * segments);

  const fillColor = nearCap ? "var(--color-oxide)" : "var(--color-amber)";

  return (
    <section
      aria-label="Kingdom Credits authorization"
      className="border border-line bg-steel p-5 sm:p-6"
    >
      <div className="flex items-baseline justify-between gap-4">
        <span className="font-display text-xs uppercase tracking-[0.22em] text-muted">
          Operating Budget · Authorization
        </span>
        <span className="font-display text-xs uppercase tracking-[0.18em] text-muted">
          Ceiling {kc(KC_CAP)}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap items-end gap-x-6 gap-y-2">
        <div className="tnum leading-none">
          <span
            className="text-5xl font-semibold sm:text-6xl"
            style={{ color: fillColor }}
          >
            {kc(clamped)}
          </span>
          <span className="ml-2 text-lg text-muted">/ {kc(KC_CAP)} KC</span>
        </div>
      </div>

      {/* segmented meter */}
      <div
        className="mt-5 flex h-8 gap-[3px]"
        role="meter"
        aria-valuemin={0}
        aria-valuemax={KC_CAP}
        aria-valuenow={clamped}
      >
        {Array.from({ length: segments }, (_, i) => {
          const lit = i < Math.floor(litExact);
          const partial = !lit && i < litExact;
          const inHazard = i >= hazardStart;
          const base = inHazard ? "var(--color-oxide)" : fillColor;
          return (
            <span
              key={i}
              className="flex-1 transition-[opacity,background-color] duration-300"
              style={{
                background: lit || partial ? base : "var(--color-plate)",
                opacity: lit ? 1 : partial ? 0.55 : inHazard ? 0.28 : 0.5,
                outline: inHazard ? "1px solid var(--color-oxide)" : "none",
                outlineOffset: "-1px",
              }}
            />
          );
        })}
      </div>

      <div className="mt-3 min-h-5">
        {nearCap ? (
          <p className="font-display text-xs uppercase tracking-[0.14em] text-oxide">
            {over ? "Over ceiling — " : "Authorization near ceiling — "}
            credits earned past {kc(KC_CAP)} KC are forfeit
          </p>
        ) : (
          <p className="text-xs text-muted">
            Requisition credits drawn against this budget.
          </p>
        )}
      </div>
    </section>
  );
}
