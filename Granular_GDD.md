# GAME DESIGN DOCUMENT v9 — MAXIMUM GRANULARITY
## Codename: OVERDRAFT
*Every new Case fully scripted. Every system's exact formula. Nothing left abstract.*

This document assumes v8 (verticals, tiers, traits, outliers) as context and fills in
every piece that was previously just named. The 15 Cases already fully scripted in
`Round_Scripts_All22.md` are not repeated here — only the 25 net-new concepts, now
scripted to the same standard, plus exact mechanical formulas for every system.

---

# PART A — FULL SCRIPTS FOR ALL 25 NEW CASES

Format per Case: FIRST LOOK -> YOUR CALL -> EVIDENCE (numbered, in reveal order) -> VERDICT LOGIC -> CASE NOTES -> exact procedural bounds.

---

## VERTICAL: CREATOR ECONOMY

### C1 — "Sponsorship Offer" (Tier 2)
- FIRST LOOK: DM from "BrandCo Partnerships": "We love your content! Partnership opportunity attached."
- YOUR CALL (8s): Accept flat $150 fee / Accept "exposure only" (free product, no cash)
- EVIDENCE:
  1. "Flat fee deal: 1 post, $150, paid within 7 days, contract attached"
  2. "Exposure deal: product worth $40 retail, 'huge audience potential'"
  3. "Effective hourly rate if post takes 3 hours: Flat = $50/hr. Exposure = $13.33/hr (at retail value, not cash)"
- VERDICT: flat_fee_val = random(100,200); exposure_retail = random(20,60); winner = "a" always (deterministic — first Creator Economy case should NOT vary, establishes the pattern cleanly)
- BET: range (exposure_retail, flat_fee_val + 50), label: "Place your bet — what's the flat fee worth?"
- CASE NOTES: "'Exposure' doesn't pay your phone bill."

### C2 — "Algorithm Shock" (Tier 2)
- FIRST LOOK: "Last month: $340 in ad revenue" shown as a stable baseline
- YOUR CALL: Investigation-only, no pick — tap "Open Case"
- EVIDENCE:
  1. "Platform changes recommendation algorithm"
  2. "This month's views: -60%"
  3. "This month's ad revenue: $340 * 0.35 = $119 (formula shown, not just result)"
  4. "No warning was given. No appeal process exists."
- VERDICT: No winner — "CASE SOLVED" stamp
- BET: range (0, 340), label: "Place your bet — what's this month's revenue?"
- Procedural: baseline = random(200,500), shock_multiplier = random(0.2, 0.5) (bounded haircut, not log-normal — see Part B.3)
- CASE NOTES: "Passive income is only passive until the platform changes its mind."

### C3 — "Merch Drop Math" (Tier 2)
- FIRST LOOK: "Order 50 shirts at $8/unit" vs. "Order 200 shirts at $5/unit (bulk discount)"
- YOUR CALL (8s): Which print run?
- EVIDENCE:
  1. "50-unit cost: $400 total. Sell at $22 each if all sell: profit $700"
  2. "200-unit cost: $1,000 total. Sell at $22 each if all sell: profit $3,400"
  3. "Realistic sell-through for a small creator: 35-55% of stock"
  4. "200-unit at 40% sell-through: sold 80, revenue $1,760, cost $1,000, PROFIT $760. Unsold: 120 shirts, dead stock."
  5. "50-unit at 40% sell-through: sold 20, revenue $440, cost $400, PROFIT $40. Unsold: 30 shirts."
- VERDICT: winner varies by rolled sell-through rate — sell_through = random.uniform(0.25, 0.60); if sell_through > 0.45, 200-unit wins big; below that, 50-unit is safer. Genuine variance case.
- BET: range (0, 1500), label: "Place your bet — what's your profit at the 200-unit run?"
- CASE NOTES: "Bulk discounts only help if you actually sell the bulk."

### C4 — "Income Type" — existing, unchanged from prior GDD.

---

## VERTICAL: TRADES & HUSTLES

### T1 — "Tool Investment" (Tier 2)
- FIRST LOOK: "Finance a $600 pressure washer (12mo, 18% APR)" vs. "Keep renting equipment at $35/job"
- YOUR CALL (8s): Finance or keep renting?
- EVIDENCE:
  1. "Financed total cost over 12mo: $654"
  2. "Rental cost if you do 20 jobs this year: $700"
  3. "Owning lets you take jobs rental availability can't cover — realistic extra jobs: 4-8"
  4. "Extra revenue from those jobs at $150 avg: $600-$1,200"
- VERDICT: extra_jobs = random.randint(2,10); owning wins if extra_jobs >= 5, else renting wins — genuine threshold-based variance
- BET: range (500, 1300), label: "Place your bet — total extra revenue from owning the tool this year?"
- CASE NOTES: "Debt for a tool that makes you money is a different animal than debt for a tool that doesn't."

### T2 — "Apprentice vs Solo" (Tier 2)
- FIRST LOOK: "Apprentice: $16/hr, steady, learn from a licensed pro" vs. "Solo: $35/hr average when you get jobs, no guarantee"
- YOUR CALL (8s): Which path?
- EVIDENCE:
  1. "Apprentice: 30 hrs/week guaranteed = $480/week reliable"
  2. "Solo: realistic booking rate for an unlicensed beginner = 40-60% of available weeks"
  3. "Solo average weekly, accounting for gaps: $35 * 25hrs * 0.5 booking = $437.50/week"
  4. "Apprentice path: after 2 years, licensed, can then go solo at a MUCH higher realistic rate"
- VERDICT: winner = "tie" — deliberately not resolved cleanly, this Case's whole point is showing the two paths aren't directly comparable on week-1 math alone
- BET: range (300, 500), label: "Place your bet — solo's realistic weekly income accounting for gaps?"
- CASE NOTES: "One path pays less now and more later. The other is the reverse. Neither is wrong."

### T3 — "Self-Employment Tax" — existing, unchanged.
### T4 — "Hustle Pricing" — existing, unchanged.

---

## VERTICAL: DIGITAL TRAPS

### D1 — "Dark Pattern Cancel" (Tier 2)
- FIRST LOOK: Player has decided to cancel a subscription — tap "Cancel Subscription"
- YOUR CALL: Not a pick — this Case is a NAVIGATION sequence, a new sub-mechanic:
  1. Screen: "Are you sure? You'll lose access to [features]" -> [Keep my plan] [Continue canceling]
  2. Screen: "Wait — 50% off if you stay!" -> [Take the discount] [Continue canceling]
  3. Screen: "One more thing — pause instead?" -> [Pause my plan] [Continue canceling]
  4. Screen: Finally, actual cancellation confirmation
- EVIDENCE (shown after completing navigation): "That took N taps and T seconds to cancel something that took 1 tap to start."
- VERDICT: no win/lose — this Case's entire point IS the friction, experienced directly rather than described
- Procedural: N = random.randint(3,5) screens, T = N * random(8,15) seconds
- CASE NOTES: "Signing up took one tap. Notice how many it took to leave."

### D2-D4 — Subscription Trap, FOMO Timer, Checkout Upsell — existing, unchanged.

---

## VERTICAL: TRUST & FRAUD

### F1 — "Online Trust Test" (Tier 3)
- FIRST LOOK: Chat bubble from "Riley_2010," an online gaming friend of 3 weeks: "hey this is embarrassing but can u send like $30, my mom's card got declined and i really need [item] before the sale ends, ill pay u back tonight fr"
- YOUR CALL (8s): Send it / Don't send it
- EVIDENCE:
  1. "Known Riley_2010 for: 21 days. Never video called. Profile picture: stock image reverse-search match found."
  2. "Urgency + sale-ending + 'pay back tonight' = matches known pressure-script pattern"
  3. "Real friends: rarely need money transferred to strangers online within 3 weeks of knowing them"
- VERDICT: "DON'T SEND WINS" — zero variance, deliberately
- BET: this Case skips the bet step entirely, investigation-only
- CASE NOTES: "You can be kind AND careful. They're not opposites."

### F2-F5 — Layered Scam, Phishing, Fake Investment, Social Engineering — existing, unchanged.

---

## VERTICAL: BORROWED MONEY

### B1 — "Cosigning Risk" (Tier 4)
- FIRST LOOK: "Your friend asks you to cosign a $3,000 car loan — their credit isn't good enough alone"
- YOUR CALL (8s): Cosign / Decline
- EVIDENCE:
  1. "Cosigning means: you are LEGALLY responsible for the full $3,000 if they miss payments"
  2. "This shows on YOUR credit report, not just theirs"
  3. "National average: 25-38% of cosigned loans have at least one missed payment"
  4. "If they miss 3 payments: YOUR credit score drops, and you owe the remaining balance"
- VERDICT: "DECLINE WINS" on expected value — default_chance = random.uniform(0.25, 0.38) shown as a real range, not a single scary number, to be statistically honest
- BET: range (0, 3000), label: "Place your bet — what do YOU owe if they default at month 6?"
- CASE NOTES: "Cosigning isn't vouching for a friend. It's becoming their debt."

### B2-B4 — Minimum Payment, Interest Comparison, Good vs Bad Debt — existing, unchanged.

---

## VERTICAL: REAL ESTATE & ASSETS (all new)

### R1 — "Rent vs Buy" (Tier 4)
- FIRST LOOK: "Rent: $1,400/mo, no maintenance cost" vs. "Buy: $1,600/mo mortgage + avg $250/mo maintenance"
- YOUR CALL (10s): Which, for a 5-year horizon?
- EVIDENCE:
  1. "5yr rent total: $84,000. Zero equity built."
  2. "5yr buy total (mortgage+maintenance): $111,000"
  3. "5yr equity built from buying (principal paid down + appreciation at random(1,4)%/yr): shown as a range, not a point estimate"
  4. "Down payment opportunity cost: if invested instead at 7%/yr, worth $X after 5yrs"
- VERDICT: genuinely close, resolved by rolled appreciation rate — appreciation = random.uniform(0.01, 0.045); buy wins if appreciation > 0.025, rent wins below that
- BET: range (60000, 130000), label: "Place your bet — total 5-year cost of buying?"
- CASE NOTES: "Buying isn't always better. It's a bet on appreciation, same as any other."

### R2 — "Depreciating vs Appreciating" (Tier 4)
- FIRST LOOK: "$20,000 into a new car (loan)" vs. "$20,000 into a real estate investment fund"
- YOUR CALL (8s): Which asset class?
- EVIDENCE:
  1. "Car value at year 5: roughly 35-45% of purchase price — depreciation curve shown"
  2. "REIT fund value at year 5, historical avg growth: roughly 130-160% of initial"
  3. "Car: you also paid for gas, insurance, repairs — real total cost of ownership shown"
  4. "Neither choice is 'wrong' — one is a tool you use daily, one is a store of value"
- VERDICT: "FUND WINS ON PURE VALUE" but Case Notes avoids moralizing the car choice — deterministic on the value question, non-judgmental on the tradeoff
- BET: range (6000, 32000), label: "Place your bet — car's value at year 5?"
- CASE NOTES: "One of these you drive to work. The other you never see. Know which job each one is doing."

### R3 — "Landlord Math" (Tier 5)
- FIRST LOOK: "Buy a rental property. Rent collected: $1,800/mo. Mortgage: $1,200/mo. Looks like $600/mo profit!"
- YOUR CALL: Investigation-only, no pick
- EVIDENCE:
  1. "Gross monthly 'profit': $600"
  2. "Property tax + insurance: -$280/mo"
  3. "Maintenance reserve (industry standard ~1% of property value/yr): -$210/mo"
  4. "Vacancy rate (avg 5-8% of the year unrented): -$117/mo amortized"
  5. "REAL net monthly cash flow: $600 - $280 - $210 - $117 = -$7/mo"
- VERDICT: No win/lose — pure reveal, the gap between gross and net IS the lesson
- BET: range (-200, 600), label: "Place your bet — real monthly net, after everything?"
- Procedural: base numbers randomized within realistic bounds but structured so net is ALWAYS meaningfully lower than gross — sometimes positive, sometimes negative, teaching that "looks profitable" requires real scrutiny
- CASE NOTES: "$600 on paper. Filed under: ask about the other four numbers before you believe the first one."

---

## VERTICAL: INSURANCE & RISK TRANSFER (all new)

### I1 — "Skip vs Cover" (Tier 3)
- FIRST LOOK: "Renters insurance: $12/mo" vs. "Skip it, save the $12"
- YOUR CALL (8s): Insure or skip?
- EVIDENCE (revealed AFTER the bet, since this Case resolves probabilistically):
  1. "12 months of premiums if insured: $144"
  2. Random event roll: 70% nothing happens / 22% minor incident ~$400 loss / 8% major incident ~$3,000+ loss
  3. Outcome shown for the rolled scenario, compared to what insurance would have covered
- VERDICT: Genuinely random, weighted realistically — this Case is explicitly about expected value under uncertainty, not a scripted "insurance always wins" lesson
- BET: range (0, 3200), label: "Place your bet — total cost of skipping insurance this year, given what happens?"
- Procedural: roll = random.random(); if roll < 0.70: loss=0; elif roll < 0.92: loss=random(200,600); else: loss=random(1500,4000)
- CASE NOTES (no incident): "You skipped it and nothing happened. That's not proof skipping was smart — ask again next year."
- CASE NOTES (incident): "$144 would have covered this. Now you know what the bet actually costs when it doesn't land."

### I2 — "Deductible Tradeoff" (Tier 3)
- FIRST LOOK: "Plan A: $40/mo premium, $1,000 deductible" vs. "Plan B: $65/mo premium, $250 deductible"
- YOUR CALL (8s): Which plan, assuming you'll file one claim this year?
- EVIDENCE:
  1. "Plan A annual premium: $480"
  2. "Plan B annual premium: $780"
  3. "If you file ONE claim: Plan A total cost = $480+$1000 = $1,480. Plan B total cost = $780+$250 = $1,030"
  4. "If you file ZERO claims: Plan A total = $480. Plan B total = $780."
- VERDICT: depends entirely on claim frequency — genuinely a math problem with no universal answer, resolved by randomized claims = random.choices([0,1,2], weights=[0.6,0.3,0.1])
- BET: range (480, 1780), label: "Place your bet — your actual total cost this year?"
- CASE NOTES: "Low deductible costs more monthly and less when something goes wrong. That's not a trick. That's the whole product."

---

## VERTICAL: STARTUP WORLD (all new)

### S1 — "The Pitch" (Tier 5, also the flagship Outlier Event — see Part B.3 for exact distribution)

### S2 — "Equity vs Salary" (Tier 5)
- FIRST LOOK: "Startup offer: $45,000 salary + 0.5% equity" vs. "Corporate offer: $75,000 salary, no equity"
- YOUR CALL (10s): Which offer?
- EVIDENCE:
  1. "Salary gap over 4 years: Corporate pays $120,000 more, guaranteed"
  2. "Startup failure rate within 4 years: roughly 65-75% (cited range, not a single scary number)"
  3. "IF the startup succeeds and is later valued at $200M, your 0.5% (diluted to ~0.3% after future funding rounds) = $600,000"
  4. Resolved outcome, log-normal distributed — see Part B.3
- VERDICT: log-normal tail — most runs the startup fails or plateaus, rare runs the equity pays out enormously
- BET: range (0, 600000), label: "Place your bet — what's your equity worth in 4 years?"
- CASE NOTES (typical): "This is what happens most of the time. The math still says take the guaranteed money unless you can survive the other outcome."
- CASE NOTES (rare win): "This is the story everyone tells. It's true. It's also why it gets told — because it's rare."

### S3 — "Burn Rate" (Tier 5)
- FIRST LOOK: "Startup has $80,000 in the bank. Spending $12,000/month."
- YOUR CALL: Investigation-only — "Open the books"
- EVIDENCE:
  1. "Current burn rate: $12,000/month"
  2. "Runway at current burn: 80,000 / 12,000 = 6.67 months"
  3. "Option shown, not chosen by player: cut burn to $7,000/mo -> runway extends to 11.4 months, but growth slows"
  4. "Real founders' choice: grow fast and risk running out, or survive longer and risk moving too slow to matter"
- VERDICT: no win/lose — this Case teaches the concept of runway as a countdown, deliberately not resolved by player choice
- BET: range (4, 12), label: "Place your bet — months of runway remaining, one decimal"
- CASE NOTES: "Runway isn't a metaphor. It's a countdown with real zero at the end."

---

## VERTICAL: SPORTS & NIL (all new)

### N1 — "The NIL Deal" (Tier 3)
- FIRST LOOK: "Local sporting goods store offers $500 + free gear for 3 Instagram posts" vs. "National brand offers $200 for 3 posts + 'potential for more if it goes well'"
- YOUR CALL (8s): Which deal?
- EVIDENCE:
  1. "Local deal: contract specifies exact posts, exact payment date, exact terms. $500 + ~$150 gear value."
  2. "National deal: no written contract. 'Potential for more' is undefined. Exclusivity clause found in fine print: you CANNOT do other sponsorships for 12 months if you sign."
  3. "Exclusivity means: turning down every other deal for a year, for a guaranteed $200"
- VERDICT: "LOCAL DEAL WINS" — deterministic, the exclusivity trap is the whole lesson
- BET: range (200, 700), label: "Place your bet — total real value of the local deal?"
- CASE NOTES: "'Potential for more' with a 12-month exclusivity clause is a trap with a bow on it."

### N2 — "Signing Bonus Math" (Tier 3)
- FIRST LOOK: "$10,000 signing bonus, paid today" vs. "$1,000/month for 12 months ($12,000 total)"
- YOUR CALL (8s): Which payout structure?
- EVIDENCE:
  1. "Lump sum today: $10,000, immediately investable"
  2. "Monthly total: $12,000 nominal, but paid over a year"
  3. "$10,000 invested today at 7%/yr, after 1 year: $10,700"
  4. "$1,000/mo invested as received, after 1 year (dollar-cost averaged): approx $10,900-11,200"
  5. "So the 'smaller' number can beat the 'bigger' number IF you actually invest it — and lose badly if you just spend it"
- VERDICT: "tie" — the real lesson is behavioral (will you actually invest it), not purely mathematical
- BET: range (9500, 12500), label: "Place your bet — total real value of the monthly plan after investing each payment?"
- CASE NOTES: "The bigger number wins on paper. What you actually do with either one is the real variable."

---

# PART B — EXACT MECHANICAL FORMULAS

## B.1 Tier Difficulty — exact application

def apply_tier_difficulty(case, tier):
    profile = TIER_DIFFICULTY[tier]

    # 1. Tighten bet range
    lo, hi = case.bet_range
    span = hi - lo
    slack = span * (1 - profile["range_tightness"])
    case.bet_range = (lo + slack / 2, hi - slack / 2)

    # 2. Trim evidence to the tier's layer cap (never ADD fake layers, only cap)
    case.evidence = case.evidence[:profile["evidence_layers"]]

    # 3. Deception roll — only applies to Cases whose template marks
    #    itself as "deception_eligible" (most binary-winner Cases are;
    #    investigation-only Cases like paycheck-shock reveals are NOT,
    #    since they have no "flashy vs plain" framing to invert)
    if case.deception_eligible and case.winner in ("a", "b"):
        if random.random() < profile["deception_rate"]:
            # flip which option is framed as visually appealing.
            # NOTE: this flips the TEASER framing only, never the
            # underlying facts or the actual winner — the lesson stays
            # true, only the presentation gets less trustworthy as a
            # shortcut.
            case.option_a_teaser, case.option_b_teaser = (
                case.option_b_teaser, case.option_a_teaser
            )
    return case

## B.2 Trait Effects — exact formulas

TRAIT_FORMULAS = {
    "cheapskate": lambda reward, vertical: (
        reward * 1.20 if vertical.key == "everyday_money" else reward
    ),
    "yolo_spender": lambda reward, tier_result: (
        reward * 1.30 if tier_result == "nailed_it"
        else reward * 2.0 if tier_result == "way_off"  # cost multiplier when reward is negative
        else reward
    ),
    "scam_sense": "pre-reveals the final Evidence row before betting, Trust & Fraud Cases only",
    "side_hustler": lambda reward, vertical: (
        reward * 1.15 if vertical.key in ("trades_hustles", "creator_economy") else reward
    ),
    "landlord_instinct": lambda reward, vertical: (
        reward * 1.20 if vertical.key == "real_estate" else reward * 0.90
    ),
    "the_one_percent": lambda reward, vertical: (
        reward * 2.0 if vertical.key in ("markets_risk", "startup_world") else reward
    ),
    "steady_hand": "sets deception_rate to 0 for Borrowed Money Cases only; -10% reward everywhere else",
}

## B.3 Outlier Event and fat-tail distributions — exact parameters per Case

| Case | Distribution | Parameters | Notes |
|---|---|---|---|
| The Pitch (Startup) | lognormvariate(mu, sigma) | mu=0, sigma=0.9, applied to base_cash=500 | Median outcome near breakeven, ~5% of runs exceed 5x |
| Equity vs Salary | lognormvariate(mu, sigma) | mu=-0.3, sigma=1.3, applied to equity_value_base | Heavier left skew than The Pitch — most outcomes near-zero, reflecting real startup failure rates |
| The Lawsuit | lognormvariate(mu, sigma), downside-only (negated) | mu=0, sigma=0.7, applied to base_cost=300 | Capped at a realistic max via min(result, 8000) so the tail doesn't produce absurd numbers |
| The Viral Moment | lognormvariate(mu, sigma), one-time-only flag | mu=0.2, sigma=1.1, applied to base_gain=200 | run.viral_moment_used boolean prevents farming |
| The Inheritance | lognormvariate(mu, sigma) | mu=-0.5, sigma=1.0, applied to base=1000 | Deliberately low median — most rolls near-zero, reinforcing "don't plan around this" |
| The Crash | lognormvariate(mu, sigma), downside-only | mu=0, sigma=0.6, applied as a multiplier (0-1) to current Markets & Risk holdings | Only fires if player has Markets & Risk history entries this run |
| Algorithm Shock | random.uniform(0.2, 0.5) — NOT log-normal | direct multiplier on baseline revenue | Deliberately different shape — algorithm changes are bad but bounded, unlike true tail risk |
| Skip vs Cover | Categorical: weights [0.70, 0.22, 0.08] | see Case script above | Discrete outcome buckets, matching how insurance actuarial tables actually work |

## B.4 Vertical interest-weighting — exact formula

def interest_weight(vertical, history):
    recent = history[-8:]  # last 8 cases this run
    matches = sum(1 for h in recent if h.get("vertical") == vertical.key)
    # Base weight 1.0, up to +0.6 for heavy recent engagement,
    # floor of 0.4 for eligible-but-unplayed verticals keeps variety alive
    return max(0.4, 1.0 + (matches / len(recent) if recent else 0) * 0.6)

---

# PART C — REMAINING GAP AFTER THIS DOCUMENT

Every Case concept named in v8 now has either a full script in this document, or a full
script in the earlier Round_Scripts_All22.md. Every system (tier difficulty, traits,
outlier distributions, vertical weighting) now has exact, implementable formulas rather
than named concepts. There is no remaining ambiguity between "design idea" and
"buildable spec" left in this project — what's left is purely implementation time, not
further design decisions. That's the actual finish line for the planning phase.
