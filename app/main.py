"""
Overdraft — FastAPI app + the run loop.

Run from the project root:   uvicorn app.main:app --reload
Or hit Run on this file directly — the __main__ block handles the path setup.

The game is one endless tier-climbing session (v8 §6): cash is net worth, net
worth picks the Net Worth Tier, the tier gates which verticals can appear, and
interest-weighting biases the draw. Each Case runs the proven loop:
DEAL -> YOUR CALL -> BET -> EVIDENCE -> VERDICT -> next Case.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app import db
from app import content   # noqa: F401 — import side effects populate the registries
from app.cases import (
    CaseResult, STARTING_CASH, score_bet, case_reward, recognition_reward,
    loss_streak, BUST_THRESHOLD,
)
from app.verticals import (
    VERTICAL_REGISTRY, VERTICAL_ORDER, current_tier, tier_name,
    eligible_verticals, draw_for_player, ARCHETYPES,
)
from app.dev import router as dev_router

app = FastAPI(title="Overdraft")
# Dev-cheat panel. Mounted unconditionally, but EVERY route inside is gated on
# settings.DEV_MODE and 404s without it (app/dev.py) — one gate, on the router, so the
# surface can't half-ship. Nothing here is reachable in a build that doesn't set DEV_MODE.
app.include_router(dev_router)
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

db.init_db()

PLAYER_COOKIE = "overdraft_player"


def current_player(request: Request) -> dict | None:
    player_id = request.cookies.get(PLAYER_COOKIE)
    return db.get_player(player_id) if player_id else None


def _draw(player: dict) -> CaseResult:
    """Draw the next Case for a player through the full pipeline (v8 §6).

    The pipeline itself (callback slot -> tier -> archetype-weighted vertical -> case ->
    tier difficulty) lives in verticals.draw_for_player() so the dev inspection routes can
    sample the identical function; this is just the player-dict adapter. Traits (v8 §4) and
    Outlier Events (v8 §5) get layered on here in later build steps.
    """
    return draw_for_player(player["cash"], player["history"],
                           archetype=player.get("archetype"))


def _tier_context(cash: float) -> dict:
    """Net-worth-tier display data for the topbar / home screen."""
    tier = current_tier(cash)
    lo, hi = None, None
    from app.cases import TIER_DIFFICULTY
    lo, hi = TIER_DIFFICULTY[tier]["cash_range"]
    if hi is None:
        progress = 1.0
    else:
        progress = max(0.0, min(1.0, (cash - lo) / (hi - lo))) if hi > lo else 1.0
    return {"tier": tier, "tier_name": tier_name(tier), "tier_progress": progress,
            "tier_lo": lo, "tier_hi": hi}


def _is_busted(player: dict) -> bool:
    """A run is over once losses hit the bust threshold (Locked Refinement #3).
    A fresh player's empty history is streak 0, so this only fires on a real bust."""
    return loss_streak(player["history"]) >= BUST_THRESHOLD


def _cold_case_context(player: dict) -> dict:
    """Cold Case framing, keyed to how far peak_cash was above the bust point —
    a Tier 1 bust and a fall from a $31k peak should not read the same."""
    peak = player["peak_cash"]
    peak_tier = current_tier(peak)
    if peak_tier <= 1:
        headline = "Busted Before You Built"
        body = ("Four cold calls in a row and the run's over. You never got past Broke — "
                "but reading the deal was always the point. Now you know what a losing "
                "streak feels like. Go again.")
    elif peak_tier <= 3:
        headline = "The Slide"
        body = (f"You climbed to ${peak:,} at your peak, then four straight misses undid it. "
                f"That's the trap — losses compound faster than wins. You've seen the "
                f"patterns now. Start over.")
    else:
        headline = "From the Top"
        body = (f"You were sitting on ${peak:,}. Four bad calls in a row and it's gone. The "
                f"higher you climb, the more a cold streak costs — nobody's too rich to "
                f"bust. Start over, and protect the downside this time.")
    return {"peak_cash": peak, "peak_tier": peak_tier, "final_cash": player["cash"],
            "streak": loss_streak(player["history"]), "bust_threshold": BUST_THRESHOLD,
            "cold_headline": headline, "cold_body": body}


def _resolve_case(request: Request, player: dict, case: CaseResult, reward: int,
                  called_it: bool, result_tier: str, ctx: dict):
    """Close out a Case: bank the reward, append the outcome, check bust, draw the next
    Case, render the verdict. Shared by BOTH resolution paths — /bet (Cases with a bet)
    and /pick (recognition Cases, has_bet=False, which resolve the moment the pick lands).

    Kept in one place deliberately: bust checking, peak tracking and the next-Case draw
    must behave identically no matter which path got here, and two copies would drift.
    `ctx` carries the path-specific verdict-template fields (bet figures, feedback badge).
    """
    old_cash = player["cash"]
    new_cash = old_cash + reward
    old_tier, new_tier = current_tier(old_cash), current_tier(new_cash)

    outcome = {
        "case_id": case.case_id, "title": case.title, "vertical": case.vertical,
        "tier": case.tier, "result_tier": result_tier, "called_it": called_it,
        "reward": reward, "is_outlier": case.is_outlier,
    }
    new_history = player["history"] + [outcome]
    new_streak = loss_streak(new_history)

    # Bust: the streak itself ends the run, regardless of cash remaining. Record the
    # losing outcome with no next Case in flight, then show the Cold Case.
    if new_streak >= BUST_THRESHOLD:
        db.record_outcome(player["id"], outcome, new_cash, None)
        return _render_cold_case(request, dict(player, cash=new_cash, history=new_history))

    # Otherwise record the outcome and draw the next Case in one shot.
    next_case = _draw(dict(player, cash=new_cash, history=new_history))
    db.record_outcome(player["id"], outcome, new_cash, next_case.to_dict())

    return templates.TemplateResponse(request, "verdict.html", {
        "case": case,
        "result_tier": result_tier,
        "called_it": called_it,
        "reward": reward,
        "new_cash": new_cash,
        "tier_up": new_tier > old_tier,
        "tier_down": new_tier < old_tier,
        "new_tier": new_tier,
        "new_tier_name": tier_name(new_tier),
        "loss_streak_now": new_streak,
        "bust_threshold": BUST_THRESHOLD,
        **_tier_context(new_cash),
        **ctx,
    })


def _render_cold_case(request: Request, player: dict):
    return templates.TemplateResponse(request, "cold_case.html", {
        "player": player, "cash": player["cash"],
        **_cold_case_context(player), **_tier_context(player["cash"]),
    })


# ---------------------------------------------------------------------------
# Onboarding + home
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    player = current_player(request)
    if not player:
        return templates.TemplateResponse(request, "onboarding.html")
    if _is_busted(player):
        return RedirectResponse(url="/cold-case", status_code=303)

    tctx = _tier_context(player["cash"])
    unlocked = [{"key": v.key, "title": v.title, "tagline": v.tagline, "min_tier": v.min_tier,
                 "unlocked": v.min_tier <= tctx["tier"]}
                for v in (VERTICAL_REGISTRY[k] for k in VERTICAL_ORDER)]

    return templates.TemplateResponse(request, "home.html", {
        "player": player,
        "cash": player["cash"],
        "peak_cash": player["peak_cash"],
        "cases_played": len(player["history"]),
        "has_case": bool(player["case_json"]),
        "verticals": unlocked,
        **tctx,
    })


@app.post("/onboard")
def onboard(nickname: str = Form(...), archetype: str = Form(None)):
    nickname = nickname.strip()[:24] or "Anonymous"
    # Only accept a known archetype; anything else (missing/tampered) stores None,
    # which archetype_weight() treats as neutral — a valid, unbiased run.
    archetype = archetype if archetype in ARCHETYPES else None
    player_id = db.create_player(nickname, STARTING_CASH, archetype)
    resp = RedirectResponse(url="/play", status_code=303)
    resp.set_cookie(PLAYER_COOKIE, player_id, httponly=True, samesite="lax",
                    max_age=60 * 60 * 24 * 365)
    return resp


# ---------------------------------------------------------------------------
# The loop
# ---------------------------------------------------------------------------

@app.get("/play", response_class=HTMLResponse)
def play(request: Request):
    player = current_player(request)
    if not player:
        return RedirectResponse(url="/", status_code=303)
    if _is_busted(player):
        return RedirectResponse(url="/cold-case", status_code=303)

    # Draw a fresh Case if none is in flight (first Case, or just after a verdict).
    if not player["case_json"]:
        case = _draw(player)
        db.set_current_case(player["id"], case.to_dict())
    else:
        case = CaseResult.from_dict(player["case_json"])

    vert = VERTICAL_REGISTRY.get(case.vertical)
    return templates.TemplateResponse(request, "deal.html", {
        "case": case,
        "vertical": vert,
        "cash": player["cash"],
        **_tier_context(player["cash"]),
    })


@app.post("/pick", response_class=HTMLResponse)
def pick(request: Request, choice: str = Form(None)):
    player = current_player(request)
    if not player:
        return RedirectResponse(url="/", status_code=303)
    if not player["case_json"]:
        return RedirectResponse(url="/play", status_code=303)

    case = CaseResult.from_dict(player["case_json"])

    # Affordability gate (Bug 1): if the chosen option is a real purchase priced above
    # the player's cash, reject it server-side — the disabled radio is only a client
    # hint; a crafted POST must not slip a broke player into an option they can't pay
    # for and collect its reward as if it happened. Re-show the deal with the option
    # still locked. Cost is never debited; this only gates selectability.
    if case.pick_type == "binary" and choice in ("a", "b"):
        cost = case.option_a_cost if choice == "a" else case.option_b_cost
        if cost is not None and player["cash"] < cost:
            return templates.TemplateResponse(request, "deal.html", {
                "case": case,
                "vertical": VERTICAL_REGISTRY.get(case.vertical),
                "cash": player["cash"],
                "afford_error": (f"You can't pick that — it costs ${cost:.2f} and you have "
                                 f"${player['cash']:,}. That's the point of this Case."),
                **_tier_context(player["cash"]),
            })

    # Binary Cases record the pick; investigation Cases have nothing to pick.
    case.picked = choice if (case.pick_type == "binary" and choice in ("a", "b")) else None
    db.set_current_case(player["id"], case.to_dict())

    # RECOGNITION Cases (has_bet=False, e.g. all of Trust & Fraud): the pick IS the whole
    # answer, so the Case resolves here and the bet step is skipped entirely — the loop
    # runs DEAL -> YOUR CALL -> EVIDENCE -> VERDICT. Fraud detection is a judgment skill,
    # not a precision skill; there's no number to estimate, so there's nothing to bet on.
    # Scoring is called_it only, via recognition_reward().
    if not case.has_bet:
        old_cash = player["cash"]
        called_it = (case.winner not in ("a", "b")) or case.picked == case.winner
        # Same early-warning escalation as /bet: a 2nd-and-beyond consecutive loss bites 1.5x.
        stakes_mult = 1.5 if loss_streak(player["history"]) >= 1 else 1.0
        reward = recognition_reward(called_it, case.tier, old_cash,
                                    deception_eligible=case.deception_eligible,
                                    stakes_mult=stakes_mult)
        # Reuse the existing result_tier vocabulary rather than inventing labels: a missed
        # recognition Case must read as a loss to loss_streak() (which counts way_off +
        # not called_it), so a scam you fell for feeds the bust streak like any wrong pick.
        result_tier = "nailed_it" if called_it else "way_off"
        return _resolve_case(request, player, case, reward, called_it, result_tier,
                             {"has_bet": False})

    return templates.TemplateResponse(request, "bet.html", {
        "case": case,
        "cash": player["cash"],
        **_tier_context(player["cash"]),
    })


@app.post("/bet", response_class=HTMLResponse)
def bet(request: Request, bet_value: float = Form(...)):
    player = current_player(request)
    if not player:
        return RedirectResponse(url="/", status_code=303)
    if not player["case_json"]:
        return RedirectResponse(url="/play", status_code=303)

    case = CaseResult.from_dict(player["case_json"])
    tier = case.tier
    result_tier, feedback = score_bet(bet_value, case.actual_value)

    old_cash = player["cash"]
    # Early-warning escalation (Locked Refinement #3): once you're already on a loss
    # streak (prior_streak >= 1), the NEXT loss — the 2nd in a row and beyond — bites
    # 1.5x, a ramping danger beat before the bust threshold.
    prior_streak = loss_streak(player["history"])
    stakes_mult = 1.5 if prior_streak >= 1 else 1.0
    reward, called_it, reward_capped = case_reward(
        result_tier, case.picked, case.winner, tier,
        cash=old_cash, actual_value=case.actual_value or 0.0,
        deception_eligible=case.deception_eligible, stakes_mult=stakes_mult,
    )

    return _resolve_case(request, player, case, reward, called_it, result_tier, {
        "has_bet": True,
        "bet_value": round(bet_value, 2),
        "actual_value": case.actual_value,
        "feedback": feedback,
        "reward_capped": reward_capped,
    })


@app.get("/cold-case", response_class=HTMLResponse)
def cold_case(request: Request):
    player = current_player(request)
    if not player:
        return RedirectResponse(url="/", status_code=303)
    if not _is_busted(player):
        return RedirectResponse(url="/", status_code=303)
    return _render_cold_case(request, player)


@app.post("/start-over")
def start_over(request: Request):
    """Bust recovery: spin up a FRESH player row (keeping the nickname) rather than
    resetting the busted one in place, so the old run stays intact as history."""
    player = current_player(request)
    nickname = player["nickname"] if player else "Anonymous"
    # Keep the busted run's archetype — it's a lasting identity, not a per-run reroll.
    archetype = player.get("archetype") if player else None
    player_id = db.create_player(nickname, STARTING_CASH, archetype)
    resp = RedirectResponse(url="/play", status_code=303)
    resp.set_cookie(PLAYER_COOKIE, player_id, httponly=True, samesite="lax",
                    max_age=60 * 60 * 24 * 365)
    return resp


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
