"""
VERTICAL — Sports & NIL  (v8 §3.11 · Granular_GDD Part A, N1-N2)

Tier 3+ vertical, content-complete. High cultural relevance for the 10-15
audience. N1 teaches contract terms / exclusivity traps; N2 teaches present-value
intuition without ever naming it.
"""
import random

from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical


@register_case
class NILDealCase(CaseTemplate):
    """N1 — The NIL Deal (Tier 3). Deterministic: the local deal wins. The buried
    12-month exclusivity clause on the 'bigger brand' offer is the whole lesson."""
    case_type = "nil_deal"
    pattern = "vague_upside_vs_concrete_terms"   # sibling: sponsorship_offer (concrete terms vs vague "potential" + exclusivity catch)
    # $200-600 first-NIL-deal framing suits a rising athlete; the numbers stop
    # making sense at Outlier net worth. Keep through Wealthy, retire at Tier 5.
    case_max_tier = 4

    def generate(self) -> CaseResult:
        local_cash = random.randint(400, 600)
        gear = random.randint(100, 200)
        local_total = local_cash + gear
        national_cash = random.randint(150, 250)

        r = CaseResult(
            case_id="nil_deal",
            title="The NIL Deal",
            vertical="sports_nil",
            tier=3,
            first_look=f"Local store: ${local_cash} + free gear for 3 posts  vs  National brand: "
                       f"${national_cash} for 3 posts + 'potential for more if it goes well'.",
            option_a_label="Sign with the local store",
            option_b_label="Sign with the national brand",
            option_a_teaser=f"${local_cash} + gear · exact terms · exact pay date",
            option_b_teaser=f"${national_cash} now · big name · 'potential for more'",
            bet_range=(200, 700),
            bet_label="Place your bet — total real value of the local deal?",
        )
        r.evidence = [
            ("Local deal", f"Exact posts, exact pay date · ${local_cash} + ~${gear} gear = ${local_total}"),
            ("National deal", "No written contract · 'potential for more' is undefined"),
            ("Fine print", "12-month EXCLUSIVITY — no other sponsorships if you sign"),
            ("What exclusivity costs",
             f"Turning down every other deal for a year, for a guaranteed ${national_cash}"),
        ]
        r.winner = "a"   # local deal wins, deterministic
        r.actual_value = float(local_total)
        r.case_notes = "'Potential for more' with a 12-month exclusivity clause is a trap with a bow on it."
        return r


@register_case
class SigningBonusCase(CaseTemplate):
    """N2 — Signing Bonus Math (Tier 3). Winner is 'tie': the lump is bigger on paper
    per year, but the monthly plan (invested as received) can pull ahead — the real
    variable is behavioral, whether you invest or spend it. Bet is the monthly plan's
    dollar-cost-averaged value after a year. Rate is a whole percent so the displayed
    growth reproduces exactly."""
    case_type = "signing_bonus"
    pattern = "lump_vs_recurring_stream"   # sibling: income_type (lump now vs a smaller stream that can win over time)

    def generate(self) -> CaseResult:
        lump = 10000
        monthly = 1000
        months = 12
        monthly_total = monthly * months   # $12,000 nominal

        rate_pct = random.randint(6, 8)
        annual_rate = rate_pct / 100
        m_rate = annual_rate / 12

        lump_fv = round(lump * (1 + annual_rate))
        # FV of an ordinary annuity: contribute `monthly` at each period-end for 12 mo.
        dca_fv = round(monthly * (((1 + m_rate) ** months - 1) / m_rate))

        r = CaseResult(
            case_id="signing_bonus",
            title="Signing Bonus Math",
            vertical="sports_nil",
            tier=3,
            first_look=f"${lump:,} signing bonus paid today  vs  ${monthly:,}/month for "
                       f"{months} months (${monthly_total:,} total).",
            option_a_label=f"Take the ${lump:,} lump sum today",
            option_b_label=f"Take ${monthly:,}/month for a year",
            option_a_teaser=f"${lump:,} now · invest it all today",
            option_b_teaser=f"${monthly_total:,} total · arrives a piece at a time",
            bet_range=(9500, 12500),
            bet_label="Place your bet — total value of the monthly plan after investing each payment?",
        )
        # DCA row (the bet's answer) is front-loaded to index 2 so it survives the
        # Tier-3 evidence cap (3 layers) — this Case's min tier.
        r.evidence = [
            ("Lump sum today", f"${lump:,} · immediately investable"),
            ("Monthly plan", f"${monthly:,}/mo · ${monthly_total:,} nominal over a year"),
            ("Monthly invested as received (dollar-cost averaged)",
             f"${monthly:,}/mo at {rate_pct}%/yr → ${dca_fv:,} after 1 year"),
            ("Lump invested",
             f"${lump:,} at {rate_pct}%/yr → ${lump_fv:,} after 1 year"),
            ("The catch",
             "The 'smaller' monthly number can beat the lump IF you actually invest it — "
             "and loses if you just spend it"),
        ]
        r.winner = "tie"
        r.actual_value = float(dca_fv)
        r.case_notes = ("The bigger number wins on paper. What you actually do with either one "
                        "is the real variable.")
        return r


register_vertical(Vertical(
    key="sports_nil",
    title="Sports & NIL",
    tagline="The offer with the bigger logo isn't always the bigger offer.",
    min_tier=3,   # v8 §3.11 — Sports & NIL is Tier 3+
    case_types=["nil_deal", "signing_bonus"],
))
