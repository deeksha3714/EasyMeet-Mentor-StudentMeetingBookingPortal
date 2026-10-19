
"""Waiting queue: scheduling policy (FCFS / Priority + Aging), ranking,
joining and leaving the waitlist."""

import  mysql.connector

from config import AGING_SECONDS, DEFAULT_POLICY, WAIT_COLS
from db_config import get_db_connection
from utils import query_all


VALID_POLICIES =  ("FCFS", "PRIORITY")
_policy = DEFAULT_POLICY


# ---------- Policy state ----------

def get_policy():
    return _policy


def change_policy(name):
    """Returns True if the policy was changed."""
    global _policy

    name = name.upper() if isinstance(name, str) else ""

    if name in VALID_POLICIES:
        _policy = name
        return True

    return False


# ---------- Scheduling logic ----------

def score(r):
    """Effective priority = base priority + aging bonus."""
    return r["priority"] + r["waited"] / AGING_SECONDS


def rank_key(r):
    """Smaller key means the request is served earlier."""
    if _policy == "FCFS":
        return (r["request_time"], r["waitlist_id"])

    # Higher effective priority first; ties use FCFS.
    return (-score(r), r["request_time"], r["waitlist_id"])


def  ranked_queues(extra_where="", params=()):
    """Return {slot_id: [waiting rows in service order]}."""
    rows = query_all(
        WAIT_COLS + " WHERE w.status = 'waiting' " + extra_where,
        params
    )

    queues = {}

    for r in sorted(rows, key=rank_key):
        r["score"] = round(score(r), 1)
        queues.setdefault(r["slot_id"], []).append(r)

    return queues


def  queue_positions():
    """Return {waitlist_id: position in its slot's queue}."""
    positions = {}

    for queue in ranked_queues().values():
        for position, row in enumerate(queue, start=1):
            positions[row["waitlist_id"]] = position

    return positions


# ---------- Waiting-list operations ----------

def join_waitlist(team_id, slot_id, reason, priority=1):
    """
    Returns (result, mentor_id).

    Possible results:
    ok, available, own, dup, past, cancelled, not_found, error
    """
    if priority not in (1, 2, 3):
        priority = 1

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        conn.start_transaction()

        # Lock the slot to coordinate concurrent requests.
        cursor.execute("""
            SELECT slot_id, mentor_id, status,
                   TIMESTAMP(date, start_time) > NOW() AS is_future
            FROM Slot
            WHERE slot_id = %s
            FOR UPDATE
        """, (slot_id,))

        slot = cursor.fetchone()

        if not slot:
            conn.rollback()
            return "not_found", None

        mentor_id = slot["mentor_id"]

        if not slot["is_future"]:
            conn.rollback()
            return "past", mentor_id

        if slot["status"] == "cancelled":
            conn.rollback()
            return "cancelled", mentor_id

        if slot["status"] == "available":
            conn.rollback()
            return "available", mentor_id

        # Prevent a team from waiting for a slot it already owns.
        cursor.execute("""
            SELECT 1
            FROM Booking
            WHERE slot_id = %s
              AND team_id = %s
              AND status = 'confirmed'
        """, (slot_id, team_id))

        if cursor.fetchone():
            conn.rollback()
            return "own", mentor_id

        # Prevent duplicate active waiting-list requests.
        cursor.execute("""
            SELECT 1
            FROM Waiting_List
            WHERE slot_id = %s
              AND team_id = %s
              AND status = 'waiting'
        """, (slot_id, team_id))

        if cursor.fetchone():
            conn.rollback()
            return "dup", mentor_id

        cursor.execute("""
            INSERT INTO Waiting_List
                (slot_id, team_id, reason, priority)
            VALUES (%s, %s, %s, %s)
        """, (slot_id, team_id, reason, priority))

        conn.commit()
        return "ok", mentor_id

    except mysql.connector.Error:
        conn.rollback()
        return "error", None

    finally:
        cursor.close()
        conn.close()


def leave_waitlist_entry(team_id, waitlist_id):
    """Expire an active request owned by the team."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            UPDATE Waiting_List
            SET status = 'expired'
            WHERE waitlist_id = %s
              AND team_id = %s
              AND status = 'waiting'
        """, (waitlist_id, team_id))

        conn.commit()
        return cursor.rowcount

    except mysql.connector.Error:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()
