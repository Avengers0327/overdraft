"""
Content package — one module per Vertical.

Importing this package imports every vertical module, and each module's import
side effects register its Case templates (@register_case) and its Vertical
(register_vertical). main.py imports this package once at startup so the
registries are fully populated before any request is served.

Add a new vertical by dropping a module here and importing it below — no central
list to edit anywhere else. This is the "open" in "open vertical system" (v8 §3).
"""
# Registration order = board display order (v8 §3). Import in that order.
# Everyday Money leads: it's the open (Tier 1) baseline vertical, the curriculum's
# foundation, so it sits first on the board.
from app.content import everyday_money    # noqa: F401  (import side effects)
from app.content import creator_economy   # noqa: F401
from app.content import trades_hustles    # noqa: F401
from app.content import borrowed_money    # noqa: F401
from app.content import real_estate       # noqa: F401
from app.content import insurance         # noqa: F401
from app.content import startup_world     # noqa: F401
from app.content import sports_nil        # noqa: F401

__all__ = [
    "everyday_money", "creator_economy", "trades_hustles", "borrowed_money",
    "real_estate", "insurance", "startup_world", "sports_nil",
]
