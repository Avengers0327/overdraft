# Overdraft

A financial literacy game for ages 10-15. You start broke, climb Net Worth
Tiers by making sharp calls on real financial decisions, and can fall — hard
— from bad ones. Built to teach without ever pausing to explain.

## Run it

**Terminal:**

pip install -r requirements.txt
uvicorn app.main:app --reload


**PyCharm:** right-click `app/main.py` → Run. Opens on `http://127.0.0.1:8000`
(or `:8001` if running via the `__main__` block — check the printed URL).

## The core loop

Every decision is a Case:

DEAL → YOUR CALL → PLACE YOUR BET → EVIDENCE (staged reveal) → VERDICT → next Case


Three interaction shapes, set per-Case via `pick_type`:
- **binary** — pick option A or B, bet on the outcome, see who wins
- **investigation** — no pick, just open the file and bet on what you'll find
- **navigation** — a dark-pattern friction sequence (e.g. canceling a
  subscription), no pick, no bet, the friction itself is the lesson

Numbers are always generated procedurally within realistic bounds — no
Case is ever hardcoded to one scenario. Bet accuracy scores as
**NAILED IT** / **SO CLOSE** / **WAY OFF**.

## Net Worth Tiers

Cash isn't a score — it's your net worth, and it *is* your difficulty level.
Five tiers, Broke to Outlier, gate which Verticals can appear:

| Tier            | Cash             |                                                                                                                 |
|-----------------|------------------|-----------------------------------------------------------------------------------------------------------------|
| 1 — Broke       | $0 – $250        | Wide bet ranges, no deception, low stakes precision-wise — but a bad call costs you 30% of what little you have |
| 2 — Stable      | $250 – $1,000    |                                                                                                                 |
| 3 — Comfortable | $1,000 – $5,000  | The game starts lying to you on purpose ~1/3 of the time                                                        |
| 4 — Wealthy     | $5,000 – $25,000 | Real debt, real interest, 4 evidence layers                                                                     |
| 5 — Outlier     | $25,000+         | Tightest bet ranges, ~50% deception rate, Outlier Events possible                                               |

**Difficulty is two separate axes, moving in opposite directions:**
- **Precision/complexity** (bet range tightness, evidence layers,
  deception rate) — goes **up** with tier. More money, more variables:
  taxes, market swings, interest rates, scams.
- **Stakes** (`stakes_pct` — what a bad call costs as a % of your cash) —
  goes **down** with tier. Life is genuinely brutal at the bottom (a bad
  call at Tier 1 costs real percentage points you can't afford to lose)
  and comparatively forgiving at the top in percentage terms, even though
  the new failure modes at high tiers are individually larger.

Tier is never fixed — it's recomputed live from cash after every Case.
You can fall as easily as you climb.

## Busting

Not a slow bleed to zero — a **loss streak**. Any `WAY OFF` + wrong pick
counts against the streak; any `NAILED IT` or `SO CLOSE` resets it to zero.
Hit the bust threshold (4 consecutive losses, by default) at **any** tier
and the run ends — a Tier 5 player can absolutely bust in one bad
streak. The Cold Case recap reads your peak net worth to frame the fall
honestly, not just the raw cash lost.

## Starting position

Three onboarding choices, each a real tradeoff, not just flavor:
- **Default** — start at Tier 1. The full intended experience.
- **Old Money** — start at Tier 2. No drawback, a soft easy mode.
- **Nepo Baby** — start at Tier 3 or 4, but stakes double if you ever fall
  back to Tier 1 or 2 — you never built the instincts, so hitting bottom
  actually hurts more than it would for someone who started there.

## Traits

Chosen/unlocked modifiers that change how the numbers behave — not just
flat cash bonuses. Several hook directly into stakes and the loss streak:
Diversifier halves your stakes percentage everywhere; House of Cards lowers
your bust threshold to 3 in exchange for bigger wins; Emergency Fund
Enjoyer breaks a dangerous streak instead of just absorbing one hit. Full
table and formulas in `Granular_GDD.md` and `CLAUDE.md`.

## Verticals

Themed pools of Cases (Everyday Money, Creator Economy, Trust & Fraud, Real
Estate & Assets, Startup World, and more), gated by minimum tier, selected
with light interest-weighting so a run can lean into a theme without fully
losing variety. The registry is **open** — adding a vertical is a new file
calling `register_vertical()`, never a change to the engine.

## Architecture

app/
cases.py Case engine: CaseResult, CaseTemplate, CASE_REGISTRY,
tier difficulty, bet scoring, cash rewards
verticals.py Vertical registry, tier lookup, interest-weighted draw
traits.py NOT YET BUILT — Trait registry and stakes/streak hooks
outliers.py NOT YET BUILT — log-normal/categorical Outlier Events
db.py SQLite. One row per player = one continuous run. Cash IS
net worth IS tier — no separate "run" or "chapter" table.
main.py FastAPI routes: onboarding → the loop → bust/recap
content/ NOT YET BUILT — Case + Vertical registrations, one file
per vertical, imported for side effects in main.py
templates/ NEEDS UPDATING — written against an earlier CaseResult
shape, not yet current with pick_type/tier/vertical fields


Adding a new Case type: subclass `CaseTemplate`, decorate with
`@register_case`, generate every number procedurally within the bounds
specified in `Granular_GDD.md`. Adding a new Vertical: create a `Vertical`
and call `register_vertical()` — nothing else needs to change.

## Design docs

- `Granular_GDD.md` — every Case fully scripted, exact formulas
- `GDD_v8_FULLY_FLESHED.md` — system architecture and curriculum crosswalk
- `CLAUDE.md` — session context, current build state, and the locked
  refinements (two-axis difficulty, streak-based busting, starting
  positions, reworked Traits) that supersede the GDDs' original numbers
  where they conflict

## Tech stack

FastAPI + HTMX + Jinja2 + SQLite. No frontend framework, no game engine,
no other database — deliberately, so a solo Python developer can ship this.

## Status

Engine (`cases.py`, `verticals.py`, `db.py`, `main.py`) is architected and
internally consistent. Not yet runnable end to end — needs the `content/`
package (actual Case + Vertical registrations), `traits.py`, and updated
templates before `uvicorn app.main:app` serves a playable game. See
`CLAUDE.md`'s Build Order for the exact sequence.