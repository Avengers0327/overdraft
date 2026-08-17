"""
Overdraft — the open Vertical system (v8 §3, §6).

A Vertical is a themed bucket of Case types with a minimum Net Worth Tier. The
registry is open: content modules call register_vertical() at import time, so
adding a vertical never means editing a central list.

Also home to the tier-selection and vertical-weighting half of the draw
pipeline (v8 §6): current_tier() maps cash to a Net Worth Tier, interest_weight()
biases toward recently-played verticals (Granular B.4), and draw_next_case()
runs the full pipeline: tier -> eligible verticals -> weighted pick -> case type
-> tier difficulty -> (traits, outliers layered on by callers).
"""
import random
from dataclasses import dataclass, field

from app.cases import (
    CaseResult, CASE_REGISTRY, TIER_DIFFICULTY, MIN_TIER, MAX_TIER, draw_case,
    case_tier_ok,
)


@dataclass
class Vertical:
    key: str
    title: str
    tagline: str
    min_tier: int
    case_types: list[str] = field(default_factory=list)
    # The curriculum FOUNDATION (Everyday Money), not a theme (v8 §3.1). A foundation
    # vertical is structurally privileged in the draw: it OWNS the run's on-ramp and
    # keeps a permanent floor share forever after — it never fades the way a themed
    # vertical does. Declared here (not hardcoded in the draw code) so the engine stays
    # registration-driven. The design has exactly one; the first marked one is used.
    foundation: bool = False


VERTICAL_REGISTRY: dict[str, Vertical] = {}
# Registration order = board display order. Insertion-ordered dict preserves it.
VERTICAL_ORDER: list[str] = []

# --- Foundation-vertical draw policy (Everyday Money's special role) -----------
# The foundation is the curriculum's floor: everyone learns the fundamentals first,
# and they never stop appearing. Two knobs govern that:
ON_RAMP_LENGTH = 5              # the first N Cases of EVERY run are foundation-only —
                                # no themed vertical is eligible until the on-ramp ends
FOUNDATION_FLOOR_SHARE = 0.20   # after the on-ramp, the foundation keeps at least this
                                # share of the weighted draw at EVERY tier, however many
                                # verticals are open — a floor, so it can never fade out


def register_vertical(v: Vertical) -> Vertical:
    if v.key in VERTICAL_REGISTRY:
        raise ValueError(f"Duplicate vertical registered: {v.key!r}")
    # Fail loudly if a vertical points at a case_type nobody registered — this
    # catches typos and half-wired content at startup, not mid-run.
    missing = [c for c in v.case_types if c not in CASE_REGISTRY]
    if missing:
        raise ValueError(f"Vertical {v.key!r} references unregistered case types: {missing}")
    # A Case's optional tier window must fall within (intersect) the Vertical's own
    # [min_tier, MAX_TIER] range — otherwise the Case could never be drawn. Catch
    # that misconfiguration at startup, not silently at runtime.
    for ct in v.case_types:
        cls = CASE_REGISTRY[ct]
        lo, hi = cls.case_min_tier, cls.case_max_tier
        if lo is not None and hi is not None and lo > hi:
            raise ValueError(f"Case {ct!r}: case_min_tier {lo} > case_max_tier {hi}")
        eff_lo = max(lo if lo is not None else MIN_TIER, v.min_tier)
        eff_hi = min(hi if hi is not None else MAX_TIER, MAX_TIER)
        if eff_lo > eff_hi:
            raise ValueError(
                f"Case {ct!r} tier window [{lo}, {hi}] never intersects vertical "
                f"{v.key!r} range [{v.min_tier}, {MAX_TIER}] — it could never be drawn")
    VERTICAL_REGISTRY[v.key] = v
    VERTICAL_ORDER.append(v.key)
    return v


# ---------------------------------------------------------------------------
# Net Worth Tiers (v8 §2.1) — cash decides the tier
# ---------------------------------------------------------------------------

def current_tier(cash: float) -> int:
    """Map a player's cash (net worth) to a Net Worth Tier, 1-5 (v8 §2.1)."""
    for tier in range(MIN_TIER, MAX_TIER + 1):
        lo, hi = TIER_DIFFICULTY[tier]["cash_range"]
        if cash >= lo and (hi is None or cash < hi):
            return tier
    return MAX_TIER if cash >= TIER_DIFFICULTY[MAX_TIER]["cash_range"][0] else MIN_TIER


def tier_name(tier: int) -> str:
    return TIER_DIFFICULTY.get(tier, {}).get("name", "")


# ---------------------------------------------------------------------------
# Vertical interest-weighting (Granular B.4)
# ---------------------------------------------------------------------------

def interest_weight(vertical_key: str, history: list) -> float:
    """Base 1.0, up to +0.6 for heavy recent engagement, floored at 0.4 so
    eligible-but-unplayed verticals still surface (Granular B.4)."""
    recent = history[-8:]
    if not recent:
        return 1.0
    matches = sum(1 for h in recent if h.get("vertical") == vertical_key)
    return max(0.4, 1.0 + (matches / len(recent)) * 0.6)


# ---------------------------------------------------------------------------
# Archetype affinity (CLAUDE.md §5 — archetype weighting)
# ---------------------------------------------------------------------------
# The archetype chosen at onboarding tilts WHICH of the other open verticals get drawn.
# Each archetype has a MAJOR vertical that starts strong and tapers as the player climbs,
# and a shared MINOR (Startup World) that starts weak and grows in — so a run opens in the
# archetype's home turf and drifts toward the endgame's high-tier content. This multiplies
# interest_weight, and is applied BEFORE the Everyday Money floor in select_vertical, so it
# only ever redistributes the NON-foundation share — it can never touch Everyday Money's
# guaranteed presence (no archetype majors in the foundation).
ARCHETYPE_MAJOR: dict[str, str] = {
    "creator":      "creator_economy",
    "athlete":      "sports_nil",
    "entrepreneur": "trades_hustles",
}
ARCHETYPE_MINOR = "startup_world"          # shared minor for all three archetypes
ARCHETYPES = tuple(ARCHETYPE_MAJOR)        # the valid onboarding choices

# Hard outside-pair floor: at least 1 in every OUTSIDE_FLOOR_WINDOW non-foundation Cases
# must come from a vertical OUTSIDE the player's major/minor pair. This is a HARD RULE
# enforced in the draw (below), not a soft weight — archetype affinity can never fully
# starve another vertical. It exists specifically to protect Trust & Fraud / Digital Traps
# content regardless of archetype (they are outside every archetype's pair). Foundation
# (Everyday Money) draws don't count — the rule governs the NON-foundation composition only.
OUTSIDE_FLOOR_WINDOW = 6


def archetype_weight(vertical_key: str, archetype: str | None, tier: int) -> float:
    """Affinity multiplier for one vertical given the player's archetype and tier.

    Neutral (1.0) for any vertical that is neither the archetype's major nor the shared
    minor — and for a player with no archetype. A simple LINEAR taper by tier (no
    hand-tuned per-tier table):

        t = (tier - 1) / 4            # 0.0 at Tier 1 .. 1.0 at Tier 5
        major = 1.8 - 1.2 * t         # 1.8 -> 0.6   (starts strong, tapers down)
        minor = 1.0 + 0.9 * t         # 1.0 -> 1.9   (starts weak, grows in)

    Everyday Money is never a major or minor, so it always returns 1.0 here — its floor
    is enforced separately and stays untouched by archetype.
    """
    if not archetype:
        return 1.0
    t = (tier - 1) / 4
    if vertical_key == ARCHETYPE_MAJOR.get(archetype):
        return 1.8 - 1.2 * t
    if vertical_key == ARCHETYPE_MINOR:
        return 1.0 + 0.9 * t
    return 1.0


def _outside_floor_due(history: list, archetype: str, foundation_key: str | None) -> bool:
    """True when the most recent (OUTSIDE_FLOOR_WINDOW - 1) consecutive NON-foundation
    draws were ALL inside the archetype's major/minor pair — meaning the next non-foundation
    draw must be forced outside the pair to keep at least 1 in every OUTSIDE_FLOOR_WINDOW
    non-foundation draws outside it.

    Foundation (Everyday Money) draws are skipped, not counted — the rule constrains only the
    composition of the non-foundation draws. Forcing on a streak of WINDOW-1 (=5) inside picks
    caps the run of inside-pair draws at 5, so every 6 consecutive non-foundation draws hold
    at least one outside pick (the strict reading of 'at least 1 in every 6')."""
    pair = {ARCHETYPE_MAJOR.get(archetype), ARCHETYPE_MINOR}
    inside_streak = 0
    for h in reversed(history):
        v = h.get("vertical")
        if v == foundation_key:
            continue
        if v in pair:
            inside_streak += 1
            if inside_streak >= OUTSIDE_FLOOR_WINDOW - 1:
                return True
        else:
            return False   # a recent outside draw already satisfies the window
    return False


def eligible_verticals(tier: int) -> list[Vertical]:
    """Verticals unlocked at this tier or below (v8 §3 min_tier gating)."""
    return [VERTICAL_REGISTRY[k] for k in VERTICAL_ORDER
            if VERTICAL_REGISTRY[k].min_tier <= tier]


def foundation_vertical():
    """The registered foundation vertical (Everyday Money), or None if none is
    marked. Exactly one is expected; the first in registration order wins."""
    for k in VERTICAL_ORDER:
        if VERTICAL_REGISTRY[k].foundation:
            return VERTICAL_REGISTRY[k]
    return None


def vertical_weights(pool: list[Vertical], history: list, tier: int = 1,
                     archetype: str | None = None) -> list[float]:
    """The final draw weight of each vertical in `pool`, in pool order.

    interest-weighting × archetype affinity, with the foundation's permanent floor
    solved in on top. This is the SINGLE source of truth for draw weights: select_vertical()
    below calls it to make the actual pick, and the dev inspection route (/dev/weights)
    calls it to report them — so what's inspected is by construction what's played.

    Not modelled here (they aren't weights): the on-ramp force and the hard outside-pair
    floor, both of which OVERRIDE the weighted pick rather than adjusting it.
    """
    weights = [interest_weight(v.key, history) * archetype_weight(v.key, archetype, tier)
               for v in pool]

    foundation = foundation_vertical()
    if foundation in pool and len(pool) > 1:
        i = pool.index(foundation)
        others = sum(w for j, w in enumerate(weights) if j != i)
        # Weight whose normalized share against `others` equals the floor:
        #   w / (w + others) = f   ->   w = f*others / (1 - f)
        floor_w = FOUNDATION_FLOOR_SHARE * others / (1 - FOUNDATION_FLOOR_SHARE)
        weights[i] = max(weights[i], floor_w)

    return weights


def select_vertical(pool: list[Vertical], history: list, tier: int = 1,
                    archetype: str | None = None) -> Vertical:
    """Pick one vertical from `pool` (already tier-eligible), applying the foundation's
    two privileges and archetype affinity on top of interest-weighting (Granular B.4).

    On-ramp: while the run's Cases-played count (len(history)) is below ON_RAMP_LENGTH,
    force the foundation — the fundamentals come first, before any theme competes,
    regardless of what higher-tier verticals are already open (and regardless of archetype).

    Archetype affinity: each non-foundation vertical's weight is multiplied by
    archetype_weight() — the major leans in early and tapers, the shared minor grows in
    with tier. Applied BEFORE the floor, so it only redistributes the non-foundation share.

    Permanent floor: past the on-ramp, guarantee the foundation at least
    FOUNDATION_FLOOR_SHARE of the draw at every tier. Because the floor is solved against
    the (already archetype-weighted) other verticals, Everyday Money's share is preserved
    exactly no matter how the archetype tilts the rest — affinity never competes with it.

    Hard outside-pair floor: if the archetype's major/minor pair has taken the last
    OUTSIDE_FLOOR_WINDOW-1 non-foundation draws in a row, a non-foundation pick here is
    forced OUTSIDE the pair (overriding the weighted choice). This is a hard rule, not a
    weight — it never touches foundation picks (so Everyday Money's share is untouched),
    only redirecting an inside-pair pick to an outside one so affinity can't starve a
    vertical (protects Trust & Fraud / Digital Traps regardless of archetype).
    """
    foundation = foundation_vertical()

    if foundation in pool and len(history) < ON_RAMP_LENGTH:
        return foundation

    # Archetype multiplies interest weight; the foundation floor is solved in on top.
    # Everyday Money returns 1.0 from archetype_weight() (never a major/minor), so
    # affinity never competes with its floored share. See vertical_weights().
    weights = vertical_weights(pool, history, tier, archetype)

    pick = random.choices(pool, weights=weights, k=1)[0]

    # Hard outside-pair floor. Only meaningful with an archetype and a non-foundation pick;
    # foundation picks are never overridden (Everyday Money's guaranteed share is sacred).
    if archetype and pick is not foundation:
        pair = {ARCHETYPE_MAJOR.get(archetype), ARCHETYPE_MINOR}
        fkey = foundation.key if foundation else None
        if pick.key in pair and _outside_floor_due(history, archetype, fkey):
            outside = [v for v in pool if v is not foundation and v.key not in pair]
            if outside:   # if no outside vertical is drawable at this tier, we can't force
                ow = [interest_weight(v.key, history) * archetype_weight(v.key, archetype, tier)
                      for v in outside]
                pick = random.choices(outside, weights=ow, k=1)[0]

    return pick


def drawable_verticals(tier: int) -> list[Vertical]:
    """The actual draw pool at `tier`: tier-eligible Verticals that still have at
    least one Case allowed at this tier (Case-level windows may retire every Case in
    an otherwise-eligible Vertical — then it's excluded from the draw, not an error).
    Falls back to the first registered Vertical if that leaves nothing."""
    pool = [v for v in eligible_verticals(tier)
            if any(case_tier_ok(ct, tier) for ct in v.case_types)]
    return pool or [VERTICAL_REGISTRY[VERTICAL_ORDER[0]]]


def draw_next_case(cash: float, history: list, forced_vertical: str = None,
                   forced_case_type: str = None, archetype: str | None = None) -> CaseResult:
    """The full draw pipeline (v8 §6), minus the trait/outlier layering that
    main.py stacks on top (those need run-level state this module doesn't own).

    forced_vertical / forced_case_type let a structured run (playing one vertical
    front to back) pin the choice instead of drawing weighted-random. `archetype`
    biases which of the OTHER open verticals draw more/less often (see select_vertical).
    """
    tier = current_tier(cash)

    if forced_case_type:
        return draw_case(forced_case_type, tier=tier)

    if forced_vertical:
        vertical = VERTICAL_REGISTRY[forced_vertical]
    else:
        # On-ramp + foundation floor + archetype affinity live in select_vertical.
        vertical = select_vertical(drawable_verticals(tier), history, tier, archetype)

    # Filter to the Cases allowed at this tier; fall back to all only if the
    # window leaves none (e.g. a forced/fallback Vertical with no tier-fit Case).
    case_types = [ct for ct in vertical.case_types if case_tier_ok(ct, tier)] \
        or vertical.case_types
    case_type = random.choice(case_types)
    return draw_case(case_type, tier=tier)


# ---------------------------------------------------------------------------
# Callback Cases (pattern-recall probe)
# ---------------------------------------------------------------------------
# Every CALLBACK_INTERVAL Cases (past the on-ramp), instead of a normal draw, replay a
# TAGGED case_type the player has already seen — fresh numbers, one fewer evidence layer —
# to test whether they learned the underlying PATTERN, not just that one instance. If the
# player hasn't encountered any tagged case_type yet, the cycle is skipped (normal draw).
CALLBACK_INTERVAL = 9


def callback_due(history: list) -> bool:
    """Whether the NEXT Case (index len(history)+1) is a Callback slot: a multiple of
    CALLBACK_INTERVAL and past the on-ramp (never during the foundation on-ramp)."""
    n = len(history)
    return n >= ON_RAMP_LENGTH and (n + 1) % CALLBACK_INTERVAL == 0


def _seen_case_ids(history: list) -> list:
    """The case_ids the player has actually played, in history order (oldest first)."""
    return [h.get("case_id") for h in history if h.get("case_id")]


def _title_seen(case_id: str, history: list) -> str:
    """The title the player saw for a case_id (from history), or the id as a fallback."""
    for h in history:
        if h.get("case_id") == case_id:
            return h.get("title") or case_id
    return case_id


def _callback_reference(case_type: str, history: list) -> str:
    """Display name for the verdict's 'Same read as ___' line. Prefers a DIFFERENT case in
    the SAME pattern family the player has also seen (the real pattern-transfer signal),
    falling back to this case's own earlier appearance. '' if the case_type isn't tagged."""
    pattern = getattr(CASE_REGISTRY.get(case_type), "pattern", None)
    if not pattern:
        return ""
    for cid in reversed(_seen_case_ids(history)):   # most recent sibling first
        cls = CASE_REGISTRY.get(cid)
        if cid != case_type and cls is not None and getattr(cls, "pattern", None) == pattern:
            return _title_seen(cid, history)
    return _title_seen(case_type, history)           # fall back to its own prior encounter


def draw_callback_case(cash: float, history: list):
    """Build a Callback Case, or None if the player has no replayable tagged Case yet.

    Eligible = a TAGGED case_type the player has encountered AND still tier-legal at the
    current tier (don't resurrect a Case that has since retired, e.g. a low-tier one at
    Outlier). Regenerate it at the current tier with one fewer evidence layer, and stamp
    the callback reference for the verdict screen.
    """
    tier = current_tier(cash)
    eligible = sorted({
        cid for cid in _seen_case_ids(history)
        if getattr(CASE_REGISTRY.get(cid), "pattern", None) and case_tier_ok(cid, tier)
    })
    if not eligible:
        return None
    case_type = random.choice(eligible)
    case = draw_case(case_type, tier=tier, evidence_drop=1)
    case.is_callback = True
    case.callback_ref = _callback_reference(case_type, history)
    return case


def draw_for_player(cash: float, history: list, archetype: str | None = None,
                    forced_vertical: str = None, forced_case_type: str = None) -> CaseResult:
    """The COMPLETE draw pipeline for a player: callback slot first, then the normal
    weighted draw. Pure — it reads state and returns a Case, mutating nothing.

    Callback slot (every CALLBACK_INTERVAL Cases past the on-ramp): replay a tagged Case the
    player has already seen, with less evidence, to probe pattern recall. Falls through to a
    normal draw if the slot isn't due or nothing replayable has been seen yet.

    Lives here rather than in main.py so /play and the dev inspection routes run the
    identical pipeline — /dev/next_case_odds sampling this function is sampling the real
    game. A forced vertical/case_type skips the callback slot: forcing means forcing.
    """
    if forced_vertical or forced_case_type:
        return draw_next_case(cash, history, forced_vertical=forced_vertical,
                              forced_case_type=forced_case_type, archetype=archetype)
    if callback_due(history):
        callback = draw_callback_case(cash, history)
        if callback is not None:
            return callback
    return draw_next_case(cash, history, archetype=archetype)
