# Kingdom Quartermaster — Design Brief

> This document records the aesthetic direction chosen via the **frontend-design**
> skill, committed before any UI code per the project prompt's hard gate. Every
> color and type decision in `frontend/` derives from this brief. If the build
> deviates, this file is updated and the reason noted in the commit message.

## Subject, audience, job (pinned)

- **Subject:** an in-world **Kingdom Corporation gear-issuance depot**. The user is
  the quartermaster. Agents are line items in the supply ledger; Kingdom Credits
  (KC) are the operating budget; locked contract tiers are *pending requisitions*;
  owned/unlocked gear is *issued / in stock*.
- **Audience:** a single VALORANT player running this locally on their own machine.
- **The page's single job:** decide **what to authorize next** with the KC on hand —
  and see how close each agent is to being fully outfitted.

This is a strictly read-only planning tool. Nothing here buys, activates, or
modifies anything. That constraint is expressed in the *language* of the design:
plans are **draft requisitions**, not transactions. No control anywhere reads as
"Buy", not even a disabled one.

## The thesis (and the one deliberate risk)

**The terminal chrome is disciplined institutional greyscale — color enters the
room only where an agent does.**

VALORANT ships a vivid per-agent gradient (`backgroundGradientColors`). If the
chrome is also loud, the two fight and the result is generic "dark gaming UI".
So the entire shell — panels, rules, type, gauges, stamps — is a restrained
gunmetal-and-manifest greyscale, and the **agent gradients are the only saturated
color in the product**. They appear as a thin left-edge *manifest stripe* on cards
and a clipped *header wash* on the agent detail view — identity, never fill.

The risk: committing hard to the in-world "corporate supply depot" fiction —
rubber-stamp status marks, requisition/ledger vernacular, monospace manifest
figures. Executed sloppily this reads as costume. The discipline (greyscale chrome,
tabular data alignment, real restraint) is what keeps it a serious instrument. The
risk is justified because the fiction is exactly what the brief asked for, and it
turns a plain data table into a coherent product with a point of view.

### Why this is not one of the AI defaults

The current AI-design clusters are (1) cream + high-contrast serif + terracotta,
(2) near-black + a single acid-green/vermilion accent, (3) broadsheet hairlines +
serif columns. This is a dark UI, so default (2) is the trap. It is avoided by:
the base is oxidized-steel graphite, **not** near-black; the accent is
**authorization-amber**, not acid-green/vermilion; there is a full *domain* status
taxonomy (issued-green / pending-grey / overdraw-oxide) plus the per-agent
gradients — not one lonely accent; and the signature (rubber-stamp marks +
mono-ledger manifest, IBM Plex + Chakra Petch) belongs to no default.

## Color system

Named tokens (implemented as CSS variables). Hex is base; some carry alpha in use.

| Token | Hex | Role |
|---|---|---|
| `--kq-ink` | `#0C0F11` | app background — cold oxidized-steel graphite, deliberately *not* pure black |
| `--kq-steel` | `#151A1D` | raised panel / rail surface |
| `--kq-plate` | `#1E252A` | cards, the next surface up |
| `--kq-line` | `#2A343A` | hairline rules, borders (1px, angular) |
| `--kq-paper` | `#E8E4D9` | primary text — warm manifest-paper white on cold steel (the core tension) |
| `--kq-muted` | `#8A9499` | secondary text, captions, inactive |
| `--kq-amber` | `#E6A23C` | the single chrome accent: authorization / the actionable next tier / key figures. Used with restraint. |
| `--kq-issued` | `#6FA06A` | status: issued / in stock (muted institutional green, never acid) |
| `--kq-oxide` | `#C4553D` | status: overdrawn / near-cap hazard / danger (brick-oxide red, never pure red) |

**Agent color** is not in this table on purpose: it comes at runtime from each
agent's `backgroundGradientColors` (8-digit `rrggbbaa` strings, e.g. Gekko
`371c5cff … 0f192300`). Rule of use: darken/clip it to a left-edge stripe and a
low-opacity top wash; never let it fill a surface or set text color.

## Typography

Three roles, self-hosted via `@fontsource/*` (no runtime CDN):

- **Display / stamped headers — Chakra Petch.** Angular, beveled, military-hardware
  character. View titles, agent names, section eyebrows, stamp labels. Used with
  restraint; it is the "voice of the terminal".
- **Body / UI — IBM Plex Sans.** The corporate voice of "Kingdom Corporation"
  (a typeface literally engineered for a corporation). Labels, prose, controls.
- **Data / ledger — IBM Plex Mono.** *Every* numeric figure: KC balances, costs,
  tier indices, timestamps, codes. Tabular figures make cost columns align like a
  real invoice and reinforce the manifest fiction.

Type scale is deliberate and tight; weights carry hierarchy (Chakra Petch 600/700
for stamps and titles, Plex Sans 400/500 for body, Plex Mono 500 for figures).
Uppercase + wide tracking is reserved for stamps and eyebrows, not body text.

## Layout principles

- Angular: `border-radius: 0` (or near-zero); structure drawn with 1px `--kq-line`
  hairlines, not shadows or rounded cards.
- A persistent terminal chrome: a top manifest bar with the Kingdom mark, the live
  KC authorization readout, a live/mock indicator, and nav between the three views.
- Content is a **manifest/ledger**: dense but disciplined, tabular alignment,
  mono figures right-aligned.
- Structural devices must encode truth, not decorate. Tier indices `01…10` are a
  *real ordered sequence* (tiers unlock sequentially), so a numbered vertical
  track is honest here — the numbering carries information the reader needs.

## Signature element

**The rubber-stamp status mark.** Requisition forms get stamped; so does every
status in this app: `ISSUED`, `IN STOCK`, `PENDING REQ.`, `OVERDRAWN`,
`NOT RECRUITED`, `AUTHORIZE`. Slightly angled, uppercase Chakra Petch, hairline
box, colored from the status taxonomy (amber/green/oxide/muted). This is the one
memorable, repeated device; everything around it stays quiet.

**Supporting hero device (Dashboard):** the **KC authorization gauge** — a
segmented horizontal meter toward the 10,000 ceiling with a hard oxide hazard zone
near the cap, so "credits past 10,000 are forfeit" is impossible to miss. This is
the dashboard's thesis moment, chosen over the template "big number + gradient".

## Copy / voice

Quartermaster register, but always in service of clarity (words exist to make the
tool easier to use):

- Near-cap: **"AUTHORIZATION NEAR CEILING — credits earned past 10,000 KC are forfeit."**
- Plans: **"DRAFT REQUISITION"**, items are *authorized*, never *bought*.
- Terminal offline (`lockfile_not_found` / `local_api_unavailable`):
  **"TERMINAL OFFLINE — the Riot Client isn't running. Start VALORANT to connect the requisition line."**
- Schema drift: **"MANIFEST FORMAT CHANGED — Riot altered the API after a patch; some readings may be unavailable until updated."**
- Stale data: show `fetched_at` age, offer **"RE-FETCH"** against the live line.
- Discrepancies are surfaced as a flagged manifest note, never an error/apology.

## Motion (restraint)

Minimal and purposeful only: a brief stamp "set" on status marks at mount, gauge
fill transitions, and hover lift on manifest rows/cards. Respect
`prefers-reduced-motion`. No ambient/scattered effects — extra animation would
read as AI-generated and undercut the instrument feel.

## Quality floor

Responsive to mobile, visible keyboard focus rings (amber), `prefers-reduced-motion`
honored, sufficient contrast (paper-on-graphite and all status colors verified).
