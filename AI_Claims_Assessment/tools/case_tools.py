import sqlite3
from pathlib import Path

from claims_agent.models import ClaimSummary, NeedsManual, HumanReviewNeeded

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "cases.db"


def _init() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS cases(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                claim_id TEXT NOT NULL,
                status TEXT NOT NULL,
                payload TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP)"""
        )

def create_claim_case(result: ClaimSummary | NeedsManual | HumanReviewNeeded) -> int:
    """Save a case for a human adjuster. Never approves/rejects anything."""
    _init()
    status = result.status if isinstance(result, ClaimSummary) else "PENDING-ADJUSTER"
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            "INSERT INTO cases(claim_id, status, payload) VALUES (?,?,?)",
            (result.claim_id, status, result.model_dump_json()),
        )
    return cur.lastrowid