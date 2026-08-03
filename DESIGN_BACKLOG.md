# DESIGN BACKLOG — Post-v9 additions
## Status: DESIGN PHASE. Nothing below is built. Build order TBD once design closes.

This doc exists so ideas from open-ended design conversation don't get lost or
half-implemented out of order. Everything here is a proposal until it's
promoted into CLAUDE.md's "Locked Refinements" — promotion happens deliberately,
not by default.

---

## 1. BUG FIXES (found via screenshots, real bugs in existing code — not design, just broken)

- **Sponsorship Offer (C1):** option_a_teaser/option_b_teaser are swapped —
  each option displays the OTHER option's description.
- **Algorithm Shock (C2):** displayed evidence formula and actual_value
  disagree due to separate rounding paths ("$441 × 0.31 = $135" when the
  real product rounds to $137). Evidence text must be built from the same
  final numbers the bet is scored against.
- **Evidence row overflow:** long values clip at the card edge instead of
  wrapping (seen on Merch Drop Math). CSS fix, applies to every Case, not
  just this one.

**These are not design decisions — fix whenever building resumes, first,
before any new content.**

---

## 2. INSTINCT PATHS (supersedes the earlier flat "Instinct Archetype" idea)

Chosen at onboarding, alongside (not merged with) the starting-tier choice
(Default/Old Money/Nepo Baby). Biases vertical draw weighting via
`interest_weight()` — never hard-locks, per the "overlap, not exclusion" rule.
Overlap is thematic-only; mechanics (stakes_pct, streak thresholds, reward
math) stay universal regardless of Path.

Each Path = a starting vertical (open, Tier 1-accessible) + a capstone
vertical (Tier 5-gated, thematically specific).

| Path           | Start vertical                                                                                | Capstone                       | Capstone status            |
|----------------|-----------------------------------------------------------------------------------------------|--------------------------------|----------------------------|
| Creator        | Creator Economy                                                                               | Famous Creator                 | New vertical, not designed |
| Trades/Hustles | Trades & Hustles                                                                              | Founder (reuses Startup World) | No new vertical needed     |
| Sports         | Sports & NIL                                                                                  | Famous Athlete                 | New vertical, not designed |
| Dev            | **Side Projects** (proposed, not designed — small coding gigs, app flips, freelance dev work) | Game Studio                    | Both new, not designed     |

**Open decision, not yet made:** build distinct capstones for all 4 paths,
or let some share Startup World as a generic capstone (cheaper, weaker
narrative payoff). Leaning toward 2-3 real capstones + shared fallback for
the rest, but not committed.

**NIL** (Sports & NIL vertical name) = Name, Image, and Likeness — the real
industry term for athlete endorsement deals. Worth a one-line tooltip/glossary
entry in the actual UI, since players won't know the acronym either.

---

## 3. CROSS-VERTICAL CASES (newest idea — least developed, needs its own design pass)

Cases that deliberately reference or combine two verticals instead of staying
in one lane — e.g. a Creator Case that needs Trades & Hustles-style production
logistics (merch fulfillment at scale), a Startup World Burn Rate Case that
requires Creator Economy marketing instincts to survive. Goal: make the
vertical set feel like one connected world at higher tiers, not 7 silos.

**Not yet designed:** which specific vertical pairs cross over, whether these
are a distinct `pick_type` or just Cases that happen to draw stats from two
domains, whether they're gated to late-game (likely, given they presuppose
the player has context from multiple verticals) or can appear earlier.

**Recommend:** revisit this only after at least 2 Paths have their capstones
built — crossover Cases referencing verticals that don't exist yet can't be
designed concretely.

---

## 4. PRIOR SESSION'S BACKLOG (from CLAUDE.md, restated here so it's not lost under new material)

Reminder — these were "locked" before this session's new ideas arrived and
still take priority over everything in sections 2-3 above:
- `stakes_pct` axis + loss path in `case_reward()`
- `loss_streak()` + bust check (threshold 4, at any tier)
- Starting-position archetypes (Default/Old Money/Nepo Baby)
- Traits rework (Emergency Fund Enjoyer, Diversifier, The 1%, Soft Landing,
  House of Cards, Comeback Kid)
- `app/content/` package (nothing is registered yet — the app cannot run
  end to end without this, regardless of any other item on this list)
- `app/traits.py`, template updates

---

## PRIORITY READ (for whenever design phase ends)

Sections 2 and 3 are **additive content/theming layers**. Section 4 is
**the engine itself, and it doesn't exist as runnable code yet.** No amount
of Path/capstone/crossover design produces a playable game until Section 4's
first two items (`app/content/` and the stakes/streak mechanics) are built.
Keep that ordering intact whenever this shifts back to build mode, regardless
of which new idea feels most exciting at the time.
