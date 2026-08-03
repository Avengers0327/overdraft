"""
VERTICAL — Everyday Money  (v8 §3.1 · Round_Scripts_All22.md, Subtopics 1-3, 5-6)

The baseline vertical: open from Tier 1, no theme, the curriculum's foundation
(Units 1-2). These are the "existing, unchanged" Cases that Granular_GDD.md
deliberately does NOT repeat (line 6-7 — they live in Round_Scripts_All22.md);
this module builds them from that canonical script, verbatim.

DETERMINISM NOTE — unlike the Creator Economy slice (every number rolled inside a
GDD range), these Cases use the script's EXACT fixed figures. That is on purpose:
Round_Scripts writes them as deterministic teaching Cases with fixed verdicts
("PAID VERSION WINS", "HYSA WINS", the −$134 net), and Build Note 3 confirms the
base game is deterministic apart from Subtopic 19. Do NOT "fix" these by adding
random rolls — the fixed numbers ARE the locked design.

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

    def generate(self) -> CaseResult:
        r = CaseResult(
            case_id="need_vs_want",
            title="The Case Cover",
            vertical="everyday_money",
            tier=1,
            first_look="Your phone case is cracked but works (free) vs a glossy new $28 case.",
            option_a_label="Buy the new $28 case",
            option_b_label="Keep the $28",
            option_a_teaser="Glossy · new · 4.2★ · the crack is gone",
            option_b_teaser="$28 stays yours · the crack was only cosmetic",
            # NO SHAME — a want is not a wrong answer. deception_eligible=False blocks
            # the case_reward LOSS path so buying can never cost cash (CLAUDE.md's ethical
            # line: never penalize a spending choice for this audience). This intentionally
            # overrides the general "all binary Cases are deception_eligible=True" rule.
            # Streak-safety: loss_streak counts way_off+wrong-pick even when no cash is lost,
            # but this range sits entirely within 10% of 29.26 (every bet scores nailed_it),
            # so the Case can never be way_off and never feeds a bust streak. Keep it tight.
            deception_eligible=False,
            bet_range=(28, 32),
            bet_label="Place your bet — what does that $28 grow to in a HYSA after 1 year?",
        )
        r.evidence = [
            ("Does the crack affect function?", "No — purely cosmetic"),
            ("New case reviews", "4.2★ · common complaint: 'peels after 2 months'"),
            ("$28 kept in a HYSA for 1 year", "$29.26"),
        ]
        r.winner = "b"   # keeping the cash wins on paper
        r.actual_value = 29.26
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

    def generate(self) -> CaseResult:
        r = CaseResult(
            case_id="account_fees",
            title="The Bonus Trap",
            vertical="everyday_money",
            tier=1,
            first_look='"GlitzBank: Sign up, get $10 instantly!" vs plain "Riverside Credit Union", no bonus.',
            option_a_label="GlitzBank — $10 signup bonus",
            option_b_label="Riverside Credit Union",
            option_a_teaser="$10 in your account today · flashy app",
            option_b_teaser="No bonus · plain · no monthly fee mentioned",
            bet_range=(-200, 50),
            bet_label="Place your bet — GlitzBank's balance after 1 year (the $10 bonus minus fees)?",
        )
        r.evidence = [
            ("GlitzBank monthly fee", "$12"),
            ("Riverside monthly fee", "$0"),
            ("1-year net", "GlitzBank = −$134  ·  Riverside = $0"),
        ]
        r.winner = "b"   # no-fee credit union wins
        r.actual_value = -134.0
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

    def generate(self) -> CaseResult:
        r = CaseResult(
            case_id="savings_type",
            title="The 0.01% Special",
            vertical="everyday_money",
            tier=1,
            is_boss=True,
            first_look='Ugly "Federal Reserve HYSA" card vs sleek gradient "Standard Saver" app. $1,000 to place.',
            option_a_label="Federal Reserve HYSA (the ugly one)",
            option_b_label="Standard Saver (the sleek one)",
            option_a_teaser="4.5% APY · boring font · plain card",
            option_b_teaser="0.01% APY · gradient · modern app",
            bet_range=(1000, 1300),
            bet_label="Place your bet — what's the $1,000 worth in the HYSA after 5 years?",
        )
        r.evidence = [
            ("HYSA rate  vs  Standard rate", "4.5% APY  vs  0.01% APY"),
            ("After 1 year", "HYSA = $1,046  ·  Standard = $1,000.10"),
            ("After 5 years", "HYSA = $1,270  ·  Standard = $1,000.50"),
        ]
        r.winner = "a"   # HYSA wins — by a lot
        r.actual_value = 1270.0
        r.case_notes = "Filed under: technically a savings account."
        return r


register_vertical(Vertical(
    key="everyday_money",
    title="Everyday Money",
    tagline="No theme. No hustle. Just the money in your pocket and where it goes.",
    min_tier=1,   # open from the start — the curriculum's foundation (crosswalk Part 6)
    case_types=["currency_illusion", "need_vs_want", "free_to_play",
                "account_fees", "savings_type"],
))
