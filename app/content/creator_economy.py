"""
VERTICAL — Creator Economy  (v8 §3.2 · Granular_GDD Part A, C1-C3)

The one content-complete slice built to prove the whole pipeline end to end.
Every number is rolled procedurally inside the GDD's stated bounds — no
scenario's figures are hardcoded.

Cases:
  C1 Sponsorship Offer  — binary, deterministic winner "a" (establishes the
                          pattern cleanly; the first Creator case never varies)
  C2 Algorithm Shock    — investigation-only; bounded uniform haircut (B.3),
                          NOT log-normal — algorithm changes are bad but bounded
  C3 Merch Drop Math    — binary, genuine variance on the rolled sell-through
  C4 Income Type        — binary, one-time sponsored post vs. evergreen ad
                          revenue; re-homed into Creator Economy (v8 §3.2). The
                          prior-GDD script lives in the missing Round_Scripts doc,
                          so this rebuilds the stated concept in the house pattern:
                          recurring income compounds over a horizon vs. a lump sum.
"""
import random

from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical


@register_case
class SponsorshipOfferCase(CaseTemplate):
    """C1 — Sponsorship Offer. Winner "a" always (GDD: first Creator case is
    deterministic, so the pattern lands before any tier deception subverts it)."""
    case_type = "sponsorship_offer"
    pattern = "vague_upside_vs_concrete_terms"   # sibling: nil_deal (concrete cash vs vague "potential")
    # $100-200 flat-fee-vs-"exposure" is a small-creator lesson; a Wealthy/Outlier
    # creator fields far bigger, real-contract deals. Retire after Comfortable.
    case_max_tier = 3

    def generate(self) -> CaseResult:
        flat_fee = random.randint(100, 200)
        exposure_retail = random.randint(20, 60)
        hours = 3
        flat_hourly = flat_fee / hours
        exposure_hourly = exposure_retail / hours   # retail value, not cash

        r = CaseResult(
            case_id="sponsorship_offer",
            title="Sponsorship Offer",
            vertical="creator_economy",
            tier=2,
            first_look='DM from "BrandCo Partnerships": "We love your content! '
                       'Partnership opportunity attached."',
            option_a_label=f"Take the flat ${flat_fee} fee",
            option_b_label="Take 'exposure only'",
            option_a_teaser=f"${flat_fee} cash · 1 post · paid within 7 days · contract attached",
            option_b_teaser=f"Free product (~${exposure_retail} retail) · 'huge audience potential!'",
            bet_range=(exposure_retail, flat_fee + 50),
            bet_label="Place your bet — what's the flat fee worth?",
        )
        r.evidence = [
            ("Flat fee deal", f"1 post · ${flat_fee} · paid within 7 days"),
            ("Exposure deal", f"Product worth ${exposure_retail} retail · 'huge potential'"),
            ("Effective hourly (3-hour post)",
             f"Flat ${flat_hourly:.2f}/hr  vs  Exposure ${exposure_hourly:.2f}/hr"),
        ]
        r.winner = "a"
        r.actual_value = float(flat_fee)
        r.case_notes = "'Exposure' doesn't pay your phone bill."
        return r


@register_case
class AlgorithmShockCase(CaseTemplate):
    """C2 — Algorithm Shock. Investigation-only. A bounded uniform(0.2, 0.5)
    haircut on a passive-income baseline (B.3 — deliberately NOT log-normal:
    platform changes are bad but bounded, unlike true tail risk)."""
    case_type = "algorithm_shock"

    def generate(self) -> CaseResult:
        baseline = random.randint(200, 500)
        # Round the multiplier to its 2-decimal display form ONCE, up front, then
        # derive both the scored value and the evidence formula from that same
        # number. If we scored on the raw multiplier but displayed a rounded one,
        # "baseline × 0.31 = 135" could disagree with what the reader computes
        # (441 × 0.31 → 137). One source of truth keeps the shown math honest.
        shock_multiplier = round(random.uniform(0.2, 0.5), 2)
        this_month = round(baseline * shock_multiplier)
        view_diff = round((1 - shock_multiplier) * 100)

        r = CaseResult(
            case_id="algorithm_shock",
            title="Algorithm Shock",
            vertical="creator_economy",
            tier=2,
            pick_type="investigation",
            deception_eligible=False,
            # Fair-bet fix: reveal the baseline AND that a shock hit up front, so the bet is
            # "how bad was it" (a real judgment from a real anchor), not "guess a number from
            # nothing." Only the exact multiplier stays hidden until the Evidence reveal.
            first_look=(f"Last month: ${baseline} in ad revenue — a stable baseline. This month "
                        f"the platform changed its recommendation algorithm and your views took a "
                        f"hit. Nobody warned you."),
            bet_range=(0, baseline),
            bet_label="Place your bet — where did THIS month's revenue land after the hit?",
        )
        r.evidence = [
            ("Platform changes the recommendation algorithm", "No warning given"),
            ("This month's views", f"−{view_diff}%"),
            ("This month's ad revenue", f"${baseline} × {shock_multiplier:.2f} = ${this_month}"),
            ("Warning · Appeal process", "None · None"),
        ]
        r.winner = "solved"
        r.actual_value = float(this_month)
        r.case_notes = "Passive income is only passive until the platform changes its mind."
        return r


@register_case
class MerchDropCase(CaseTemplate):
    """C3 — Merch Drop Math. Genuine variance: the winner turns on the rolled
    sell-through. GDD verdict rule verbatim — the lesson is dead-stock RISK, so
    the threshold is the stated 0.45, not the raw profit crossover."""
    case_type = "merch_drop"
    pattern = "headline_hides_real_net"   # sibling: landlord_math (big sticker profit vs real net after realistic leakage)

    def generate(self) -> CaseResult:
        price = 22
        sell_through = random.uniform(0.25, 0.60)

        cost_200, cost_50 = 1000, 400
        sold_200 = round(200 * sell_through)
        sold_50 = round(50 * sell_through)
        profit_200 = sold_200 * price - cost_200
        profit_50 = sold_50 * price - cost_50

        winner = "b" if sell_through > 0.45 else "a"   # a = 50-unit (safe), b = 200-unit (bulk)

        r = CaseResult(
            case_id="merch_drop",
            title="Merch Drop Math",
            vertical="creator_economy",
            tier=2,
            option_a_label="Print 50 shirts",
            option_b_label="Print 200 shirts",
            option_a_teaser="$8/unit · $400 total · low risk",
            option_b_teaser="$5/unit bulk discount · $1,000 total · big upside",
            bet_range=(0, 2000),   # covers the full rolled profit range (up to ~$1,640)
            bet_label="Place your bet — what's your profit at the 200-unit run?",
        )
        r.evidence = [
            ("50-unit run", "$400 cost · sell at $22 · up to $700 profit"),
            ("200-unit run", "$1,000 cost · sell at $22 · up to $3,400 profit"),
            ("Realistic sell-through (small creator)", "35-55% of stock"),
            (f"200-unit @ {sell_through * 100:.0f}% sold",
             f"{sold_200} sold · profit ${profit_200} · {200 - sold_200} dead stock"),
            (f"50-unit @ {sell_through * 100:.0f}% sold",
             f"{sold_50} sold · profit ${profit_50} · {50 - sold_50} unsold"),
        ]
        r.winner = winner
        r.actual_value = float(profit_200)
        r.case_notes = "Bulk discounts only help if you actually sell the bulk."
        return r


@register_case
class IncomeTypeCase(CaseTemplate):
    """C4 — Income Type. One-time sponsored post (lump now) vs. evergreen ad
    revenue (smaller, but recurring). Winner turns on the rolled monthly rate:
    over a 12-month horizon the recurring stream often — but not always — beats
    the lump, which is the whole lesson about income *type*, not size."""
    case_type = "income_type"
    pattern = "lump_vs_recurring_stream"   # sibling: signing_bonus (one-time lump vs a stream that adds up)

    def generate(self) -> CaseResult:
        horizon = 12   # months — a one-year horizon frames "recurring vs. once"
        one_time = random.randint(400, 800)
        monthly = random.randint(40, 90)
        evergreen_total = monthly * horizon   # exact ints — displayed math == scored

        # a = take the lump; b = build the recurring stream
        winner = "b" if evergreen_total > one_time else "a"

        r = CaseResult(
            case_id="income_type",
            title="Income Type",
            vertical="creator_economy",
            tier=2,
            first_look="Two ways to get paid for the same audience — one pays once, "
                       "one keeps paying. Which is worth more over a year?",
            option_a_label="Take the one-time sponsored post",
            option_b_label="Build evergreen ad revenue",
            option_a_teaser=f"${one_time} now · single payment · done",
            option_b_teaser=f"~${monthly}/month · keeps paying",
            bet_range=(0, 1200),
            bet_label="Place your bet — what's the evergreen revenue worth over 12 months?",
        )
        r.evidence = [
            ("One-time sponsored post", f"${one_time} · paid once"),
            ("Evergreen ad revenue", f"${monthly}/month · recurring"),
            (f"Evergreen over {horizon} months",
             f"${monthly} × {horizon} = ${evergreen_total}"),
            ("One-time  vs  evergreen (12-mo)", f"${one_time}  vs  ${evergreen_total}"),
        ]
        r.winner = winner
        r.actual_value = float(evergreen_total)
        r.case_notes = "One-time money spends once. Recurring money keeps showing up."
        return r


register_vertical(Vertical(
    key="creator_economy",
    title="Creator Economy",
    tagline="The follower count is real. The money is the question.",
    min_tier=2,   # v8 §3.2 — Creator Economy is Tier 2+
    case_types=["sponsorship_offer", "algorithm_shock", "merch_drop", "income_type"],
))
