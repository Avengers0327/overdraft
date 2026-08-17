"""
Overdraft — Case engine core.

This is the loop's beating heart: the CaseResult record (one Case from first
look to verdict), the CaseTemplate base every Case subclasses, the open
CASE_REGISTRY, and the Part-B mechanics that live at the Case level —
tier difficulty (Granular B.1 / v8 §2.3) and bet scoring / rewards.

Vertical selection, traits, and outlier events live in their own modules
(verticals.py, traits.py, outliers.py) per v8 §6. Nothing here imports those,
to keep the dependency graph one-directional: content -> engine, never back.

Interaction shapes (CaseResult.pick_type):
  * "binary"        — pick option A or B, then bet, then verdict (classic loop)
  * "investigation" — no pick; open the file, read evidence, bet, "CASE SOLVED"
  * "navigation"    — a dark-pattern friction sequence; no pick, no bet, no winner
"""
import random
from dataclasses import dataclass, field, asdict
from typing import Callable, Optional


# ---------------------------------------------------------------------------
# CaseResult — the serialized state of one Case, first look to verdict
# ---------------------------------------------------------------------------

@dataclass
class CaseResult:
    case_id: str
    title: str

    vertical: str = ""
    tier: int = 2

    pick_type: str = "binary"          # binary | investigation | navigation
    has_bet: bool = True               # navigation Cases skip the bet step

    first_look: str = ""
    option_a_label: str = ""
    option_b_label: str = ""
    option_a_teaser: str = ""          # partial info only — that's the point
    option_b_teaser: str = ""
    # Real-dollar price of an option, set ONLY when picking it is an actual purchase
    # the player pays for out of pocket now (e.g. Free-to-Play's $4.99 Pro). None on
    # every option that isn't a purchase (signing a deal, opening an account, placing
    # savings — those cost nothing to choose). When set and the player's cash is below
    # it, the option is blocked: you can't buy what you can't afford (Bug 1). Costs are
    # NOT debited from cash — cash tracks bet skill, not scenario spending — the field
    # only gates selectability, so a broke player can't collect the reward "as if paid."
    option_a_cost: Optional[float] = None
    option_b_cost: Optional[float] = None
    deception_eligible: bool = True    # can tier difficulty flip the teaser framing?

    picked: Optional[str] = None       # "a"/"b" after the pick (None if no pick)

    bet_range: tuple = (0, 100)
    bet_label: str = "Place your bet — where do you think this lands?"

    evidence: list = field(default_factory=list)   # (label, value_str), revealed in order
    winner: Optional[str] = None       # "a" | "b" | "tie" | "solved"
    actual_value: Optional[float] = None
    case_notes: str = ""
    is_boss: bool = False

    # Outlier-event provenance (v8 §5). Set when a Tier-5 Case is replaced by an
    # Outlier Event, so the verdict screen can frame it as rare-air.
    is_outlier: bool = False
    outlier_key: str = ""

    # Callback provenance. Set when this draw is a Callback Case (a replay of a case_type the
    # player already saw, with one fewer evidence layer). callback_ref is the display name of a
    # sibling in the same pattern family the player also encountered — shown as one quiet line on
    # the verdict screen ONLY if they read it correctly. Never surfaced pre-bet (the test is silent).
    is_callback: bool = False
    callback_ref: str = ""

    # Navigation sub-mechanic state (D1 — Dark Pattern Cancel).
    nav_screens: list = field(default_factory=list)
    nav_step: int = 0
    nav_taps: int = 0
    nav_seconds: int = 0
    nav_outcome: str = ""              # "" | "canceled" | "retained"

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "CaseResult":
        d = dict(d)
        # JSON round-trips tuples as lists; restore the ones we rely on as tuples.
        d["bet_range"] = tuple(d.get("bet_range", (0, 100)))
        d["evidence"] = [tuple(e) for e in d.get("evidence", [])]
        return cls(**d)


class CaseTemplate:
    """Base class every Case type subclasses. Subclasses set case_type and
    implement generate() -> CaseResult with numbers rolled procedurally within
    the GDD's stated bounds. Never hardcode a scenario's numbers."""
    case_type = "base"

    # Optional Case-level tier window, ADDITIONAL to (never replacing) the
    # Vertical's own min_tier gating. None = evergreen (no extra restriction).
    # Use these when a Case's premise or dollar scale only makes sense over part
    # of its Vertical's tier range — e.g. an entry-point Case that should retire
    # once the player has clearly progressed (case_max_tier), or an advanced-
    # premise Case that shouldn't appear at the low end (case_min_tier).
    case_min_tier: Optional[int] = None
    case_max_tier: Optional[int] = None

    # The tier this Case is being drawn for, set by draw_case() BEFORE generate() runs
    # so a Case can scale its scenario DOLLAR amounts to the tier (foundation Cases do;
    # most ignore it). None only in low-level direct use — treat as the anchor (Tier 1),
    # i.e. no scaling. This is the draw target; the separate apply_tier_difficulty() step
    # (bet-range tightening, evidence cap) still runs afterward on the same tier.
    target_tier: Optional[int] = None

    # Callback pattern — the UNDERLYING lesson this Case teaches, never shown to the
    # player. Case types sharing a `pattern` are siblings; the Callback Case mechanic
    # (verticals.py, wired later) replays one with one fewer evidence layer to test whether
    # the player learned the PATTERN, not just that one instance, and can reference a sibling
    # on the verdict screen. None = not yet part of a tagged pattern family (most Cases —
    # we tag only the clearest overlaps first, not everything at once).
    pattern: Optional[str] = None

    def generate(self) -> CaseResult:
        raise NotImplementedError


def case_tier_ok(case_type: str, tier: int) -> bool:
    """Whether a Case type may appear at `tier`, per its optional Case-level tier
    window (separate from, and on top of, its Vertical's min_tier gating)."""
    cls = CASE_REGISTRY[case_type]
    lo, hi = cls.case_min_tier, cls.case_max_tier
    return (lo is None or tier >= lo) and (hi is None or tier <= hi)


# ---------------------------------------------------------------------------
# Open Case registry — content modules register their templates at import time
# ---------------------------------------------------------------------------

CASE_REGISTRY: dict[str, Callable[[], CaseTemplate]] = {}


def register_case(cls: type[CaseTemplate]) -> type[CaseTemplate]:
    """Class decorator: add a CaseTemplate to the open registry under its
    case_type. Used by every module under app/content/."""
    if cls.case_type in CASE_REGISTRY:
        raise ValueError(f"Duplicate case_type registered: {cls.case_type!r}")
    CASE_REGISTRY[cls.case_type] = cls
    return cls


# ===========================================================================
# PART B.1 — Tier difficulty  (formula: Granular_GDD B.1 · numbers: v8 §2.3)
# ===========================================================================
#
# v8 §2.3 gives the difficulty table. `range_keep` below is the fraction of a
# Case's bet span that survives tightening — Granular B.1 defines
# new_span = span * range_keep, so a SMALLER range_keep = a tighter, harder bet.
#
# CONTRADICTION NOTE (resolved deliberately): v8 §2.1's texture says Tier 1 has
# "wide bet ranges" and Tier 5 is "tight — real precision required," i.e.
# difficulty should tighten as tiers rise. But v8 §2.3's literal column pairs
# Tier 1 with 0.45 and Tier 5 with 1.0, which under B.1's formula makes Tier 5
# the *widest* (easiest) — the opposite of the stated intent and of any sane
# difficulty curve. We honor the unambiguous intent: range_keep DECREASES with
# tier (Tier 1 fully forgiving, Tier 5 tightest), reusing v8's exact number set.
# This is the single tunable that reconciles the two locked docs; flip the
# mapping here if the raw §2.3 pairing is ever confirmed as intended.
# `stakes_pct` (Locked Refinement #1) is the SECOND difficulty axis: the fraction
# of current cash at risk on a bad call. It DECREASES with tier — life is brutal
# with no money (Tier 1: lose 30% on a bad call) and forgiving in percentage terms
# once wealthy (Tier 5: 4%), even though the endgame's dollar losses are larger.
# This is deliberately the opposite curve from range_keep (precision UP with tier).
TIER_DIFFICULTY: dict[int, dict] = {
    1: {"name": "Broke",       "cash_range": (0, 250),
        "range_keep": 1.00, "evidence_layers": 2, "deception_rate": 0.00, "stakes_pct": 0.30},
    2: {"name": "Stable",      "cash_range": (250, 1000),
        "range_keep": 0.88, "evidence_layers": 3, "deception_rate": 0.10, "stakes_pct": 0.20},
    3: {"name": "Comfortable", "cash_range": (1000, 5000),
        "range_keep": 0.75, "evidence_layers": 3, "deception_rate": 0.33, "stakes_pct": 0.12},
    4: {"name": "Wealthy",     "cash_range": (5000, 25000),
        "range_keep": 0.60, "evidence_layers": 4, "deception_rate": 0.40, "stakes_pct": 0.07},
    5: {"name": "Outlier",     "cash_range": (25000, None),
        "range_keep": 0.45, "evidence_layers": 4, "deception_rate": 0.50, "stakes_pct": 0.04},
}

MIN_TIER = 1
MAX_TIER = 5


def apply_tier_difficulty(case: CaseResult, tier: int, evidence_drop: int = 0) -> CaseResult:
    """Scale a freshly generated Case to a tier (Granular B.1, verbatim shape).

    1. Tighten the bet range around its midpoint (keep `range_keep` of the span),
       but never so far that the correct answer falls off the slider — a range
       that can't express the right bet makes the Case unwinnable by construction.
    2. Cap evidence to the tier's layer count — cap only, never pad fake layers.
       `evidence_drop` trims that cap by an extra N layers (Callback Cases pass 1),
       clamped so at least one row always survives.

    NOTE: the GDD's tier-difficulty step 3 was a "deception roll" that swapped
    option_a_teaser <-> option_b_teaser. That's removed: every Case here writes
    OPTION-SPECIFIC, factual teasers (dollar figures tied to that option), so
    swapping them mislabels the options ("$540 now" under the evergreen label)
    rather than merely reframing appeal. The teaser must always match its own
    label. `deception_rate` is kept in TIER_DIFFICULTY (per CLAUDE.md, and for a
    future deception redesign that uses generic appeal-framing teasers), and
    `deception_eligible` still gates the real-stakes LOSS path in case_reward().
    """
    profile = TIER_DIFFICULTY.get(tier, TIER_DIFFICULTY[2])
    case.tier = tier

    lo, hi = case.bet_range
    span = hi - lo
    slack = span * (1 - profile["range_keep"])
    new_lo, new_hi = lo + slack / 2, hi - slack / 2
    # Clamp the tightened window so it always still contains actual_value.
    # Midpoint-tightening alone can evict an answer that sits near an edge (worst
    # at high tiers, where the window shrinks most), leaving the player unable to
    # bet correctly. Reachability of the answer beats hitting the exact width.
    if case.actual_value is not None:
        new_lo = min(new_lo, case.actual_value)
        new_hi = max(new_hi, case.actual_value)
    case.bet_range = (new_lo, new_hi)

    layers = max(1, profile["evidence_layers"] - evidence_drop)
    case.evidence = case.evidence[:layers]

    # (No teaser swap — see docstring. Teasers stay bound to their own labels.)
    return case


# ===========================================================================
# Drawing
# ===========================================================================

def draw_case(case_type: Optional[str] = None, seed: Optional[int] = None,
              tier: Optional[int] = None, evidence_drop: int = 0) -> CaseResult:
    """Generate one Case, then apply tier difficulty.

    `tier` here scales the Case; when None the Case keeps its own default tier.
    The full tier -> vertical -> case_type selection lives in verticals.py; this
    is the low-level "make me this case_type at this tier" primitive.
    Pass `seed` for Daily Seed mode (same seed = same numbers for everyone).
    `evidence_drop` shows that many fewer evidence layers than the tier normally would
    (Callback Cases pass 1 — a leaner post-bet reveal).
    """
    if seed is not None:
        random.seed(seed)
    if case_type is None:
        case_type = random.choice(list(CASE_REGISTRY.keys()))
    tmpl = CASE_REGISTRY[case_type]()
    # Tell the template which tier it's being drawn for BEFORE generate(), so a Case can
    # scale its scenario dollars to the tier (foundation Cases do; most ignore target_tier).
    tmpl.target_tier = tier
    case = tmpl.generate()
    return apply_tier_difficulty(case, tier if tier is not None else case.tier,
                                 evidence_drop=evidence_drop)


# ===========================================================================
# Bet scoring + cash rewards
# ===========================================================================

def score_bet(bet_value: float, actual_value: float) -> tuple[str, str]:
    """(result_tier, feedback_line). Never says 'wrong' — always upbeat framing."""
    if actual_value == 0:
        pct_off = abs(bet_value - actual_value)
    else:
        pct_off = abs(bet_value - actual_value) / abs(actual_value)

    if pct_off <= 0.10:
        return "nailed_it", "NAILED IT"
    elif pct_off <= 0.25:
        return "so_close", "SO CLOSE"
    return "way_off", "WAY OFF"


# Rewards are GROUNDED in each Case's own actual_value — the scenario's real stakes —
# not an abstract tier point-table (the old TIER_REWARD_BASE/ACCURACY_MULT approach was
# fully decoupled from the numbers on screen, paying +$36 to WAY-OFF a $7.99 Gems Case
# while a NAILED-IT $840 Case paid $225). Now cash tracks what the scenario said was at
# stake: nail it and you gain roughly the winning choice's worth; miss and you give a
# slice of it (or the stakes_pct wrong-pick loss) back.
NAILED_CAP_MULT = 3        # any positive payout is capped at this × current cash (anti-explosion:
                           # a single lucky Tier-5 log-normal Outlier must not 100x a run)
WAY_OFF_MISS_PCT = 0.15    # flat penalty when you read the situation right but missed the
                           # number — or on a tie/investigation Case with no wrong pick to make
JUDGMENT_BONUS_PCT = 0.10  # flat bonus for a CORRECT call on a binary Case, on top of the
                           # precision reward — rewards judgment separately from bet accuracy


LOSS_FLOOR = 1        # a single Case can never leave cash below this (Locked Refinement #2)
BUST_THRESHOLD = 4    # consecutive losses that end the run (Locked Refinement #3)


def case_reward(result_tier: str, picked: Optional[str], winner: Optional[str],
                tier: int, cash: float = 0, actual_value: float = 0.0,
                deception_eligible: bool = True,
                stakes_mult: float = 1.0) -> tuple[int, bool, bool]:
    """Cash delta for a bet Case, grounded in actual_value. Returns (delta, called_it, capped).

    called_it: a tie/investigation Case ("tie"/"solved" winner) has no wrong pick, so it
    always counts as called; a binary Case counts only when picked == winner.

    Precision component (bet accuracy):
      NAILED IT -> +round(|actual_value|), roughly what the winning choice was worth.
      SO CLOSE  -> 0. Pure breakeven — close isn't wrong, but it isn't a win.
      WAY OFF, wrong pick (called_it == False) on a deception_eligible binary Case -> the
          stakes_pct LOSS path, UNCHANGED (Locked Refinement #1-2): -round(cash * stakes_pct *
          stakes_mult); this branch takes NO judgment bonus and returns immediately.
      WAY OFF otherwise (you called the winner but missed the math, OR a tie/investigation Case
          with no wrong pick) -> the smaller flat -round(|actual_value| * WAY_OFF_MISS_PCT).

    Judgment component (Fix 2): on a BINARY Case where you called the winner (called_it == True
    AND there was a real wrong pick to avoid), add a flat +round(|actual_value| *
    JUDGMENT_BONUS_PCT) ON TOP of the precision reward — at every accuracy tier. This rewards
    reading the situation right, separately from nailing the number. It does NOT apply to
    tie/investigation Cases (no "call" to make — precision is the only skill there) and never
    to a wrong pick.

    Any positive payout (precision + bonus) is capped at NAILED_CAP_MULT × cash (capped=True so
    the verdict can say so). Every loss is clamped so a SINGLE Case can't drop cash below
    LOSS_FLOOR; only a loss STREAK ends a run (bust is streak-based — Locked Refinement #3).
    Magnitude uses abs() so a Case whose bet target is negative (e.g. a −$134 fee net) still
    pays a positive reward for nailing it.
    """
    has_wrong_pick = winner in ("a", "b")
    called_it = (not has_wrong_pick) or picked == winner
    magnitude = abs(round(actual_value or 0))
    floor_room = max(0, int(cash) - LOSS_FLOOR)   # the most a single Case may ever take
    cap = NAILED_CAP_MULT * int(cash)

    # Wrong-pick WAY OFF on a deception-eligible binary Case: the stakes_pct loss path, exactly
    # as before. No judgment bonus (you didn't call it), no precision reward — return here.
    if result_tier == "way_off" and has_wrong_pick and not called_it and deception_eligible:
        stakes_pct = TIER_DIFFICULTY.get(tier, TIER_DIFFICULTY[2])["stakes_pct"]
        loss = round(cash * stakes_pct * stakes_mult)
        return -min(loss, floor_room), called_it, False

    # Precision component.
    if result_tier == "nailed_it":
        base = magnitude
    elif result_tier == "so_close":
        base = 0
    else:   # way_off, but called-it (binary) or a tie/investigation Case with no wrong pick
        base = -min(round(magnitude * WAY_OFF_MISS_PCT), floor_room)

    # Judgment component — only a genuine correct call on a binary Case earns it.
    judgment_bonus = round(magnitude * JUDGMENT_BONUS_PCT) if (has_wrong_pick and called_it) else 0

    reward = base + judgment_bonus
    if reward > cap:                       # cap ALL positive payouts, so the bonus can't
        return cap, called_it, True        # sneak past the anti-explosion ceiling
    return reward, called_it, False


def recognition_reward(called_it: bool, tier: int, cash: float,
                       deception_eligible: bool = True,
                       stakes_mult: float = 1.0) -> int:
    """Cash delta for a RECOGNITION Case — a binary Case with has_bet=False.

    Fraud detection is a JUDGMENT skill (spot the pattern), not a PRECISION skill
    (estimate a number), so there is no bet to score and nothing to ground a reward in
    the way case_reward() grounds itself in actual_value. The payout is therefore keyed
    to the tier's stakes_pct and is SYMMETRIC:

        called it  ->  +round(cash * stakes_pct)
        missed it  ->  -round(cash * stakes_pct * stakes_mult)

    The loss side is deliberately the SAME stakes_pct penalty any other binary Case's
    wrong pick takes (Locked Refinement #1-2) — falling for a scam costs what a bad call
    costs. No bet-accuracy multiplier is involved on either side, because there is no bet.

    Symmetry means the tier curve carries through untouched: spotting a scam is worth 30%
    of your cash at Broke and 4% at Outlier, matching the two-axis design (stakes DOWN as
    tier rises) without inventing a dollar figure the scripts never specified.

    `deception_eligible=False` disables the loss side only (a no-shame recognition Case
    could reward the right call without punishing the wrong one); the gain side is unaffected.
    Losses are clamped so a SINGLE Case can't drop cash below LOSS_FLOOR — only a streak
    ends a run, and a missed recognition Case feeds that streak like any other wrong pick.
    """
    stakes_pct = TIER_DIFFICULTY.get(tier, TIER_DIFFICULTY[2])["stakes_pct"]
    if called_it:
        return round(cash * stakes_pct)
    if not deception_eligible:
        return 0
    floor_room = max(0, int(cash) - LOSS_FLOOR)
    return -min(round(cash * stakes_pct * stakes_mult), floor_room)


def loss_streak(history: list[dict]) -> int:
    """Consecutive losses ending at the most recent Case (Locked Refinement #3).
    Any nailed_it or so_close resets it to 0 — one good call pulls you back from
    the edge. A loss is a `way_off` result on a wrong pick."""
    streak = 0
    for h in reversed(history):
        if h.get("result_tier") == "way_off" and not h.get("called_it"):
            streak += 1
        else:
            break
    return streak


# PROVISIONAL: navigation Cases (D1 Dark Pattern Cancel) have no bet and no actual_value,
# so the reward can't be grounded the way case_reward() now is. This flat payout is a
# placeholder until the navigation sub-mechanic is actually wired and balanced — nav_reward
# is not yet called anywhere. Revisit the number then rather than treating it as tuned.
NAV_COMPLETE_REWARD = 40


def nav_reward(outcome: str) -> int:
    """Navigation Cases have no bet — a flat payout for completing the friction
    lesson, halved if the dark pattern actually retained you."""
    return NAV_COMPLETE_REWARD if outcome == "canceled" else NAV_COMPLETE_REWARD // 2


STARTING_CASH = 100   # opens the player in Tier 1 (Broke), per v8 §2.1
