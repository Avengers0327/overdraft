"""
VERTICAL — Insurance & Risk Transfer  (v8 §3.9 · Granular_GDD Part A, I1-I2)

Tier 3+ vertical, content-complete (both Cases new-scripted). These teach
expected value under uncertainty: the outcome is rolled, and the Evidence that
resolves it is only revealed on the verdict screen — after the bet is locked.
"""
import random

from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical


@register_case
class SkipVsCoverCase(CaseTemplate):
    """I1 — Skip vs Cover (Tier 3). A weighted random event decides whether skipping
    insurance was cheap or expensive this year. Explicitly NOT a scripted 'insurance
    always wins' — the bet is on the realized cost of skipping (Granular B.3)."""
    case_type = "skip_vs_cover"

    def generate(self) -> CaseResult:
        premium_mo = 12
        premium_year = premium_mo * 12   # $144

        roll = random.random()
        if roll < 0.70:
            loss, scenario = 0, "Nothing happened this year"
        elif roll < 0.92:
            loss = random.randint(200, 600)
            scenario = f"Minor incident — ${loss} loss"
        else:
            loss = random.randint(1500, 4000)
            scenario = f"Major incident — ${loss:,} loss"

        # a = skip, b = cover. Skipping only wins the year nothing goes wrong.
        winner = "a" if loss == 0 else "b"

        r = CaseResult(
            case_id="skip_vs_cover",
            title="Skip vs Cover",
            vertical="insurance",
            tier=3,
            first_look=f"Renters insurance: ${premium_mo}/mo  vs  skip it, save the ${premium_mo}.",
            option_a_label="Skip it — save the $12/mo",
            option_b_label="Get renters insurance",
            option_a_teaser="$0 out of pocket · nothing goes wrong most years",
            option_b_teaser=f"${premium_mo}/mo · someone else eats the big loss",
            bet_range=(0, 3200),
            bet_label="Place your bet — total cost of skipping insurance this year, given what happens?",
        )
        r.evidence = [
            ("12 months of premiums if insured", f"${premium_year}"),
            ("This year's rolled event", scenario),
            ("Your cost skipping  vs  insured",
             f"${loss:,}  vs  ${premium_year} (+ any deductible)"),
        ]
        r.winner = winner
        r.actual_value = float(loss)
        r.case_notes = ("You skipped it and nothing happened — that's not proof it was smart; "
                        "ask again next year." if loss == 0 else
                        f"${premium_year} would have covered most of this. Now you know what the "
                        f"bet costs when it doesn't land.")
        return r


@register_case
class DeductibleTradeoffCase(CaseTemplate):
    """I2 — Deductible Tradeoff (Tier 3). No universal answer: the cheaper plan
    depends on how many claims you file, which is rolled. Bet is Plan A's realized
    total cost for the year."""
    case_type = "deductible_tradeoff"

    def generate(self) -> CaseResult:
        # Clean teaching numbers per the script (the rolled variable is claim count).
        a_premium_year, a_deductible = 480, 1000   # $40/mo, high deductible
        b_premium_year, b_deductible = 780, 250     # $65/mo, low deductible

        claims = random.choices([0, 1, 2], weights=[0.6, 0.3, 0.1])[0]
        a_total = a_premium_year + claims * a_deductible
        b_total = b_premium_year + claims * b_deductible
        winner = "a" if a_total < b_total else "b"

        r = CaseResult(
            case_id="deductible_tradeoff",
            title="Deductible Tradeoff",
            vertical="insurance",
            tier=3,
            first_look="Plan A: $40/mo, $1,000 deductible  vs  Plan B: $65/mo, $250 deductible.",
            option_a_label="Plan A — $40/mo, $1,000 deductible",
            option_b_label="Plan B — $65/mo, $250 deductible",
            option_a_teaser="Cheaper every month · costs more when something breaks",
            option_b_teaser="Pricier every month · softer landing on a claim",
            bet_range=(480, 1780),
            bet_label="Place your bet — your total cost this year on Plan A?",
        )
        # Three rows so the realized-totals answer survives the Tier-3 cap (3 layers);
        # the claim count is folded into that row's label rather than standing alone.
        r.evidence = [
            ("Plan A", f"${a_premium_year} premium/yr · then ${a_deductible:,} per claim"),
            ("Plan B", f"${b_premium_year} premium/yr · then ${b_deductible} per claim"),
            (f"You file {claims} claim(s) → realized totals",
             f"A: ${a_premium_year} + {claims}×${a_deductible:,} = ${a_total:,}  ·  "
             f"B: ${b_premium_year} + {claims}×${b_deductible} = ${b_total:,}"),
        ]
        r.winner = winner
        r.actual_value = float(a_total)
        r.case_notes = ("Low deductible costs more monthly and less when something goes wrong. "
                        "That's not a trick — that's the whole product.")
        return r


register_vertical(Vertical(
    key="insurance",
    title="Insurance & Risk Transfer",
    tagline="You're not buying a thing. You're buying who eats the bad day.",
    min_tier=3,   # v8 §3.9 — Insurance & Risk Transfer is Tier 3+
    case_types=["skip_vs_cover", "deductible_tradeoff"],
))
