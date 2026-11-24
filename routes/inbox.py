"""Inbox and AI routes: direct messaging, AI draft generation, and meeting briefings."""
import logging
from flask import (current_app, flash, jsonify, redirect,
                   render_template, request, session, url_for)

from ai_service import create_meeting_briefing, draft_message
from services.inbox_service import (
    get_booking_for_briefing, get_conversation_bookings,
    get_conversation_history, get_mentor_conversations,
    get_saved_briefings, get_team_conversations,
    resolve_conversation_pair, save_chat_message, save_meeting_briefing)
from utils import query_all

logger = logging.getLogger(__name__)


def inbox():
    if session.get("role") not in ("team", "mentor"):
        flash("Please log in to open your inbox.")
        return redirect(url_for("login"))

    role = session["role"]
    user_id = session["user_id"]

    if role == "team":
        conversations = get_team_conversations(user_id)
        requested_id = request.args.get("mentor_id", type=int)
    else:
        conversations = get_mentor_conversations(user_id)
        requested_id = request.args.get("team_id", type=int)

    available_ids = {
        int(row["counterpart_id"]) for row in conversations
    }
    selected_id = (
        requested_id if requested_id in available_ids
        else (int(conversations[0]["counterpart_id"]) if conversations else None)
    )

    messages = []
    bookings = []
    saved_briefings = []

    if selected_id is not None:
        pair = resolve_conversation_pair(selected_id, role, user_id)
        if pair:
            team_id, mentor_id = pair
            messages = get_conversation_history(team_id, mentor_id, limit=100)
            bookings = get_conversation_bookings(team_id, mentor_id)
            saved_briefings = get_saved_briefings(team_id, mentor_id)

    return render_template(
        "inbox.html",
        conversations=conversations,
        selected_id=selected_id,
        messages=messages,
        bookings=bookings,
        saved_briefings=saved_briefings,
        role=role,
    )


def inbox_messages(counterpart_id):
    if session.get("role") not in ("team", "mentor"):
        return jsonify({"error": "Authentication required."}), 401

    pair = resolve_conversation_pair(counterpart_id, session["role"], session["user_id"])
    if not pair:
        return jsonify({"error": "Conversation not found or access denied."}), 403

    team_id, mentor_id = pair
    return jsonify({
        "messages": get_conversation_history(team_id, mentor_id, limit=100)
    })


def send_inbox_message():
    if session.get("role") not in ("team", "mentor"):
        return jsonify({"error": "Authentication required."}), 401

    payload = request.get_json(silent=True) or {}
    try:
        counterpart_id = int(payload.get("counterpart_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Choose a valid conversation."}), 400

    message_text = str(payload.get("message", "")).strip()
    if not message_text:
        return jsonify({"error": "Message cannot be empty."}), 400
    if len(message_text) > 5000:
        return jsonify({"error": "Messages must be 5000 characters or fewer."}), 400

    pair = resolve_conversation_pair(counterpart_id, session["role"], session["user_id"])
    if not pair:
        return jsonify({"error": "Conversation not found or access denied."}), 403

    team_id, mentor_id = pair
    try:
        save_chat_message(team_id, mentor_id, session["role"], message_text)
    except Exception:
        current_app.logger.exception("Unable to save inbox message")
        return jsonify({
            "error": "Message could not be saved. Check the inbox database migration."
        }), 500

    return jsonify({
        "ok": True,
        "messages": get_conversation_history(team_id, mentor_id, limit=100)
    })


def ai_draft_endpoint():
    """Generate an editable inbox draft using Gemini."""
    if session.get("role") not in ("team", "mentor"):
        return jsonify({"success": False, "error": "Authentication required."}), 401

    payload = request.get_json(silent=True) or {}
    try:
        counterpart_id = int(payload.get("counterpart_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Choose a conversation first."}), 400

    draft_text = str(payload.get("draft_text", "")).strip()
    if len(draft_text) > 3000:
        return jsonify({
            "success": False,
            "error": "Draft input must be 3000 characters or fewer."
        }), 400

    tone = str(payload.get("tone", "professional")).strip().lower()
    if tone not in {"professional", "friendly", "concise"}:
        tone = "professional"

    pair = resolve_conversation_pair(counterpart_id, session["role"], session["user_id"])
    if not pair:
        return jsonify({
            "success": False,
            "error": "Conversation not found or access denied."
        }), 403

    try:
        team_id, mentor_id = pair
        history = get_conversation_history(team_id, mentor_id, limit=10)

        sender_role = session["role"]
        sender_name = session.get("name", "")
        if sender_role == "mentor":
            team_info = query_all("SELECT team_name FROM Team WHERE team_id = %s", (team_id,))
            recipient_name = team_info[0]["team_name"] if team_info else "Student Team"
        else:
            mentor_info = query_all("SELECT name FROM Mentor WHERE mentor_id = %s", (mentor_id,))
            recipient_name = mentor_info[0]["name"] if mentor_info else "Mentor"

        result = draft_message(
            role=sender_role,
            draft_text=draft_text,
            tone=tone,
            history=history,
            user_name=sender_name,
            recipient_name=recipient_name,
        )

        if not isinstance(result, str) or not result.strip():
            raise RuntimeError("Gemini returned an empty draft.")

        return jsonify({"success": True, "draft": result.strip()}), 200

    except ValueError as exc:
        current_app.logger.exception("Gemini configuration/input error while drafting")
        return jsonify({"success": False, "error": str(exc)}), 400
    except Exception as exc:
        current_app.logger.exception("Gemini message drafting failed")
        return jsonify({"success": False, "error": str(exc) or "Gemini draft generation failed."}), 502


def ai_briefing_endpoint():
    if session.get("role") not in ("team", "mentor"):
        return jsonify({"error": "Authentication required."}), 401

    if session.get("role") != "mentor":
        return jsonify({"error": "Only mentors can generate meeting briefings."}), 403

    payload = request.get_json(silent=True) or {}
    try:
        booking_id = int(payload.get("booking_id"))
    except (TypeError, ValueError):
        return jsonify({"error": "Choose a valid booking."}), 400

    booking = get_booking_for_briefing(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found."}), 404

    if (
        (session["role"] == "team" and booking["team_id"] != session["user_id"]) or
        (session["role"] == "mentor" and booking["mentor_id"] != session["user_id"])
    ):
        return jsonify({
            "error": "You do not have access to this booking."
        }), 403

    if booking["status"] not in ("confirmed", "completed"):
        return jsonify({
            "error": "Briefings can only be generated for confirmed or completed bookings."
        }), 400

    history = get_conversation_history(booking["team_id"], booking["mentor_id"], limit=20)

    try:
        briefing = create_meeting_briefing(booking, history)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception:
        current_app.logger.exception("Gemini briefing generation failed")
        return jsonify({
            "error": "Gemini could not generate the briefing. Check GEMINI_API_KEY and try again."
        }), 502

    try:
        save_meeting_briefing(booking_id, briefing)
    except Exception:
        current_app.logger.exception("Unable to save meeting briefing")
        return jsonify({
            "error": "Briefing generated but could not be saved to MySQL."
        }), 500

    return jsonify({
        "ok": True,
        "booking_id": booking_id,
        "briefing": briefing
    })


def init_app(app):
    app.add_url_rule("/inbox", endpoint="inbox", view_func=inbox)
    app.add_url_rule("/api/inbox/messages/<int:counterpart_id>", view_func=inbox_messages)
    app.add_url_rule("/api/inbox/messages", view_func=send_inbox_message, methods=["POST"])
    app.add_url_rule("/api/ai/draft", view_func=ai_draft_endpoint, methods=["POST"])
    app.add_url_rule("/api/ai/briefing", view_func=ai_briefing_endpoint, methods=["POST"])
