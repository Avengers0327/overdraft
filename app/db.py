"""
SQLite persistence — zero-config, single file, survives restarts.

The game is one continuous tier-climbing session per player (v8 §6: cash is net
worth, net worth is the tier), so player state IS the run: cash, active traits,
per-Case history, and the current Case in flight. No separate "run" table and no
"vertical complete" — the loop is endless, the tier follows the money.

Swap the connection string for Postgres when you outgrow it; the SQL is
deliberately boring enough to port in an afternoon.
"""
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "overdraft.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS players (
            id          TEXT PRIMARY KEY,
            nickname    TEXT NOT NULL,
            cash        INTEGER NOT NULL,
            traits      TEXT NOT NULL DEFAULT '[]',   -- active Trait keys (v8 §4)
            history     TEXT NOT NULL DEFAULT '[]',   -- per-Case outcomes
            case_json   TEXT,                          -- the Case currently in flight
            peak_cash   INTEGER NOT NULL DEFAULT 0,   -- high-water net worth reached
            archetype   TEXT,                          -- onboarding choice: creator|athlete|entrepreneur
            created_at  TEXT NOT NULL
        );
        """)
        # Migration: add archetype to DBs created before it existed (CREATE TABLE
        # IF NOT EXISTS won't add columns to an already-present table).
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(players)")}
        if "archetype" not in cols:
            conn.execute("ALTER TABLE players ADD COLUMN archetype TEXT")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_player(row: sqlite3.Row) -> dict:
    p = dict(row)
    p["traits"] = json.loads(p["traits"]) if p["traits"] else []
    p["history"] = json.loads(p["history"]) if p["history"] else []
    p["case_json"] = json.loads(p["case_json"]) if p["case_json"] else None
    return p


# ---- players ---------------------------------------------------------------

def create_player(nickname: str, cash: int, archetype: str | None = None) -> str:
    player_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            """INSERT INTO players (id, nickname, cash, traits, history, case_json,
                                    peak_cash, archetype, created_at)
               VALUES (?, ?, ?, '[]', '[]', NULL, ?, ?, ?)""",
            (player_id, nickname, cash, cash, archetype, _now()),
        )
    return player_id


def get_player(player_id: str) -> dict | None:
    with _connect() as conn:
        row = conn.execute("SELECT * FROM players WHERE id = ?", (player_id,)).fetchone()
    return _row_to_player(row) if row else None


def set_current_case(player_id: str, case_json: dict | None) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE players SET case_json = ? WHERE id = ?",
            (json.dumps(case_json) if case_json else None, player_id),
        )


def set_traits(player_id: str, traits: list[str]) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE players SET traits = ? WHERE id = ?",
            (json.dumps(traits), player_id),
        )


# Columns the dev panel (app/dev.py) is allowed to write directly. A whitelist, so a
# dev route can never scribble over id/created_at or invent a column name.
_DEV_WRITABLE = {"cash", "peak_cash", "archetype", "nickname"}
_DEV_WRITABLE_JSON = {"traits", "history", "case_json"}


def dev_set_fields(player_id: str, **fields) -> None:
    """DEV ONLY (gated by settings.DEV_MODE at the route layer) — write player columns
    directly, bypassing game rules. `traits`/`history`/`case_json` are JSON-encoded for
    you; pass native lists/dicts/None. Raises on any column outside the whitelist."""
    sets, values = [], []
    for key, value in fields.items():
        if key in _DEV_WRITABLE_JSON:
            value = json.dumps(value) if value is not None else None
        elif key not in _DEV_WRITABLE:
            raise ValueError(f"dev_set_fields: refusing to write unknown column {key!r}")
        sets.append(f"{key} = ?")
        values.append(value)
    if not sets:
        return
    with _connect() as conn:
        conn.execute(f"UPDATE players SET {', '.join(sets)} WHERE id = ?",
                     (*values, player_id))


def record_outcome(player_id: str, outcome: dict, new_cash: int,
                   next_case_json: dict | None) -> None:
    """Atomically append a Case outcome to history, update cash + peak, and set
    the next Case in flight."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT history, peak_cash FROM players WHERE id = ?", (player_id,)
        ).fetchone()
        history = json.loads(row["history"]) if row and row["history"] else []
        history.append(outcome)
        peak = max(row["peak_cash"] if row else 0, new_cash)
        conn.execute(
            """UPDATE players SET history = ?, cash = ?, peak_cash = ?, case_json = ?
               WHERE id = ?""",
            (json.dumps(history), new_cash, peak,
             json.dumps(next_case_json) if next_case_json else None, player_id),
        )
