"""
Inbox and AI service: conversation resolution, messaging queries,
and meeting briefing storage.
"""
from config import BRIEF_TS_FMT, D_FMT, MSG_TS_FMT, T_FMT
from db_config import get_db_connection
from utils import query_all


def resolve_conversation_pair(counterpart_id, role, user_id):
    """Resolve and authorize the current mentor/team conversation."""
    if role == "team":
        team_id, mentor_id = user_id, counterpart_id
        mentor = query_all(
            "SELECT mentor_id FROM Mentor WHERE mentor_id = %s",
            (mentor_id,)
        )
        if not mentor:
            return None
        return team_id, mentor_id

    if role == "mentor":
        mentor_id, team_id = user_id, counterpart_id
        team = query_all(
            "SELECT team_id FROM Team WHERE team_id = %s",
            (team_id,)
        )
        if not team:
            return None
        return team_id, mentor_id

    return None


def get_conversation_history(team_id, mentor_id, limit=12):
    rows = query_all("""
        SELECT sender, message_text,
               DATE_FORMAT(`timestamp`, %s) AS sent_at
        FROM Chat_Messages
        WHERE team_id = %s AND mentor_id = %s
        ORDER BY message_id DESC
        LIMIT %s
    """, ('%Y-%m-%d %H:%i', team_id, mentor_id, limit))
    return list(reversed(rows))


def get_team_conversations(user_id):
    return query_all("""
        SELECT m.mentor_id AS counterpart_id, m.name AS counterpart_name,
               m.department AS detail,
               (SELECT cm.message_text FROM Chat_Messages cm
                WHERE cm.team_id = %s AND cm.mentor_id = m.mentor_id
                ORDER BY cm.message_id DESC LIMIT 1) AS last_message,
               (SELECT DATE_FORMAT(cm.`timestamp`, %s)
                FROM Chat_Messages cm
                WHERE cm.team_id = %s AND cm.mentor_id = m.mentor_id
                ORDER BY cm.message_id DESC LIMIT 1) AS last_at
        FROM Mentor m ORDER BY m.name
    """, (user_id, MSG_TS_FMT, user_id))


def get_mentor_conversations(user_id):
    return query_all("""
        SELECT t.team_id AS counterpart_id, t.team_name AS counterpart_name,
               'Team conversation' AS detail,
               (SELECT cm.message_text FROM Chat_Messages cm
                WHERE cm.mentor_id = %s AND cm.team_id = t.team_id
                ORDER BY cm.message_id DESC LIMIT 1) AS last_message,
               (SELECT DATE_FORMAT(cm.`timestamp`, %s)
                FROM Chat_Messages cm
                WHERE cm.mentor_id = %s AND cm.team_id = t.team_id
                ORDER BY cm.message_id DESC LIMIT 1) AS last_at
        FROM Team t
        WHERE EXISTS (
            SELECT 1 FROM Booking b
            WHERE b.mentor_id = %s AND b.team_id = t.team_id
        ) OR EXISTS (
            SELECT 1 FROM Chat_Messages cm
            WHERE cm.mentor_id = %s AND cm.team_id = t.team_id
        ) OR t.assigned_mentor_id = %s
        ORDER BY t.team_name
    """, (user_id, MSG_TS_FMT, user_id, user_id, user_id, user_id))


def get_conversation_bookings(team_id, mentor_id):
    return query_all("""
        SELECT b.booking_id, b.status, b.reason,
               DATE_FORMAT(s.date, %s) AS meeting_date,
               TIME_FORMAT(s.start_time, %s) AS start_time,
               TIME_FORMAT(s.end_time, %s) AS end_time
        FROM Booking b JOIN Slot s ON s.slot_id = b.slot_id
        WHERE b.team_id = %s AND b.mentor_id = %s
          AND b.status IN ('confirmed', 'completed')
        ORDER BY s.date DESC, s.start_time DESC
    """, (D_FMT, T_FMT, T_FMT, team_id, mentor_id))


def get_saved_briefings(team_id, mentor_id):
    return query_all("""
        SELECT mb.booking_id, mb.briefing_text,
               DATE_FORMAT(mb.generated_at, %s) AS generated_at
        FROM Meeting_Briefings mb
        JOIN Booking b ON b.booking_id = mb.booking_id
        WHERE b.team_id = %s AND b.mentor_id = %s
        ORDER BY mb.generated_at DESC
    """, (BRIEF_TS_FMT, team_id, mentor_id))


def save_chat_message(team_id, mentor_id, sender_role, message_text):
    """Save a chat message with sender value 'mentor' or 'team'."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        sender_value = "mentor" if sender_role == "mentor" else "team"
        cur.execute("""
            INSERT INTO Chat_Messages
                (team_id, mentor_id, sender, message_text, is_ai_draft)
            VALUES (%s, %s, %s, %s, FALSE)
        """, (team_id, mentor_id, sender_value, message_text))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


def get_booking_for_briefing(booking_id):
    rows = query_all("""
        SELECT b.booking_id, b.team_id, b.mentor_id, b.reason, b.status,
               t.team_name, m.name AS mentor_name,
               DATE_FORMAT(s.date, %s) AS meeting_date,
               TIME_FORMAT(s.start_time, %s) AS start_time,
               TIME_FORMAT(s.end_time, %s) AS end_time
        FROM Booking b
        JOIN Team t ON t.team_id = b.team_id
        JOIN Mentor m ON m.mentor_id = b.mentor_id
        JOIN Slot s ON s.slot_id = b.slot_id
        WHERE b.booking_id = %s
    """, (D_FMT, T_FMT, T_FMT, booking_id))
    return rows[0] if rows else None


def save_meeting_briefing(booking_id, briefing_text):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO Meeting_Briefings (booking_id, briefing_text)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                briefing_text = VALUES(briefing_text),
                generated_at = CURRENT_TIMESTAMP
        """, (booking_id, briefing_text))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
