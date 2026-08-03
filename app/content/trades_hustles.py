"""
VERTICAL — Trades & Hustles  (v8 §3.3 · Granular_GDD Part A, T1-T2)

Tier 2+ vertical. Only the two new-scripted Cases (Tool Investment, Apprentice vs
Solo) are wired here. T3 "Self-Employment Tax" and T4 "Hustle Pricing" are the
prior-GDD scripts that live in the missing Round_Scripts doc, so they are not
registered yet — the vertical launches with its two available Cases.
"""
import random

from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical


@register_case
class ToolInvestmentCase(CaseTemplate):
    """T1 — Tool Investment (Tier 2). Threshold variance: owning the tool wins if it
    lets you take enough extra jobs to clear the financing cost. Bet is the extra
    revenue owning generates this year."""
    case_type = "tool_investment"
    # Small-operator premise/scale (finance a $600 tool vs $35/job rentals) — a
    # trivial decision once Wealthy. Keep it through Comfortable, then retire.
    case_max_tier = 3

    def generate(self) -> CaseResult:
        financed_total = 654   # $600 financed 12mo @ 18% APR
        jobs_this_year = 20
        rental_per_job = 35
        rental_cost = jobs_this_year * rental_per_job   # $700

        extra_jobs = random.randint(2, 10)
        avg_job = 150
        extra_revenue = extra_jobs * avg_job
        winner = "a" if extra_jobs >= 5 else "b"   # a = finance/own, b = keep renting

        r = CaseResult(
            case_id="tool_investment",
            title="Tool Investment",
            vertical="trades_hustles",
            tier=2,
            first_look="Finance a $600 pressure washer (12mo, 18% APR)  vs  keep renting "
                       "equipment at $35/job.",
            option_a_label="Finance the $600 pressure washer",
            option_b_label="Keep renting equipment",
            option_a_teaser=f"~${financed_total} total · own it · take jobs rentals can't cover",
            option_b_teaser=f"${rental_per_job}/job · no debt · cash only",
            bet_range=(500, 1300),
            bet_label="Place your bet — total extra revenue from owning the tool this year?",
        )
        r.evidence = [
            ("Financed total cost over 12mo", f"${financed_total}"),
            ("Rental cost if you do 20 jobs this year", f"${rental_cost}"),
            ("Owning lets you take jobs rentals can't cover", "Realistic extra jobs: 4-8"),
            ("Extra revenue from those jobs at $150 avg", "$600-$1,200"),
        ]
        r.winner = winner
        r.actual_value = float(extra_revenue)
        r.case_notes = ("Debt for a tool that makes you money is a different animal than debt "
                        "for a tool that doesn't.")
        return r


@register_case
class ApprenticeVsSoloCase(CaseTemplate):
    """T2 — Apprentice vs Solo (Tier 2). Winner is 'tie' by design — the two paths
    aren't comparable on week-1 math alone. Bet is solo's realistic weekly income
    once you account for booking gaps."""
    case_type = "apprentice_vs_solo"
    # Beginner's-choice premise ("apprentice or go solo?") — nonsensical for a
    # player already past Stable. Retire it after Tier 2.
    case_max_tier = 2

    def generate(self) -> CaseResult:
        apprentice_weekly = 480   # $16/hr × 30 guaranteed hrs
        solo_rate = 35
        solo_hours = 25
        booking = round(random.uniform(0.40, 0.60), 2)   # rolled booking fraction
        solo_weekly = round(solo_rate * solo_hours * booking)

        r = CaseResult(
            case_id="apprentice_vs_solo",
            title="Apprentice vs Solo",
            vertical="trades_hustles",
            tier=2,
            first_look="Apprentice: $16/hr, steady, learn from a licensed pro  vs  Solo: "
                       "$35/hr average when you get jobs, no guarantee.",
            option_a_label="Take the apprenticeship",
            option_b_label="Go solo now",
            option_a_teaser="$16/hr · steady hours · licensed in 2 years",
            option_b_teaser="$35/hr · when you book · no floor under you",
            bet_range=(300, 500),
            bet_label="Place your bet — solo's realistic weekly income accounting for gaps?",
        )
        r.evidence = [
            ("Apprentice", f"30 hrs/week guaranteed = ${apprentice_weekly}/week reliable"),
            ("Solo booking rate (unlicensed beginner)", "40-60% of available weeks"),
            ("Solo weekly, accounting for gaps",
             f"${solo_rate} × {solo_hours}hrs × {booking:.2f} = ${solo_weekly}/week"),
            ("Apprentice payoff",
             "After 2 years: licensed, then go solo at a much higher realistic rate"),
        ]
        r.winner = "tie"
        r.actual_value = float(solo_weekly)
        r.case_notes = ("One path pays less now and more later. The other is the reverse. "
                        "Neither is wrong.")
        return r


register_vertical(Vertical(
    key="trades_hustles",
    title="Trades & Hustles",
    tagline="The tools cost money. So does not having them.",
    min_tier=2,   # v8 §3.3 — Trades & Hustles is Tier 2+
    case_types=["tool_investment", "apprentice_vs_solo"],
))
