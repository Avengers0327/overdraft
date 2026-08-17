"""
VERTICAL — Trades & Hustles  (v8 §3.3 · Granular_GDD Part A, T1-T2)

Tier 2+ vertical. Tool Investment and Apprentice vs Solo are the two new-scripted
low-tier Cases (both retire by Tier 2-3). To keep the vertical from going SILENT at
Tier 4-5 — a real problem for the Entrepreneur archetype, whose major IS this vertical
while the shared Startup World minor is still ramping in — two Tier-4+ Cases were added:
Hire a Crew (scale by capacity) and Raise Your Rates (scale by price, rebuilding the
prior-GDD "Hustle Pricing" concept in the house pattern). T3 "Self-Employment Tax" is
still a missing Round_Scripts script and not registered.
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


@register_case
class HireCrewCase(CaseTemplate):
    """Tier 4-5 — Hire a Crew. Scaling a maxed-out solo operation by hiring a full-time
    helper: the fixed payroll only pays off if the extra capacity clears it. Threshold
    variance on the rolled overflow demand (echoes tool_investment one scale up — does the
    added capacity beat the fixed cost you took on?). Bet is the gross extra revenue the
    helper's capacity brings in this year. Keeps the vertical alive at the tiers its own
    archetype (Entrepreneur) leans on it."""
    case_type = "hire_crew"
    case_min_tier = 4   # a payroll decision is a Wealthy/Outlier-scale move, not an entry one

    def generate(self) -> CaseResult:
        payroll = 52000              # a full-time helper, loaded: wage + payroll tax + insurance
        avg_job = 300
        weeks = 48
        overflow_per_week = random.randint(2, 6)   # jobs/week you currently turn away
        extra_revenue = overflow_per_week * avg_job * weeks
        winner = "a" if extra_revenue > payroll else "b"   # a = hire, b = stay solo

        r = CaseResult(
            case_id="hire_crew",
            title="Hire a Crew",
            vertical="trades_hustles",
            tier=4,
            first_look=f"You're booked solid and turning work away. Hire a full-time helper "
                       f"(~${payroll:,}/yr loaded)  vs  stay solo and keep saying no.",
            option_a_label="Hire the helper",
            option_b_label="Stay solo",
            option_a_teaser=f"~${payroll:,}/yr fixed · take the overflow jobs you can't reach now",
            option_b_teaser="$0 payroll · but you're capped at your own two hands",
            bet_range=(20000, 100000),
            bet_label="Place your bet — extra revenue the helper's added capacity brings in this year?",
        )
        r.evidence = [
            ("Helper — fully loaded cost", f"${payroll:,}/yr (wage + payroll tax + insurance)"),
            ("Overflow you turn away now", f"~{overflow_per_week} jobs/week at ${avg_job} each"),
            ("Extra revenue the helper unlocks",
             f"{overflow_per_week} × ${avg_job} × {weeks} wks = ${extra_revenue:,}"),
            ("Does it clear payroll?",
             f"${extra_revenue:,} vs ${payroll:,} → {'clears it' if winner == 'a' else 'does NOT clear it'}"),
        ]
        r.winner = winner
        r.actual_value = float(extra_revenue)
        r.case_notes = ("A payroll the work can't cover is a faster way to go broke. One it "
                        "clears is the only way to grow past your own two hands.")
        return r


@register_case
class RaiseRatesCase(CaseTemplate):
    """Tier 4-5 — Raise Your Rates (rebuilds the prior-GDD 'Hustle Pricing' concept in the
    house pattern). Raising your rate loses price-sensitive clients but earns more per job —
    a win until churn outruns the higher price. Winner turns on the rolled churn. Bet is
    the new annual revenue after the raise."""
    case_type = "raise_rates"
    case_min_tier = 4

    def generate(self) -> CaseResult:
        jobs = 200
        old_rate = 400
        old_revenue = jobs * old_rate            # $80,000 book
        raise_pct = 30
        new_rate = round(old_rate * (1 + raise_pct / 100))   # $520
        churn = round(random.uniform(0.10, 0.40), 2)         # fraction of clients lost
        new_jobs = round(jobs * (1 - churn))
        new_revenue = new_jobs * new_rate
        winner = "a" if new_revenue > old_revenue else "b"   # a = raise, b = keep the rate

        r = CaseResult(
            case_id="raise_rates",
            title="Raise Your Rates",
            vertical="trades_hustles",
            tier=4,
            first_look=f"Your book is {jobs} jobs/yr at ${old_rate}. Raise to ${new_rate} "
                       f"(+{raise_pct}%) and lose some clients  vs  keep the rate and the full book.",
            option_a_label=f"Raise to ${new_rate}/job",
            option_b_label=f"Keep ${old_rate}/job",
            option_a_teaser=f"+{raise_pct}%/job · but price-sensitive clients walk",
            option_b_teaser=f"${old_revenue:,}/yr · full book · leaving money on the table?",
            bet_range=(50000, 110000),
            bet_label="Place your bet — your new annual revenue after the raise?",
        )
        r.evidence = [
            ("Current book", f"{jobs} jobs × ${old_rate} = ${old_revenue:,}/yr"),
            ("New rate", f"${new_rate}/job (+{raise_pct}%)"),
            ("Clients lost to the raise", f"{round(churn * 100)}% → {new_jobs} jobs remain"),
            ("New revenue vs old",
             f"{new_jobs} × ${new_rate} = ${new_revenue:,}  vs  ${old_revenue:,}"),
        ]
        r.winner = winner
        r.actual_value = float(new_revenue)
        r.case_notes = ("Raising prices isn't greed — it's a test of what the work is worth. "
                        "The skill is knowing where more-per-job stops beating more clients.")
        return r


register_vertical(Vertical(
    key="trades_hustles",
    title="Trades & Hustles",
    tagline="The tools cost money. So does not having them.",
    min_tier=2,   # v8 §3.3 — Trades & Hustles is Tier 2+
    case_types=["tool_investment", "apprentice_vs_solo", "hire_crew", "raise_rates"],
))
