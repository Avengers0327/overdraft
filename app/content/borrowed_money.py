"""
VERTICAL — Borrowed Money  (v8 §3.6 · Granular_GDD Part A, B1)

Tier 4+ vertical. Only the new-scripted Case (Cosigning Risk) is wired here. B2
"Minimum Payment", B3 "Interest Comparison", and B4 "Good vs Bad Debt" are the
prior-GDD scripts in the missing Round_Scripts doc, so the vertical launches with
its one available Case for now.

Note: Cosigning Risk stays deception_eligible (the default) on purpose — the
Steady Hand Trait (v8 §4) is defined to zero out deception specifically on
Borrowed Money Cases, which only means something if those Cases carry deception.
"""
import random

from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical


@register_case
class CosigningRiskCase(CaseTemplate):
    """B1 — Cosigning Risk (Tier 4). Decline wins on expected value. Bet is what YOU
    owe if the friend defaults at month 6 — the remaining balance, which most people
    badly underestimate."""
    case_type = "cosigning_risk"

    def generate(self) -> CaseResult:
        loan = 3000
        term = random.choice([36, 48, 60])           # months
        default_month = 6
        remaining = round(loan * (1 - default_month / term))

        r = CaseResult(
            case_id="cosigning_risk",
            title="Cosigning Risk",
            vertical="borrowed_money",
            tier=4,
            first_look=f"Your friend asks you to cosign a ${loan:,} car loan — their credit "
                       f"isn't good enough alone.",
            option_a_label="Cosign the loan",
            option_b_label="Decline",
            option_a_teaser="Help a friend out · 'they'll definitely pay it back'",
            option_b_teaser="Keep your name off it · the debt stays theirs",
            bet_range=(0, 3000),
            bet_label="Place your bet — what do YOU owe if they default at month 6?",
        )
        r.evidence = [
            ("Cosigning means",
             f"You are LEGALLY responsible for the full ${loan:,} if they miss payments"),
            ("Whose credit report", "It shows on YOURS, not just theirs"),
            ("National average", "25-38% of cosigned loans miss at least one payment"),
            (f"If they default at month {default_month} (of {term})",
             f"You owe the remaining ${remaining:,}"),
        ]
        r.winner = "b"   # decline wins on expected value
        r.actual_value = float(remaining)
        r.case_notes = "Cosigning isn't vouching for a friend. It's becoming their debt."
        return r


register_vertical(Vertical(
    key="borrowed_money",
    title="Borrowed Money",
    tagline="The signature is free. The liability isn't.",
    min_tier=4,   # v8 §3.6 — Borrowed Money is Tier 4+
    case_types=["cosigning_risk"],
))
