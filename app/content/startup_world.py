"""
VERTICAL — Startup World  (v8 §3.10 · Granular_GDD Part A, S2-S3)

Tier 5 vertical. S1 "The Pitch" is the flagship Outlier Event (log-normal, lives
in outliers.py — not built yet), so it is intentionally not registered here. S2
and S3 are the two regular Tier-5 Cases and are content-complete.

S2 uses a log-normal outcome directly (random.lognormvariate) — that's a plain
distribution roll, distinct from the Outlier Event *replacement* mechanic.
"""
import random

from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical

# Balance knob (not fixed by the GDD, which gives mu/sigma but not the base the
# multiplier scales): tuned so the guaranteed-salary path wins most runs — matching
# the "~65-75% failure" narrative — with a fat tail up to the stated ~$600k success.
EQUITY_BASE = 75000
EQUITY_CAP = 600000


@register_case
class EquityVsSalaryCase(CaseTemplate):
    """S2 — Equity vs Salary (Tier 5). Log-normal tail (mu=-0.3, sigma=1.3): most
    runs the equity is worth less than the guaranteed salary gap, rarely it's huge.
    Bet is this run's rolled equity value."""
    case_type = "equity_vs_salary"

    def generate(self) -> CaseResult:
        years = 4
        startup_salary = 45000
        corporate_salary = 75000
        salary_gap = (corporate_salary - startup_salary) * years   # $120,000 guaranteed

        multiplier = random.lognormvariate(-0.3, 1.3)
        equity_value = min(round(EQUITY_BASE * multiplier), EQUITY_CAP)

        # a = startup (equity), b = corporate (guaranteed). Equity has to clear the
        # guaranteed salary gap to have been the better call.
        winner = "a" if equity_value > salary_gap else "b"

        r = CaseResult(
            case_id="equity_vs_salary",
            title="Equity vs Salary",
            vertical="startup_world",
            tier=5,
            first_look=f"Startup: ${startup_salary:,} salary + 0.5% equity  vs  Corporate: "
                       f"${corporate_salary:,} salary, no equity. Which offer?",
            option_a_label="Join the startup (lower pay + equity)",
            option_b_label="Take the corporate job (guaranteed)",
            option_a_teaser="Less cash now · a lottery ticket on 0.5%",
            option_b_teaser=f"${corporate_salary:,}/yr · guaranteed · no upside past it",
            bet_range=(0, 600000),
            bet_label="Place your bet — what's your equity worth in 4 years?",
        )
        r.evidence = [
            ("Salary gap over 4 years", f"Corporate pays ${salary_gap:,} more, guaranteed"),
            ("Startup failure rate within 4 years", "~65-75% (cited range, not a scare number)"),
            ("IF it succeeds at a $200M valuation",
             "Your 0.5% (diluted to ~0.3%) ≈ $600,000"),
            ("This run's rolled outcome", f"Your equity = ${equity_value:,}"),
        ]
        r.winner = winner
        r.actual_value = float(equity_value)
        r.case_notes = ("This is the story everyone tells. It's true. It's also why it gets told — "
                        "because it's rare." if winner == "a" else
                        "This is what happens most of the time. The math still says take the "
                        "guaranteed money unless you can survive the other outcome.")
        return r


@register_case
class BurnRateCase(CaseTemplate):
    """S3 — Burn Rate (Tier 5). Investigation-only: runway as a countdown. Bet is
    months of runway remaining, one decimal."""
    case_type = "burn_rate"

    def generate(self) -> CaseResult:
        cash = random.randint(60000, 100000)
        burn = random.randint(8000, 15000)
        runway = cash / burn

        cut_burn = round(burn * 0.6)
        ext_runway = cash / cut_burn

        r = CaseResult(
            case_id="burn_rate",
            title="Burn Rate",
            vertical="startup_world",
            tier=5,
            pick_type="investigation",
            deception_eligible=False,
            first_look=f"Startup has ${cash:,} in the bank. Spending ${burn:,}/month.",
            bet_range=(4, 12),
            bet_label="Place your bet — months of runway remaining (one decimal)?",
        )
        r.evidence = [
            ("Current burn rate", f"${burn:,}/month"),
            ("Runway at current burn", f"${cash:,} / ${burn:,} = {runway:.1f} months"),
            ("If burn is cut to $%s/mo" % f"{cut_burn:,}",
             f"Runway extends to {ext_runway:.1f} months, but growth slows"),
            ("The real founders' choice",
             "Grow fast and risk zero, or survive longer and risk moving too slow to matter"),
        ]
        r.winner = "solved"
        r.actual_value = round(runway, 1)
        r.case_notes = "Runway isn't a metaphor. It's a countdown with a real zero at the end."
        return r


register_vertical(Vertical(
    key="startup_world",
    title="Startup World",
    tagline="Most of the time the boring money was right. Most.",
    min_tier=5,   # v8 §3.10 — Startup World is Tier 5 only
    case_types=["equity_vs_salary", "burn_rate"],
))
