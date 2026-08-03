# GAME DESIGN DOCUMENT v8 — FULLY FLESHED
## Codename: OVERDRAFT
*The complete spec. Every system, every vertical, worked examples at every tier.*

---

## TABLE OF CONTENTS
1. Core Loop (unchanged, restated for completeness)
2. Net Worth Tiers — full difficulty curve with worked examples
3. The Open Vertical System — 11 verticals, fully detailed
4. Traits — reintegrated, now interact with Verticals and Tiers
5. Outlier Events — full catalog
6. Complete Architecture & Data Model
7. Full Curriculum Crosswalk (Vertical × Tier × Subtopic)
8. Build Sequencing

---

## 1. CORE LOOP

```
DEAL -> YOUR CALL (pick A/B) -> PLACE YOUR BET (slider) -> EVIDENCE (staged reveal) -> VERDICT -> CASE NOTES
```

Unchanged from prior versions. Everything below modifies *what* generates inside this loop, never the loop's shape — the shape is proven, don't touch it.

---

## 2. NET WORTH TIERS — FULL DIFFICULTY CURVE

### 2.1 The five tiers, with texture

**Tier 1 — Broke ($0-$250)**
Feel: everything is small stakes, forgiving, exploratory. Wide bet ranges. Deception is rare and telegraphed. This tier exists to teach the *interface* (how a Case works) more than to challenge.

**Tier 2 — Stable ($250-$1,000)**
Feel: first real trade-offs. Fees start to bite. Ranges tighten noticeably. Deception appears but the flashy option is still usually honest — you're building trust in the pattern before it gets subverted.

**Tier 3 — Comfortable ($1,000-$5,000)**
Feel: the game starts lying to you on purpose, roughly 1-in-3 Cases. This is the tier where "just pick the ugly one" stops working as a heuristic, which is the actual skill floor of the whole game.

**Tier 4 — Wealthy ($5,000-$25,000)**
Feel: real debt, real interest, real consequence sizes. A bad Verdict here can cost hundreds of in-game dollars, not tens. Evidence layers reach 4 — genuinely harder to hold in your head.

**Tier 5 — Outlier ($25,000+)**
Feel: rare air. Deception is common (roughly half of Cases have a layered trap). Outlier Events become possible. This tier should feel like the stakes finally match how it feels to actually have money — more to lose, more interesting ways to lose it.

### 2.2 Worked example: the SAME Case concept at every tier

To make the difficulty curve concrete, here's "Account Fees" (a Case type that exists at multiple tiers with scaled numbers) shown at each tier:

**Tier 1 version — "Piggy Bank Bonus"**
- Amounts: $10 signup bonus, $2/mo fee, $50 starting balance
- Bet range: full $30 spread (very forgiving)
- Evidence layers: 2 (fee, 1-year total)
- Deception: none — GlitzBank is honestly worse, no hidden twist

**Tier 3 version — "The Bonus Trap"** *(as originally designed)*
- Amounts: $5-25 bonus, $6-15/mo fee, $500 balance
- Bet range: tightened ~20%
- Evidence layers: 3 (fee, comparison, 1yr net)
- Deception: sometimes the bonus account wins if the fee is low enough — the player can no longer assume "flashy = bad"

**Tier 5 version — "The Private Banking Pitch"**
- Amounts: $500 "relationship bonus," $45/mo "wealth management fee," $15,000 balance, PLUS a hidden AUM (assets-under-management) percentage fee revealed only in the final Evidence beat
- Bet range: tight — real precision required
- Evidence layers: 4 (bonus, monthly fee, AUM %, 1yr total inclusive of AUM drag)
- Deception: high — the pitch is dressed in legitimacy language ("exclusive," "relationship manager") specifically because that's how real high-net-worth fee traps work

This shows the design principle clearly: **tiers don't just change numbers, they change what's being taught.** Tier 1 teaches "read the fee." Tier 5 teaches "sophistication is not the same as safety" — a materially more advanced lesson, using the same underlying Case skeleton.

### 2.3 Difficulty profile table (complete)

```python
TIER_DIFFICULTY = {
    1: {"name": "Broke",       "cash_range": (0, 250),
        "range_tightness": 0.45, "evidence_layers": 2, "deception_rate": 0.0},
    2: {"name": "Stable",      "cash_range": (250, 1000),
        "range_tightness": 0.60, "evidence_layers": 3, "deception_rate": 0.10},
    3: {"name": "Comfortable", "cash_range": (1000, 5000),
        "range_tightness": 0.75, "evidence_layers": 3, "deception_rate": 0.33},
    4: {"name": "Wealthy",     "cash_range": (5000, 25000),
        "range_tightness": 0.88, "evidence_layers": 4, "deception_rate": 0.40},
    5: {"name": "Outlier",     "cash_range": (25000, None),
        "range_tightness": 1.0,  "evidence_layers": 4, "deception_rate": 0.50},
}
```

`deception_rate` = probability that the visually "worse" option actually wins. At Tier 1 this is 0 (never lies). By Tier 5 it's a coin flip — true unpredictability, which is the honest end-state: at real wealth levels, sophistication of presentation genuinely stops correlating with quality of the deal.

---

## 3. THE OPEN VERTICAL SYSTEM — FULLY DETAILED

Expanded from 7 to 11 launch verticals, each with concrete Case concepts (not just names) so this is buildable, not just categorized.

### 3.1 Everyday Money *(Tier 1+, no theme — the baseline)*
- **Currency Illusion** — Gem bundles, in-game currency obfuscation
- **Need vs Want** — phone cases, small discretionary buys
- **Free-to-Play** — hidden costs of "free" apps/games
- **Account Fees** — the bonus-trap mechanic, scales through all 5 tiers per Section 2.2
- **Savings Type** — HYSA vs standard savings, the "0.01% Special"
- **Credit vs Debit** — the plastic-twins mechanic

### 3.2 Creator Economy *(Tier 2+)*
- **Sponsorship Offer** *(new)* — a brand DM arrives; real deals have contracts and clear terms, fake ones are vague and urgent. Numbers: flat fee vs. "exposure" offers, revealing real effective hourly rate
- **Algorithm Shock** *(new)* — a creator's monthly ad revenue swings based on a platform change; teaches income volatility in passive/creator income specifically
- **Income Type** — one-time sponsored post vs. evergreen ad revenue (existing, re-homed here)
- **Merch Drop Math** *(new)* — unit cost, print minimums, and breakeven on a merch run; teaches fixed cost / breakeven concept concretely

### 3.3 Trades & Hustles *(Tier 2+)*
- **Hustle Pricing** — the lawn-job pricing tie (existing)
- **Self-Employment Tax** — "Nobody Told Me" (existing, re-homed)
- **Tool Investment** *(new)* — buy a better pressure washer on credit to take bigger jobs, or stay small and cash-only; teaches leverage as a real trade-off, not just a warning
- **Apprentice vs Solo** *(new)* — take steady lower pay learning a trade vs. freelance immediately at higher, unstable pay

### 3.4 Digital Traps *(Tier 2+)*
- **Subscription Trap** — free trial mechanics (existing)
- **FOMO Timer** — fake urgency countdowns (existing)
- **Checkout Upsell** — the multi-stage upsell maze (existing)
- **Dark Pattern Cancel** *(new)* — a service makes canceling deliberately hard; player navigates a fake "are you sure" maze, teaches persistence-testing as a manipulation tactic

### 3.5 Trust & Fraud *(Tier 3+)*
- **Phishing** — "You Won!" (existing)
- **Fake Investment** — "Guaranteed Returns" (existing)
- **Social Engineering** — "Just This Once" gift card ask (existing)
- **Layered Scam** — "The Brand Deal That Wasn't" (existing)
- **Online Trust Test** *(new, age-appropriately framed)* — an online-only "friend" of a few weeks asks for help urgently; kept non-romantic, framed purely as a trust/urgency pattern

### 3.6 Borrowed Money *(Tier 4+)*
- **Minimum Payment** — the 41-months reveal (existing)
- **Interest Comparison** — "Two Loans" (existing)
- **Good Debt vs Bad Debt** — "Financing the Flex," car vs. sneakers (existing)
- **Cosigning Risk** *(new)* — a friend asks you to cosign a loan; teaches that cosigning makes their debt legally yours too, a genuinely under-taught concept at this age

### 3.7 Markets & Risk *(Tier 5 only)*
- **Diversification** — "All In vs Spread Out" (existing)
- **Boring vs Hyped** — index fund vs. meme stock (existing)
- **Outlier Event** — see Section 5, full catalog

### 3.8 Real Estate & Assets *(Tier 4+, NEW vertical)*
- **Rent vs Buy** *(new)* — simplified but real: monthly rent vs. mortgage+maintenance+opportunity cost of the down payment, teaches that "buying is always better" is not universally true
- **Depreciating vs Appreciating** *(new)* — a car loan vs. a "starter" real estate stake, teaches asset classes behave differently over time
- **Landlord Math** *(new, Tier 5)* — buying a small rental property; revenue looks great until vacancy, repairs, and property tax reveal real net yield

### 3.9 Insurance & Risk Transfer *(Tier 3+, NEW vertical)*
- **Skip vs Cover** *(new)* — no insurance (save the premium) vs. basic coverage; a random bad-luck event resolves after the bet, teaches expected-value thinking under uncertainty
- **Deductible Tradeoff** *(new)* — high premium/low deductible vs. low premium/high deductible, teaches this is a real math problem, not a moral one

### 3.10 Startup World *(Tier 5 only, NEW vertical)*
- **The Pitch** — the Outlier Event flagship case (see Section 5)
- **Equity vs Salary** *(new)* — join a friend's startup for lower pay + equity vs. a stable job; log-normal-flavored outcome, most of the time the stable job wins, rarely the equity is huge
- **Burn Rate** *(new)* — a startup context Case about runway: spending fast to grow vs. conserving cash, teaches burn rate as a real, tense countdown mechanic

### 3.11 Sports & NIL *(Tier 3+, NEW vertical — high cultural relevance for this age group)*
- **The NIL Deal** *(new)* — a young athlete gets a name/image/likeness sponsorship offer; teaches contract terms, exclusivity clauses, and the same "vague = red flag" pattern from Trust & Fraud, in a context this age group actually follows
- **Signing Bonus Math** *(new)* — a big one-time number vs. steady smaller payments over time, teaches present value intuitively without ever naming it

### Vertical registry table (complete)

| Vertical | Min Tier | Case count at launch | Status |
|---|---|---|---|
| Everyday Money | 1 | 6 | Content-complete |
| Creator Economy | 2 | 4 | 1 existing + 3 new to write |
| Trades & Hustles | 2 | 4 | 2 existing + 2 new to write |
| Digital Traps | 2 | 4 | 3 existing + 1 new to write |
| Trust & Fraud | 3 | 5 | 4 existing + 1 new to write |
| Borrowed Money | 4 | 4 | 3 existing + 1 new to write |
| Markets & Risk | 5 | 3 | 2 existing + Outlier Events |
| Real Estate & Assets | 4 | 3 | All new to write |
| Insurance & Risk Transfer | 3 | 2 | All new to write |
| Startup World | 5 | 3 | All new to write |
| Sports & NIL | 3 | 2 | All new to write |

**Total: 40 Case concepts across 11 verticals.** 15 already fully scripted from prior GDD versions, 25 net-new concepts defined here (not yet fully scripted — that's the actual remaining content workload, now organized and scoped instead of vague).

---

## 4. TRAITS — REINTEGRATED, NOW VERTICAL-AWARE

Traits from the earlier GDD return, with several updated to interact with Verticals specifically — this is what makes vertical choice matter mechanically, not just cosmetically.

| Trait | Effect | Vertical interaction |
|---|---|---|
| Cheapskate | +20% cash on Purchase-type wins | Strongest in Everyday Money |
| YOLO Spender | +30% on nailed_it, 2x cost on way_off | Strongest in Startup World (high variance matches high variance) |
| Scam Sense | Auto-reveals 1 Evidence row on Scam-type Cases | Strongest in Trust & Fraud |
| Side Hustler | +15% cash in Trades & Hustles and Creator Economy specifically | New — first Trait explicitly scoped to 2 verticals |
| Landlord Instinct | +20% cash in Real Estate & Assets, -10% elsewhere (over-specialization tradeoff) | New — rewards leaning into a vertical, at a cost |
| The 1% | Doubles both wins and losses on Markets & Risk and Startup World Cases | Extended from prior version to cover 2 verticals |
| Steady Hand | Removes deception entirely on Cases from Borrowed Money (always know if the flashy one lies), but -10% cash everywhere else | New — a genuine specialization choice |

This is the mechanism that makes "which vertical did you lean into" a real build decision, not flavor text — a Landlord Instinct + Real Estate-heavy run plays meaningfully differently than a Scam Sense + Trust & Fraud-heavy run.

---

## 5. OUTLIER EVENTS — FULL CATALOG (Tier 5 only)

All use log-normal distributions per the earlier correction — real wealth swings are fat-tailed, not bell-curved.

1. **The Pitch** — invest in a friend's startup, most runs a dud, rare 15x
2. **The Lawsuit** *(new)* — a minor incident escalates; most outcomes are a manageable settlement, rare outcome is a genuinely large cost, teaches that liability risk is also fat-tailed, not just upside
3. **The Viral Moment** *(new)* — a creator-vertical crossover: a post unexpectedly blows up, most gains are modest, rare outcome is a career-changing spike, explicitly non-repeatable (a flag prevents grinding this one)
4. **The Inheritance** *(new)* — reveals only after the bet: a distant relative's estate is usually small/nothing, rarely substantial; deliberately teaches that windfalls are not a plan, they're a rare tail event
5. **The Crash** *(new)* — a downside-only Outlier: a market-wide event that reduces holdings; teaches that fat tails cut both directions, not just favorably — a Markets & Risk-heavy player with no Diversifier-style Trait should feel this one

---

## 6. COMPLETE ARCHITECTURE & DATA MODEL

### New/changed files
```
app/
  cases.py       - CaseTemplate classes, TIER_DIFFICULTY, apply_tier_difficulty()
  verticals.py   - Vertical dataclass, VERTICAL_REGISTRY, register_vertical() calls
  traits.py      - NEW: Trait dataclass, TRAIT_REGISTRY, apply_trait_effects()
  outliers.py    - NEW: outlier_swing(), OUTLIER_EVENT_REGISTRY
  db.py          - unchanged schema; add current_tier(), recent_vertical_weight()
  main.py        - draw logic now: tier -> eligible verticals -> weighted vertical pick -> case type -> apply tier difficulty -> apply active traits
```

### Draw pipeline (full, current state)
```python
def draw_next_case(run: dict) -> CaseResult:
    tier = current_tier(run["cash"])
    eligible_verticals = [v for v in VERTICAL_REGISTRY.values() if v.min_tier <= tier]
    weights = [interest_weight(v, run["history"]) for v in eligible_verticals]
    vertical = random.choices(eligible_verticals, weights=weights, k=1)[0]

    case_type = random.choice(vertical.case_types)
    case = draw_case(case_type)                      # base generation
    case = apply_tier_difficulty(case, tier)          # scale numbers/ranges/layers
    case = apply_trait_effects(case, run["traits"], vertical)  # trait modifiers

    if tier == 5 and random.random() < 0.05:
        case = maybe_replace_with_outlier_event(case)

    return case
```

### Schema additions (minimal — reuses existing JSON columns)
- `runs.history` entries gain a `vertical` field (string key) alongside existing `case_id`, `tier`, `reward`
- `runs` gains a `traits` column (JSON list of active Trait keys) — the only actual new column needed

---

## 7. FULL CURRICULUM CROSSWALK

| Vertical | Tier(s) | Core financial concepts covered |
|---|---|---|
| Everyday Money | 1-5 | Currency illusion, needs/wants, hidden costs, fees, savings types, credit mechanics |
| Creator Economy | 2+ | Passive vs active income, contract literacy, income volatility, breakeven math |
| Trades & Hustles | 2+ | Profit vs revenue, self-employment tax, leverage, opportunity cost of training |
| Digital Traps | 2+ | Dark patterns, urgency manipulation, checkout psychology, cancellation friction |
| Trust & Fraud | 3+ | Phishing, fake investment red flags, social engineering, layered scams |
| Borrowed Money | 4+ | Minimum payment trap, interest comparison, good/bad debt, cosigning liability |
| Markets & Risk | 5 | Diversification, risk/reward, fat-tail investing outcomes |
| Real Estate & Assets | 4+ | Rent vs buy, asset classes, net yield vs gross revenue |
| Insurance & Risk Transfer | 3+ | Expected value under uncertainty, premium/deductible tradeoffs |
| Startup World | 5 | Equity vs salary, burn rate, fat-tail entrepreneurial outcomes |
| Sports & NIL | 3+ | Contract terms, present value intuition, exclusivity clauses |

Every one of the original 22 curriculum subtopics is covered by at least one Vertical; the new verticals (Real Estate, Insurance, Startup World, Sports & NIL) add concepts the original 22 never touched — present value, expected value under uncertainty, cosigning liability, net yield — which is a genuine curriculum upgrade, not just more content volume.

---

## 8. BUILD SEQUENCING (given this is now a much bigger spec)

1. **Engine first**: `apply_tier_difficulty()`, `verticals.py` registry, wire into existing 6 Everyday Money Cases — this proves the whole pipeline on content you've already fully scripted
2. **One new vertical fully content-complete** (recommend Creator Economy — highest cultural relevance, only 3 new Cases to write) — proves a second vertical end to end
3. **Traits reintegration** — apply_trait_effects() against the 2 verticals now live
4. **Remaining launch verticals**, roughly 2-4 new Case scripts each, written in whatever order matches your actual interest/energy — the architecture no longer cares about order
5. **Outlier Events** — last, since they only matter once Tier 5 is reachable, which requires the rest of the curve to exist first

This is a genuinely large build now — 40 Case concepts vs. the 6 that exist in code today. That's the honest size of what "incredibly fleshed out" costs. The architecture supports building it incrementally without ever being in a broken state, which is the most important property given the scope.
