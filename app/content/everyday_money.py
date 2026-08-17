"""
VERTICAL — Everyday Money  (v8 §3.1 · Round_Scripts_All22.md, Subtopics 1-3, 5-6)

The baseline vertical: open from Tier 1, no theme, the curriculum's foundation
(Units 1-2). These are the "existing, unchanged" Cases that Granular_GDD.md
deliberately does NOT repeat (line 6-7 — they live in Round_Scripts_All22.md);
this module builds them from that canonical script, verbatim.

DETERMINISM NOTE — unlike the Creator Economy slice (every number rolled inside a
GDD range), these Cases are DETERMINISTIC: no random rolls (Build Note 3 — the base
game is deterministic apart from Subtopic 19). Do NOT add random rolls here.

TIER-SCALING (this session) — Everyday Money is the foundation and never fades from the
draw (see verticals.select_vertical), so its Cases must stay relevant across the whole
tier climb, not just Tier 1.

THE RULE that decides scale-vs-cap, learned from seeing both directions fail and succeed:

  * Cases about ABSTRACT FINANCIAL TERMS — fees, bonuses, interest rates, account
    balances — SCALE. There is no real-world ceiling on what a bank might offer or
    charge, so a $90 signup bonus at Tier 3 reads exactly as true as a $10 one at
    Tier 1. These are: Account Fees (fee & bonus) and Savings Type (placed balance).

  * Cases about REAL-WORLD-PRICED CONSUMER GOODS with a known, fixed price range —
    phone cases, gem bundles, mobile games — get case_max_tier CAPS instead. The
    item's real price ceiling does not move regardless of the player's wealth: no
    amount of net worth makes a phone case cost $180. These are: Currency Illusion
    ($9.99 gems), Free-to-Play ($4.99 app), and Need vs Want ($28 phone case) —
    all capped at case_max_tier=2, retiring once the player is clearly past that scale.

Scaling is DETERMINISTIC where it applies (a fixed figure per tier keyed off
self.target_tier, NOT a roll). TIER 1 REPRODUCES THE SCRIPT'S EXACT LOCKED FIGURES as
the anchor (−$134 net, $1,270 HYSA); higher tiers scale up from there, preserving each
scenario's shape and verdict. Rates/ratios never scale (4.5% APY, the 1,000-Gems
illusion) — only magnitudes.

NOTE — the foundation's high-tier floor share (20% of every draw at every tier) is
therefore carried by only TWO Cases at Tier 3+: Account Fees and Savings Type. That is
thin repetition-wise and is a known open item, not an oversight.

TIER-1 EVIDENCE CAP — Everyday Money is the first min_tier=1 vertical, so at Tier 1
apply_tier_difficulty() caps evidence to 2 layers. Each Case below keeps the
script's exact reveal ORDER but is arranged so the first two beats (plus
first_look) already contain enough to reason toward the bet answer; the 3rd beat
is the explicit "= answer" summary that only surfaces once the Case is drawn at a
higher tier. Tier 1's forgiving bet range (range_keep 1.0) absorbs the rest — this
is the two-axis design working as intended (fewer layers low, tighter range high).

Cases (Round_Scripts subtopic → case_type):
  S1  Currency Illusion — "1,000 Gems"      → currency_illusion  (pure reveal, tie)
  S2  Need vs Want      — "The Case Cover"  → need_vs_want       (no-shame: deception off)
  S3  Free-to-Play      — "Totally Free"    → free_to_play       (Chapter 1 boss)
  S5  Account Fees      — "The Bonus Trap"  → account_fees
  S6  Savings Type      — "The 0.01% Special" → savings_type     (Chapter 2 boss)

NOT built: Credit vs Debit (GDD_v8 §3.1's "plastic-twins" concept). It is not one
of the 22 scripted subtopics — no script exists in any doc — so per the standing
"build only what the docs support" rule it is intentionally omitted, not invented.
"""
from app.cases import CaseResult, CaseTemplate, register_case
from app.verticals import Vertical, register_vertical


@register_case
class CurrencyIllusionCase(CaseTemplate):
    """S1 — "1,000 Gems." Pure reveal: the pick (buy/skip) is never scored, so
    winner="tie" (renders "Case Notes Only"). The skill is the bet — calling what
    the thing you actually want costs in REAL dollars, which the in-game currency
    is designed to obscure."""
    case_type = "currency_illusion"
    # A real-world-priced consumer good: a $9.99 gem bundle is a Broke/Stable-scale lesson
    # and scaling it up reads as fake. Retire it past Tier 2 (foundation's high-tier floor
    # is carried by the two scaling Cases — Account Fees and Savings Type).
    case_max_tier = 2

    def generate(self) -> CaseResult:
        r = CaseResult(
            case_id="currency_illusion",
            title="1,000 Gems",
            vertical="everyday_money",
            tier=1,
            first_look='"1,000 GEMS — BEST VALUE" in flashy gold. The price, tiny in the corner: $9.99.',
            option_a_label="Buy the Gem bundle — $9.99",
            option_b_label="Skip it, keep the $9.99",
            option_a_teaser="1,000 Gems · 'best value' · feels like a lot in Gem-terms",
            option_b_teaser="$9.99 stays in your pocket · zero Gems",
            option_a_cost=9.99,   # buying the bundle actually costs $9.99 (Bug 1 gate)
            deception_eligible=False,   # no wrong pick here — buying is illusion, not error
            bet_range=(0, 9.99),
            bet_label="Place your bet — what does the skin you want ACTUALLY cost in real dollars?",
        )
        r.evidence = [
            ("The skin you want", "800 Gems — feels cheap in Gem-terms"),
            ("800 Gems in real money", "$7.99"),
            ("Left in your account", "200 Gems — not enough for anything"),
        ]
        r.winner = "tie"
        r.actual_value = 7.99
        r.case_notes = ("1,000 Gems sounds like a lot. $9.99 sounds like less. "
                        "That gap is the whole business model.")
        return r


@register_case
class NeedVsWantCase(CaseTemplate):
    """S2 — "The Case Cover." Needs vs wants. Keeping the cash wins on paper, but
    the script is explicit that picking the case earns a NO-SHAME badge, never a
    penalty — so deception_eligible is False (a bad pick can never cost cash).
    That's not just tone: CLAUDE.md's ethical line forbids penalizing spending
    choices for this audience. The bet is the "compounding tease" — deliberately
    tiny — that sets up Chapter 2's savings Cases."""
    case_type = "need_vs_want"
    # A phone case is a REAL-WORLD-PRICED CONSUMER GOOD: its price ceiling is set by the
    # market, not by the player's net worth. Scaling it produced a $180 phone case at Tier 3
    # and a $1,200 one at Tier 5 — nonsense, and exactly the failure Currency Illusion and
    # Free-to-Play were capped to avoid. So it is capped, not scaled (see module docstring).
    case_max_tier = 2

    # The locked Tier-1 script figures, verbatim — this Case no longer varies by tier.
    PRICE = 28
    GROWN = 29.26   # $28 in a HYSA for 1 year (locked script figure, not a computed rate)
    BET_HI = 32

    def generate(self) -> CaseResult:
        # Fixed figures: the scenario is the same at Tier 1 and Tier 2, the only tiers it
        # can now be drawn at. The streak-safety property still holds — the whole bet range
        # (28, 32) sits within 10% of 29.26, so every in-range bet scores nailed_it (deception
        # off, no-shame: a want is never a wrong answer, and this can never feed a bust streak).
        price, grown, hi = self.PRICE, self.GROWN, self.BET_HI
        r = CaseResult(
            case_id="need_vs_want",
            title="The Case Cover",
            vertical="everyday_money",
            tier=1,
            first_look=f"Your phone case is cracked but works (free) vs a glossy new ${price:g} case.",
            option_a_label=f"Buy the new ${price:g} case",
            option_b_label=f"Keep the ${price:g}",
            option_a_teaser="Glossy · new · 4.2★ · the crack is gone",
            option_b_teaser=f"${price:g} stays yours · the crack was only cosmetic",
            option_a_cost=float(price),   # the new case actually costs $price (Bug 1 gate)
            # NO SHAME — a want is not a wrong answer. deception_eligible=False blocks
            # the case_reward LOSS path so buying can never cost cash (CLAUDE.md's ethical
            # line: never penalize a spending choice for this audience). This intentionally
            # overrides the general "all binary Cases are deception_eligible=True" rule.
            # Streak-safety: loss_streak counts way_off+wrong-pick even when no cash is lost,
            # but this range sits entirely within 10% of the grown value (every bet scores
            # nailed_it), so the Case can never be way_off and never feeds a bust streak.
            deception_eligible=False,
            bet_range=(price, hi),
            bet_label=f"Place your bet — what does that ${price:g} grow to in a HYSA after 1 year?",
        )
        r.evidence = [
            ("Does the crack affect function?", "No — purely cosmetic"),
            ("New case reviews", "4.2★ · common complaint: 'peels after 2 months'"),
            (f"${price:g} kept in a HYSA for 1 year", f"${grown:.2f}"),
        ]
        r.winner = "b"   # keeping the cash wins on paper
        r.actual_value = grown
        r.case_notes = ("Nothing wrong with wanting nice things. "
                        "Just know which pile you're picking from.")
        return r


@register_case
class FreeToPlayCase(CaseTemplate):
    """S3 — "Totally Free" (Chapter 1 boss). The hidden cost of "free": the free
    game's power-up spend dwarfs the paid game's one-time price. Deterministic —
    paid version wins. Bet is the 12-month cost of the "free" game ($276), fully
    derivable from beat 1's $23/month, so it survives the Tier-1 2-layer cap."""
    case_type = "free_to_play"
    # A $4.99 app / $23-a-month power-up habit is a Broke/Stable-scale lesson; it doesn't
    # scale to Outlier wealth realistically. Retire past Tier 2 (like Currency Illusion).
    case_max_tier = 2

    def generate(self) -> CaseResult:
        r = CaseResult(
            case_id="free_to_play",
            title="Totally Free",
            vertical="everyday_money",
            tier=1,
            is_boss=True,
            first_look='"SkyDash: FREE" (huge banner) vs "SkyDash Pro: $4.99" (small price, no banner).',
            option_a_label="Download the FREE version",
            option_b_label="Buy the $4.99 version",
            option_a_teaser="$0 to download · huge 'FREE' banner",
            option_b_teaser="$4.99 once · no banner · no power-ups to buy",
            option_b_cost=4.99,   # the paid version actually costs $4.99 (Bug 1 gate)
            bet_range=(0, 350),
            bet_label="Place your bet — total 12-month cost of the 'free' game?",
        )
        r.evidence = [
            ("Free version average spend", "$23/month in power-ups"),
            ("Paid version", "$4.99. Forever. That's it."),
            ("12-month cost", "Free = $276  ·  Paid = $4.99"),
        ]
        r.winner = "b"   # paid version wins
        r.actual_value = 276.0
        r.case_notes = "Free to download. Not free to enjoy."
        return r


@register_case
class AccountFeesCase(CaseTemplate):
    """S5 — "The Bonus Trap." Banking fees: a $10 signup bonus is swallowed by a
    $12/mo fee, netting −$134 over a year, while the no-bonus credit union nets $0.
    The −$134 answer is derivable from first_look's $10 bonus + beat 1's $12/mo, so
    it survives the Tier-1 cap. The flashy-bonus option is the loser — real stakes."""
    case_type = "account_fees"
    pattern = "flashy_hides_worse_terms"   # sibling: savings_type (flashy $10 bonus hides the fee)
    # Bank scale by tier: a $12/mo fee & $10 bonus at Broke; a $300/mo premium/AUM-style
    # fee & a $600 "relationship bonus" at Outlier (sophistication ≠ safety — the fee
    # still beats the bonus, and by MORE in absolute terms as wealth rises). Tier 1 = the
    # locked script figures (bonus $10, fee $12/mo, net −$134). Dicts are tuned so the net
    # loss grows monotonically with tier — a −$134 sting at Broke, a −$3,000 one at Outlier
    # — so the lesson stays proportionate to net worth instead of shrinking to noise.
    FEE_BY_TIER   = {1: 12, 2: 20, 3: 45, 4: 110, 5: 300}
    BONUS_BY_TIER = {1: 10, 2: 30, 3: 90, 4: 250, 5: 600}

    def generate(self) -> CaseResult:
        t = self.target_tier or 1
        fee = self.FEE_BY_TIER.get(t, 12)
        bonus = self.BONUS_BY_TIER.get(t, 10)
        net = bonus - fee * 12                    # Tier 1: 10 − 144 = −134 (locked)
        r = CaseResult(
            case_id="account_fees",
            title="The Bonus Trap",
            vertical="everyday_money",
            tier=1,
            first_look=f'"GlitzBank: Sign up, get ${bonus} instantly!" vs plain "Riverside Credit Union", no bonus.',
            option_a_label=f"GlitzBank — ${bonus} signup bonus",
            option_b_label="Riverside Credit Union",
            option_a_teaser=f"${bonus} in your account today · flashy app",
            option_b_teaser="No bonus · plain · no monthly fee mentioned",
            bet_range=(round(net - fee * 6), round(bonus + fee)),
            bet_label="Place your bet — GlitzBank's balance after 1 year (the bonus minus fees)?",
        )
        r.evidence = [
            ("GlitzBank monthly fee", f"${fee}"),
            ("Riverside monthly fee", "$0"),
            ("1-year net", f"GlitzBank = −${abs(net)}  ·  Riverside = $0"),
        ]
        r.winner = "b"   # no-fee credit union wins
        r.actual_value = float(net)
        r.case_notes = "The bonus cost more than it paid."
        return r


@register_case
class SavingsTypeCase(CaseTemplate):
    """S6 — "The 0.01% Special" (Chapter 2 boss). HYSA vs standard savings on
    $1,000. The ugly, boring HYSA card wins by a lot — the signature "flashy ≠
    better" inversion. Bet is the 5-year HYSA value ($1,270); at Tier 1 only the
    rate and the 1-year figure show, so the player estimates the 5-year compounding
    into the forgiving Tier-1 range — exactly the intended low-tier experience."""
    case_type = "savings_type"
    pattern = "flashy_hides_worse_terms"   # sibling: account_fees (sleek app hides the 0.01% rate)
    # Placed sum by tier: $1,000 at Broke, $100,000 at Outlier. The RATES never scale —
    # 4.5% HYSA vs 0.01% standard is the fixed lesson. Tier 1 = the locked script figures.
    PLACED_BY_TIER = {1: 1000, 2: 2500, 3: 8000, 4: 30000, 5: 100000}

    def generate(self) -> CaseResult:
        t = self.target_tier or 1
        placed = self.PLACED_BY_TIER.get(t, 1000)
        # Tier 1 keeps the hand-authored script numbers verbatim ($1,046 / $1,270 aren't a
        # clean 4.5% compounding — they're the locked figures); higher tiers compute from
        # the placed balance at the same rates.
        if t == 1:
            hysa_1yr, hysa_5yr, std_1yr, std_5yr = 1046, 1270, 1000.10, 1000.50
        else:
            hysa_1yr = round(placed * 1.045)
            hysa_5yr = round(placed * 1.045 ** 5)
            std_1yr = round(placed * 1.0001, 2)
            std_5yr = round(placed * 1.0001 ** 5, 2)
        r = CaseResult(
            case_id="savings_type",
            title="The 0.01% Special",
            vertical="everyday_money",
            tier=1,
            is_boss=True,
            first_look=f'Ugly "Federal Reserve HYSA" card vs sleek gradient "Standard Saver" app. ${placed:,} to place.',
            option_a_label="Federal Reserve HYSA (the ugly one)",
            option_b_label="Standard Saver (the sleek one)",
            option_a_teaser="4.5% APY · boring font · plain card",
            option_b_teaser="0.01% APY · gradient · modern app",
            bet_range=(placed, round(placed * 1.30)),
            bet_label=f"Place your bet — what's the ${placed:,} worth in the HYSA after 5 years?",
        )
        r.evidence = [
            ("HYSA rate  vs  Standard rate", "4.5% APY  vs  0.01% APY"),
            ("After 1 year", f"HYSA = ${hysa_1yr:,}  ·  Standard = ${std_1yr:,.2f}"),
            ("After 5 years", f"HYSA = ${hysa_5yr:,}  ·  Standard = ${std_5yr:,.2f}"),
        ]
        r.winner = "a"   # HYSA wins — by a lot
        r.actual_value = float(hysa_5yr)
        r.case_notes = "Filed under: technically a savings account."
        return r


register_vertical(Vertical(
    key="everyday_money",
    title="Everyday Money",
    tagline="No theme. No hustle. Just the money in your pocket and where it goes.",
    min_tier=1,   # open from the start — the curriculum's foundation (crosswalk Part 6)
    # The foundation, not a theme: it owns the run's on-ramp and keeps a permanent
    # floor share of the draw at every tier (see verticals.select_vertical). This is
    # the one vertical that never fades out.
    foundation=True,
    case_types=["currency_illusion", "need_vs_want", "free_to_play",
                "account_fees", "savings_type"],
))
