"""Booking engine: booking, cancelling (with auto-promotion from the waitlist),
and the read queries for 'My Bookings' and the status page."""
import time
from datetime import date

import mysql.connector

from config import (DEMO_DELAY, D_FMT, PRIORITY_LABELS, T_FMT, TS_FMT,
                    URGENCY_TAG, WAIT_COLS)
from db_config import get_db_connection
from services.waitlist_service import queue_positions, rank_key, ranked_queues
from utils import query_all


# =====================================================
# Booking engine (mutual exclusion + atomicity)
# =====================================================
def book_slot(team_id, slot_id, reason):
    """Returns (result, mentor_id). result: ok/taken/past/cancelled/not_found/error"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        # LOCK the slot row: other transactions on this slot wait here
        cursor.execute("""
            SELECT slot_id, mentor_id, status,
                   TIMESTAMP(date, start_time) > NOW() AS is_future
            FROM Slot WHERE slot_id = %s FOR UPDATE
        """, (slot_id,))
        slot = cursor.fetchone()

        if DEMO_DELAY:
            time.sleep(DEMO_DELAY)   # demo only: holds the lock

        if not slot:
            conn.rollback()
            return "not_found", None
        if not slot["is_future"]:
            conn.rollback()
            return "past", slot["mentor_id"]
        if slot["status"] == "cancelled":
            conn.rollback()
            return "cancelled", slot["mentor_id"]
        if slot["status"] != "available":
            conn.rollback()
            return "taken", slot["mentor_id"]

        cursor.execute("""
            INSERT INTO Booking (team_id, mentor_id, slot_id, reason)
            VALUES (%s, %s, %s, %s)
        """, (team_id, slot["mentor_id"], slot_id, reason))
        cursor.execute("UPDATE Slot SET status = 'booked' WHERE slot_id = %s", (slot_id,))

        conn.commit()               # lock released
        return "ok", slot["mentor_id"]
    except mysql.connector.Error:
        conn.rollback()
        return "error", None
    finally:
        cursor.close()
        conn.close()


def cancel_booking(team_id, booking_id):
    """Returns result: promoted/freed/past/not_found/error.
    Lock order is always Slot -> Booking -> Waiting_List (prevents deadlock)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        cursor.execute("""SELECT slot_id FROM Booking
                          WHERE booking_id = %s AND team_id = %s AND status = 'confirmed'""",
                       (booking_id, team_id))
        row = cursor.fetchone()
        if not row:
            conn.rollback()
            return "not_found"
        slot_id = row["slot_id"]

        # 1) lock the slot first
        cursor.execute("""SELECT slot_id,
                                 TIMESTAMP(date, start_time) > NOW() AS is_future
                          FROM Slot WHERE slot_id = %s FOR UPDATE""", (slot_id,))
        slot = cursor.fetchone()
        if not slot["is_future"]:
            conn.rollback()
            return "past"

        # 2) re-check the booking now that we hold the lock
        cursor.execute("""SELECT booking_id FROM Booking
                          WHERE booking_id = %s AND team_id = %s AND status = 'confirmed'
                          FOR UPDATE""", (booking_id, team_id))
        if not cursor.fetchone():
            conn.rollback()
            return "not_found"

        # 3) pick the next team using the active policy (FCFS or Priority + Aging)
        cursor.execute(WAIT_COLS + " WHERE w.slot_id = %s AND w.status = 'waiting' FOR UPDATE",
                       (slot_id,))
        rows = cursor.fetchall()
        nxt = min(rows, key=rank_key) if rows else None

        if nxt:
            # hand the same booking row to the chosen team (slot stays 'booked')
            cursor.execute("""UPDATE Booking
                              SET team_id = %s, reason = %s, booking_time = NOW(),
                                  urgency_tag = %s
                              WHERE booking_id = %s""",
                           (nxt["team_id"], nxt["reason"],
                            URGENCY_TAG.get(nxt["priority"], "general"), booking_id))
            cursor.execute("UPDATE Waiting_List SET status = 'promoted' WHERE waitlist_id = %s",
                           (nxt["waitlist_id"],))
            result = "promoted"
        else:
            cursor.execute("DELETE FROM Booking WHERE booking_id = %s", (booking_id,))
            cursor.execute("UPDATE Slot SET status = 'available' WHERE slot_id = %s", (slot_id,))
            result = "freed"

        conn.commit()
        return result
    except mysql.connector.Error:
        conn.rollback()
        return "error"
    finally:
        cursor.close()
        conn.close()


# =====================================================
# Read queries for pages
# =====================================================
def get_team_bookings(team_id):
    """Returns (bookings, waits, cancelled) for the 'My Bookings' page."""
    bookings = query_all("""
        SELECT b.booking_id, m.name AS mentor_name,
               DATE_FORMAT(s.date, %s) AS slot_date,
               TIME_FORMAT(s.start_time, %s) AS start_t,
               TIME_FORMAT(s.end_time, %s) AS end_t,
               b.reason,
               TIMESTAMP(s.date, s.start_time) > NOW() AS is_future
        FROM Booking b
        JOIN Slot s ON s.slot_id = b.slot_id
        JOIN Mentor m ON m.mentor_id = b.mentor_id
        WHERE b.team_id = %s AND b.status = 'confirmed'
        ORDER BY s.date, s.start_time
    """, (D_FMT, T_FMT, T_FMT, team_id))

    waits = query_all("""
        SELECT w.waitlist_id, m.name AS mentor_name,
               DATE_FORMAT(s.date, %s) AS slot_date,
               TIME_FORMAT(s.start_time, %s) AS start_t,
               TIME_FORMAT(s.end_time, %s) AS end_t,
               w.reason, w.priority
        FROM Waiting_List w
        JOIN Slot s ON s.slot_id = w.slot_id
        JOIN Mentor m ON m.mentor_id = s.mentor_id
        WHERE w.team_id = %s AND w.status = 'waiting'
        ORDER BY s.date, s.start_time
    """, (D_FMT, T_FMT, T_FMT, team_id))

    pos = queue_positions()
    for w in waits:
        w["queue_pos"] = pos.get(w["waitlist_id"])
        w["priority_label"] = PRIORITY_LABELS.get(w["priority"], "General")

    # upcoming sessions the mentor cancelled (confirmed bookings and waitlist requests)
    cancelled_bookings = query_all("""
        SELECT m.name AS mentor_name,
               DATE_FORMAT(s.date, %s) AS slot_date,
               TIME_FORMAT(s.start_time, %s) AS start_t,
               TIME_FORMAT(s.end_time, %s) AS end_t,
               b.reason
        FROM Booking b
        JOIN Slot s ON s.slot_id = b.slot_id
        JOIN Mentor m ON m.mentor_id = b.mentor_id
        WHERE b.team_id = %s AND b.status = 'cancelled'
          AND TIMESTAMP(s.date, s.start_time) > NOW()
        ORDER BY s.date, s.start_time
    """, (D_FMT, T_FMT, T_FMT, team_id))
    cancelled_waits = query_all("""
        SELECT m.name AS mentor_name,
               DATE_FORMAT(s.date, %s) AS slot_date,
               TIME_FORMAT(s.start_time, %s) AS start_t,
               TIME_FORMAT(s.end_time, %s) AS end_t,
               w.reason
        FROM Waiting_List w
        JOIN Slot s ON s.slot_id = w.slot_id
        JOIN Mentor m ON m.mentor_id = s.mentor_id
        WHERE w.team_id = %s AND w.status = 'cancelled'
          AND TIMESTAMP(s.date, s.start_time) > NOW()
        ORDER BY s.date, s.start_time
    """, (D_FMT, T_FMT, T_FMT, team_id))
    cancelled = ([dict(c, kind="Booking") for c in cancelled_bookings] +
                 [dict(c, kind="Waitlist request") for c in cancelled_waits])

    return bookings, waits, cancelled


def get_status_snapshot():
    """Data for the live status page: all upcoming slots and waiting teams."""
    slots = query_all("""
        SELECT s.slot_id, m.name AS mentor_name,
               DATE_FORMAT(s.date, %s) AS slot_date,
               TIME_FORMAT(s.start_time, %s) AS start_t,
               TIME_FORMAT(s.end_time, %s) AS end_t,
               s.status, t.team_name AS holder, b.reason
        FROM Slot s
        JOIN Mentor m ON m.mentor_id = s.mentor_id
        LEFT JOIN Booking b ON b.slot_id = s.slot_id AND b.status = 'confirmed'
        LEFT JOIN Team t ON t.team_id = b.team_id
        WHERE s.date >= %s AND s.status <> 'cancelled'
        ORDER BY s.date, s.start_time, s.slot_id
    """, (D_FMT, T_FMT, T_FMT, date.today()))

    waits = query_all("""
        SELECT w.waitlist_id, w.slot_id, t.team_name, w.priority,
               DATE_FORMAT(w.request_time, %s) AS requested_at
        FROM Waiting_List w
        JOIN Team t ON t.team_id = w.team_id
        JOIN Slot s ON s.slot_id = w.slot_id
        WHERE w.status = 'waiting' AND s.date >= %s
    """, (TS_FMT, date.today()))

    pos = queue_positions()
    scores = {r["waitlist_id"]: r["score"]
              for q in ranked_queues().values() for r in q}
    for w in waits:
        w["queue_pos"] = pos.get(w["waitlist_id"])
        w["score"] = scores.get(w["waitlist_id"])
        w["priority_label"] = PRIORITY_LABELS.get(w["priority"], "General")
    waits.sort(key=lambda w: (w["slot_id"], w["queue_pos"] or 0))

    booked = sum(1 for s in slots if s["status"] == "booked")
    return dict(slots=slots, waits=waits, total=len(slots),
                booked=booked, available=len(slots) - booked)
