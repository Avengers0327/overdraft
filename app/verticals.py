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


VERTICAL_REGISTRY: dict[str, Vertical] = {}
# Registration order = board display order. Insertion-ordered dict preserves it.
VERTICAL_ORDER: list[str] = []


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


def eligible_verticals(tier: int) -> list[Vertical]:
    """Verticals unlocked at this tier or below (v8 §3 min_tier gating)."""
    return [VERTICAL_REGISTRY[k] for k in VERTICAL_ORDER
            if VERTICAL_REGISTRY[k].min_tier <= tier]


def draw_next_case(cash: float, history: list, forced_vertical: str = None,
                   forced_case_type: str = None) -> CaseResult:
    """The full draw pipeline (v8 §6), minus the trait/outlier layering that
    main.py stacks on top (those need run-level state this module doesn't own).

    forced_vertical / forced_case_type let a structured run (playing one vertical
    front to back) pin the choice instead of drawing weighted-random.
    """
    tier = current_tier(cash)

    if forced_case_type:
        return draw_case(forced_case_type, tier=tier)

    if forced_vertical:
        vertical = VERTICAL_REGISTRY[forced_vertical]
    else:
        # Only consider Verticals that have at least one Case actually allowed at
        # this tier (Case-level windows may retire every Case in an otherwise-
        # eligible Vertical — then it's excluded from the draw, not an error).
        pool = [v for v in eligible_verticals(tier)
                if any(case_tier_ok(ct, tier) for ct in v.case_types)]
        if not pool:
            pool = [VERTICAL_REGISTRY[VERTICAL_ORDER[0]]]
        weights = [interest_weight(v.key, history) for v in pool]
        vertical = random.choices(pool, weights=weights, k=1)[0]

    # Filter to the Cases allowed at this tier; fall back to all only if the
    # window leaves none (e.g. a forced/fallback Vertical with no tier-fit Case).
    case_types = [ct for ct in vertical.case_types if case_tier_ok(ct, tier)] \
        or vertical.case_types
    case_type = random.choice(case_types)
    return draw_case(case_type, tier=tier)
