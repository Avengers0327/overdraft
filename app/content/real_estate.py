"""
VERTICAL — Real Estate & Assets  (v8 §3.8 · Granular_GDD Part A, R1-R3)

Tier 4+ vertical. All three Cases are new-scripted in the Granular GDD, so this
vertical is content-complete. Every figure is rolled inside the GDD's stated
bounds; displayed formulas are derived from the same rounded numbers that feed
actual_value, so the shown math always agrees with what gets scored.
"""
import random

from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical


@register_case
class RentVsBuyCase(CaseTemplate):
    """R1 — Rent vs Buy (Tier 4). Genuinely close; the winner turns on the rolled
    annual appreciation rate. Bet is the (deterministic) 5-year cost of buying."""
    case_type = "rent_vs_buy"

    def generate(self) -> CaseResult:
        months = 60   # 5-year horizon
        rent_mo = random.randint(1300, 1500)
        mortgage_mo = random.randint(1500, 1700)
        maint_mo = random.randint(200, 300)

        rent_5yr = rent_mo * months
        buy_5yr = (mortgage_mo + maint_mo) * months

        appreciation = round(random.uniform(0.010, 0.045), 3)   # rolled per-year rate
        # a = rent, b = buy. Buying is a bet on appreciation clearing the bar.
        winner = "b" if appreciation > 0.025 else "a"

        down = random.randint(30000, 50000)
        opp_cost = round(down * (1.07 ** 5))   # down payment invested at 7% instead

        r = CaseResult(
            case_id="rent_vs_buy",
            title="Rent vs Buy",
            vertical="real_estate",
            tier=4,
            first_look=f"Rent: ${rent_mo:,}/mo, no maintenance  vs  Buy: ${mortgage_mo:,}/mo "
                       f"mortgage + ~${maint_mo}/mo upkeep. Five-year horizon.",
            option_a_label="Rent",
            option_b_label="Buy",
            option_a_teaser=f"${rent_mo:,}/mo · no upkeep · walk away anytime",
            option_b_teaser=f"${mortgage_mo:,}/mo + ${maint_mo}/mo upkeep · build equity",
            bet_range=(60000, 130000),
            bet_label="Place your bet — total 5-year cost of buying?",
        )
        r.evidence = [
            ("5-year rent total", f"${rent_5yr:,} · zero equity built"),
            ("5-year buy total (mortgage + maintenance)", f"${buy_5yr:,}"),
            ("Appreciation this scenario",
             f"{appreciation * 100:.1f}%/yr — equity is a bet on this number"),
            ("Down payment opportunity cost",
             f"${down:,} invested at 7%/yr → ${opp_cost:,} after 5 yrs"),
        ]
        r.winner = winner
        r.actual_value = float(buy_5yr)
        r.case_notes = "Buying isn't always better. It's a bet on appreciation, same as any other."
        return r


@register_case
class DepreciatingVsAppreciatingCase(CaseTemplate):
    """R2 — Depreciating vs Appreciating (Tier 4). Deterministic on the value
    question (the fund always out-values the car), non-judgmental on the tradeoff.
    Bet is the car's year-5 value. Percentages are whole-number so the displayed
    'X% of $P = $V' reproduces exactly under a reader's own arithmetic."""
    case_type = "asset_class"

    def generate(self) -> CaseResult:
        price = random.choice([18000, 20000, 22000])
        car_retain_pct = random.randint(35, 45)     # % of price retained at year 5
        fund_growth_pct = random.randint(130, 160)  # % of initial at year 5

        car_val5 = round(price * car_retain_pct / 100)
        fund_val5 = round(price * fund_growth_pct / 100)

        r = CaseResult(
            case_id="asset_class",
            title="Depreciating vs Appreciating",
            vertical="real_estate",
            tier=4,
            first_look=f"${price:,} into a new car (loan)  vs  ${price:,} into a real "
                       f"estate investment fund. Which asset class?",
            option_a_label="Buy the car",
            option_b_label="Buy into the REIT fund",
            option_a_teaser="A tool you use every day · loses value over time",
            option_b_teaser="A store of value · you never touch it · grows over time",
            bet_range=(6000, 32000),
            bet_label="Place your bet — the car's value at year 5?",
        )
        r.evidence = [
            ("Car value at year 5",
             f"~{car_retain_pct}% of ${price:,} = ${car_val5:,}"),
            ("REIT fund at year 5 (historical avg)",
             f"~{fund_growth_pct}% of ${price:,} = ${fund_val5:,}"),
            ("Car's real cost of ownership", "Plus gas, insurance, repairs — higher still"),
            ("Neither is 'wrong'", "One's a daily tool, one's a store of value"),
        ]
        r.winner = "b"   # fund wins on pure value, always
        r.actual_value = float(car_val5)
        r.case_notes = ("One of these you drive to work. The other you never see. "
                        "Know which job each one is doing.")
        return r


@register_case
class LandlordMathCase(CaseTemplate):
    """R3 — Landlord Math (Tier 5). Investigation-only reveal: the gap between the
    headline gross 'profit' and the real net after tax, maintenance, and vacancy IS
    the lesson. Structured so net is always well below gross — sometimes positive,
    sometimes negative."""
    case_type = "landlord_math"
    # GDD marks R3 as Tier 5; the vertical opens at Tier 4, so pin this Case to
    # Tier 5 — buying a rental property is an Outlier-tier move, not a Wealthy one.
    case_min_tier = 5

    def generate(self) -> CaseResult:
        rent = random.randint(1700, 2000)
        mortgage = random.randint(1100, 1300)
        gross = rent - mortgage

        tax_ins = random.randint(250, 320)
        maint = random.randint(195, 230)                       # ~1% of property value / yr
        vacancy = round(rent * random.uniform(0.05, 0.08))     # 5-8% of the year unrented
        net = gross - tax_ins - maint - vacancy

        r = CaseResult(
            case_id="landlord_math",
            title="Landlord Math",
            vertical="real_estate",
            tier=5,
            pick_type="investigation",
            deception_eligible=False,
            first_look=f"Buy a rental. Rent collected: ${rent:,}/mo. Mortgage: "
                       f"${mortgage:,}/mo. Looks like ${gross}/mo profit!",
            bet_range=(-200, 600),
            bet_label="Place your bet — real monthly net, after everything?",
        )
        # Four rows on purpose: the tier-5 evidence cap is 4 layers, so the net
        # reveal (the whole lesson) must fit inside four — tax + insurance +
        # maintenance are folded into one "fixed costs" line to make room for it.
        fixed_costs = tax_ins + maint
        net_str = f"-${abs(net)}" if net < 0 else f"${net}"   # "-$7", not "$-7"
        r.evidence = [
            ("Gross monthly 'profit'", f"${gross}"),
            ("Tax + insurance + maintenance reserve", f"−${fixed_costs}/mo"),
            ("Vacancy (5-8% of the year unrented)", f"−${vacancy}/mo amortized"),
            ("REAL net monthly cash flow",
             f"${gross} − ${fixed_costs} − ${vacancy} = {net_str}/mo"),
        ]
        r.winner = "solved"
        r.actual_value = float(net)
        r.case_notes = ("$%d on paper. Filed under: ask about the other three numbers "
                        "before you believe the first one." % gross)
        return r


register_vertical(Vertical(
    key="real_estate",
    title="Real Estate & Assets",
    tagline="The headline number is never the real number.",
    min_tier=4,   # v8 §3.8 — Real Estate & Assets is Tier 4+
    case_types=["rent_vs_buy", "asset_class", "landlord_math"],
))
