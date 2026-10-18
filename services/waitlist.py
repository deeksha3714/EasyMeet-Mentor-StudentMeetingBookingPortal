"""Waitlist routes: join and leave."""
from flask import flash, redirect, request, session, url_for

from services.waitlist_service import join_waitlist, leave_waitlist_entry
from utils import login_required


@login_required("team")
def waitlist(slot_id):
    reason = request.form.get("reason", "").strip()
    try:
        priority = int(request.form.get("priority", 1))
    except ValueError:
        priority = 1
    if priority not in (1, 2, 3):
        priority = 1

    result, mentor_id = join_waitlist(session["user_id"], slot_id, reason, priority)
    flash({
        "ok": "You joined the waitlist. See My Bookings for your position.",
        "available": "This slot is free now. You can book it directly.",
        "own": "You already hold this slot.",
        "dup": "You are already on the waitlist for this slot.",
        "past": "This slot is in the past.",
        "cancelled": "This slot was cancelled by the mentor.",
        "not_found": "Slot not found.",
        "error": "Something went wrong. You were not added.",
    }[result])
    if mentor_id:
        return redirect(url_for("view_mentor_slots", mentor_id=mentor_id))
    return redirect(url_for("team_dashboard"))


@login_required("team")
def leave_waitlist(waitlist_id):
    changed = leave_waitlist_entry(session["user_id"], waitlist_id)
    flash("You left the waitlist." if changed else "Nothing to remove.")
    return redirect(url_for("my_bookings"))


def init_app(app):
    app.add_url_rule("/team/waitlist/<int:slot_id>", view_func=waitlist, methods=["POST"])
    app.add_url_rule("/team/leave_waitlist/<int:waitlist_id>",
                     view_func=leave_waitlist, methods=["POST"])
