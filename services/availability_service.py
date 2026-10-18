"""
Mentor availability: slot generation, slot cancellation, and the
slot / calendar queries used by the mentor and team views.
"""
from datetime import datetime, timedelta

import mysql.connector

from config import D_FMT, T_FMT
from db_config import get_db_connection
from services.waitlist_service import ranked_queues
from utils import mysql_time_to_time, query_all


# ---------- mentor lookups ----------
def get_all_mentors():
    return query_all("SELECT mentor_id, name, department FROM Mentor ORDER BY name")


def get_mentor(mentor_id):
    rows = query_all(
        "SELECT mentor_id, name, department FROM Mentor WHERE mentor_id = %s",
        (mentor_id,))
    return rows[0] if rows else None


# ---------- slot listings ----------
def get_mentor_dashboard_slots(mentor_id):
    return query_all("""
        SELECT s.slot_id,
               DATE_FORMAT(s.date, %s) AS slot_date,
               TIME_FORMAT(s.start_time, %s) AS start_t,
               TIME_FORMAT(s.end_time, %s) AS end_t,
               s.status,
               t.team_name,
               b.reason,
               TIMESTAMP(s.date, s.start_time) > NOW() AS is_future,
               (SELECT COUNT(*) FROM Waiting_List w
                 WHERE w.slot_id = s.slot_id AND w.status = 'waiting') AS waiting_count
        FROM Slot s
        LEFT JOIN Booking b ON b.slot_id = s.slot_id AND b.status = 'confirmed'
        LEFT JOIN Team t ON t.team_id = b.team_id
        WHERE s.mentor_id = %s
        ORDER BY s.date, s.start_time
    """, (D_FMT, T_FMT, T_FMT, mentor_id))


def get_mentor_slots_for_team(mentor_id, team_id):
    """Upcoming non-cancelled slots of a mentor, with queue length and
    the given team's position on each slot's waitlist."""
    slots = query_all("""
        SELECT s.slot_id,
               DATE_FORMAT(s.date, %s) AS slot_date,
               DATE_FORMAT(s.date, %s) AS slot_iso,
               TIME_FORMAT(s.start_time, %s) AS start_t,
               TIME_FORMAT(s.end_time, %s) AS end_t,
               s.status,
               b.team_id AS booked_by
        FROM Slot s
        LEFT JOIN Booking b ON b.slot_id = s.slot_id AND b.status = 'confirmed'
        WHERE s.mentor_id = %s AND s.status <> 'cancelled'
          AND TIMESTAMP(s.date, s.start_time) > NOW()
        ORDER BY s.date, s.start_time
    """, (D_FMT, "%Y-%m-%d", T_FMT, T_FMT, mentor_id))

    # waitlist queues for this mentor's slots, in policy order
    ranked = ranked_queues(
        "AND w.slot_id IN (SELECT slot_id FROM Slot WHERE mentor_id = %s)", (mentor_id,))
    queues = {sid: [r["team_id"] for r in q] for sid, q in ranked.items()}

    for s in slots:
        q = queues.get(s["slot_id"], [])
        s["queue_len"] = len(q)
        s["my_pos"] = q.index(team_id) + 1 if team_id in q else None
    return slots


# ---------- calendar events (FullCalendar) ----------
def get_mentor_calendar_events(mentor_id):
    """FullCalendar events for a mentor's own calendar."""
    rows = query_all("""
        SELECT s.slot_id, s.date AS slot_date,
               s.start_time, s.end_time, s.status,
               t.team_name, b.reason
        FROM Slot s
        LEFT JOIN Booking b
          ON b.slot_id = s.slot_id AND b.status = 'confirmed'
        LEFT JOIN Team t ON t.team_id = b.team_id
        WHERE s.mentor_id = %s
        ORDER BY s.date, s.start_time
    """, (mentor_id,))

    events = []
    for row in rows:
        start_dt = datetime.combine(row["slot_date"], mysql_time_to_time(row["start_time"]))
        end_dt = datetime.combine(row["slot_date"], mysql_time_to_time(row["end_time"]))
        available = row["status"] == "available"
        cancelled = row["status"] == "cancelled"
        time_label = start_dt.strftime("%H:%M")
        label = "Cancelled" if cancelled else ("Available" if available else "Booked")
        color = "#6b7280" if cancelled else ("#16a34a" if available else "#dc2626")
        title = f"{label} · {time_label}"
        if not available and not cancelled and row.get("team_name"):
            title += f" · {row['team_name']}"

        events.append({
            "id": str(row["slot_id"]),
            "title": title,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {
                "slotId": row["slot_id"],
                "status": row["status"],
                "teamName": row.get("team_name") or "",
                "reason": row.get("reason") or "",
                "startTime": start_dt.strftime("%H:%M"),
                "endTime": end_dt.strftime("%H:%M"),
            },
        })
    return events


def get_team_calendar_events(mentor_id, my_team_id):
    """Future slot events for a mentor, as seen by a team.
    Other teams' names stay private. Returns None if the mentor doesn't exist."""
    if not query_all("SELECT mentor_id FROM Mentor WHERE mentor_id = %s", (mentor_id,)):
        return None

    rows = query_all("""
        SELECT s.slot_id, s.date AS slot_date,
               s.start_time, s.end_time, s.status,
               b.team_id AS booked_by
        FROM Slot s
        LEFT JOIN Booking b
          ON b.slot_id = s.slot_id AND b.status = 'confirmed'
        WHERE s.mentor_id = %s AND s.status <> 'cancelled'
          AND TIMESTAMP(s.date, s.start_time) > NOW()
        ORDER BY s.date, s.start_time
    """, (mentor_id,))

    events = []
    for row in rows:
        start_dt = datetime.combine(row["slot_date"], mysql_time_to_time(row["start_time"]))
        end_dt = datetime.combine(row["slot_date"], mysql_time_to_time(row["end_time"]))
        available = row["status"] == "available"
        mine = row.get("booked_by") == my_team_id
        time_label = start_dt.strftime("%H:%M")

        if available:
            title = f"Available · {time_label}"
            color = "#16a34a"
        elif mine:
            title = f"Your meeting · {time_label}"
            color = "#2563eb"
        else:
            title = f"Booked · {time_label}"
            color = "#dc2626"

        events.append({
            "id": str(row["slot_id"]),
            "title": title,
            "start": start_dt.isoformat(),
            "end": end_dt.isoformat(),
            "backgroundColor": color,
            "borderColor": color,
            "extendedProps": {
                "slotId": row["slot_id"],
                "status": row["status"],
                "mine": mine,
                "startTime": start_dt.strftime("%H:%M"),
                "endTime": end_dt.strftime("%H:%M"),
            },
        })
    return events


# ---------- slot creation ----------
def generate_slot_times(slot_date, free_from, free_to, duration):
    """Split [free_from, free_to] into back-to-back slots of `duration` minutes."""
    step = timedelta(minutes=duration)
    current = datetime.combine(slot_date, free_from)
    end = datetime.combine(slot_date, free_to)
    slot_times = []
    while current + step <= end:
        slot_times.append((current.time(), (current + step).time()))
        current += step
    return slot_times


def create_availability(mentor_id, slot_date, free_from, free_to, duration, slot_times):
    """Store the availability window and insert non-overlapping slots.
    Returns (ok, created, skipped). Everything is rolled back on error."""
    conn = get_db_connection()
    cursor = conn.cursor()
    created = skipped = 0
    try:
        cursor.execute("""
            INSERT INTO Mentor_Availability
            (mentor_id, day, free_from, free_to, meeting_duration)
            VALUES (%s, %s, %s, %s, %s)
        """, (mentor_id, slot_date.strftime("%A"), free_from, free_to, duration))

        for start_t, end_t in slot_times:
            cursor.execute("""
                SELECT 1 FROM Slot
                WHERE mentor_id = %s AND date = %s AND status <> 'cancelled'
                  AND start_time < %s AND end_time > %s
                LIMIT 1
            """, (mentor_id, slot_date, end_t, start_t))
            if cursor.fetchone():
                skipped += 1
                continue
            cursor.execute("""
                INSERT INTO Slot (mentor_id, date, start_time, end_time)
                VALUES (%s, %s, %s, %s)
            """, (mentor_id, slot_date, start_t, end_t))
            created += 1

        conn.commit()
        return True, created, skipped
    except Exception:
        conn.rollback()
        return False, 0, 0
    finally:
        cursor.close()
        conn.close()


# ---------- slot cancellation (by mentor) ----------
def mentor_cancel_slot(mentor_id, slot_id):
    """Mentor cancels one of THEIR slots (e.g. mentor is busy).
    Returns (result, had_booking, waiting_count).
    result: ok/not_found/already/past/error
    Lock order is Slot -> Booking -> Waiting_List (same as everywhere else)."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        conn.start_transaction()

        # 1) lock the slot (and make sure it belongs to this mentor)
        cursor.execute("""
            SELECT slot_id, status,
                   TIMESTAMP(date, start_time) > NOW() AS is_future
            FROM Slot WHERE slot_id = %s AND mentor_id = %s FOR UPDATE
        """, (slot_id, mentor_id))
        slot = cursor.fetchone()
        if not slot:
            conn.rollback()
            return "not_found", 0, 0
        if slot["status"] == "cancelled":
            conn.rollback()
            return "already", 0, 0
        if not slot["is_future"]:
            conn.rollback()
            return "past", 0, 0

        # 2) cancel the confirmed booking, if any (row is kept, so the team can see why)
        cursor.execute("""UPDATE Booking SET status = 'cancelled'
                          WHERE slot_id = %s AND status = 'confirmed'""", (slot_id,))
        had_booking = cursor.rowcount

        # 3) close the waiting queue for this slot
        cursor.execute("""UPDATE Waiting_List SET status = 'cancelled'
                          WHERE slot_id = %s AND status = 'waiting'""", (slot_id,))
        waiting = cursor.rowcount

        # 4) finally mark the slot itself as cancelled
        cursor.execute("UPDATE Slot SET status = 'cancelled' WHERE slot_id = %s", (slot_id,))

        conn.commit()
        return "ok", had_booking, waiting
    except mysql.connector.Error:
        conn.rollback()
        return "error", 0, 0
    finally:
        cursor.close()
        conn.close()


def cancel_day_slots(mentor_id, day):
    """Cancel every upcoming slot of the mentor on `day`.
    Returns None if there was nothing to cancel, else (cancelled, bookings, waiting)."""
    ids = query_all("""
        SELECT slot_id FROM Slot
        WHERE mentor_id = %s AND date = %s AND status <> 'cancelled'
          AND TIMESTAMP(date, start_time) > NOW()
        ORDER BY slot_id
    """, (mentor_id, day))
    if not ids:
        return None

    cancelled = bookings = waiting = 0
    for row in ids:            # one transaction per slot, always in slot_id order
        result, b, w = mentor_cancel_slot(mentor_id, row["slot_id"])
        if result == "ok":
            cancelled += 1
            bookings += b
            waiting += w
    return cancelled, bookings, waiting
