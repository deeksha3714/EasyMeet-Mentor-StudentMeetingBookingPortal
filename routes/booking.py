"""Team-side routes: browse mentors/slots, book, my bookings, cancel, status page."""
from flask import flash, jsonify, redirect, render_template, request, session, url_for

from services.availability_service import (
    get_all_mentors, get_mentor, get_mentor_slots_for_team, get_team_calendar_events)
from services.booking_service import (
    book_slot, cancel_booking, get_status_snapshot, get_team_bookings)
from utils import login_required


@login_required("team")
def team_dashboard():
    return render_template("team_dashboard.html", mentors=get_all_mentors())


@login_required("team")
def team_mentor_calendar_events(mentor_id):
    """Future slot events for the selected mentor. Other teams' names stay private."""
    events = get_team_calendar_events(mentor_id, session["user_id"])
    if events is None:
        return jsonify({"error": "Mentor not found"}), 404
    return jsonify(events)


@login_required("team")
def view_mentor_slots(mentor_id):
    mentor = get_mentor(mentor_id)
    if not mentor:
        flash("Mentor not found.")
        return redirect(url_for("team_dashboard"))

    my_team = session["user_id"]
    slots = get_mentor_slots_for_team(mentor_id, my_team)
    return render_template("mentor_slots.html", mentor=mentor,
                           slots=slots, my_team_id=my_team)


@login_required("team")
def book(slot_id):
    reason = request.form.get("reason", "").strip()
    result, mentor_id = book_slot(session["user_id"], slot_id, reason)
    flash({
        "ok": "Slot booked successfully!",
        "taken": "Sorry, this slot was just taken by another team. You can join the waitlist.",
        "past": "This slot is in the past and cannot be booked.",
        "cancelled": "This slot was cancelled by the mentor.",
        "not_found": "Slot not found.",
        "error": "Something went wrong. Nothing was booked.",
    }[result])
    if mentor_id:
        return redirect(url_for("view_mentor_slots", mentor_id=mentor_id))
    return redirect(url_for("team_dashboard"))


@login_required("team")
def my_bookings():
    bookings, waits, cancelled = get_team_bookings(session["user_id"])
    return render_template("my_bookings.html", bookings=bookings, waits=waits,
                           cancelled=cancelled)


@login_required("team")
def cancel(booking_id):
    result = cancel_booking(session["user_id"], booking_id)
    flash({
        "promoted": "Booking cancelled. The slot was given to the next team on the waitlist.",
        "freed": "Booking cancelled. The slot is available again.",
        "past": "Past bookings cannot be cancelled.",
        "not_found": "Booking not found.",
        "error": "Something went wrong. Nothing was changed.",
    }[result])
    return redirect(url_for("my_bookings"))


def status():
    """Live demo screen (any logged-in user)."""
    if "role" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    return render_template("status.html", **get_status_snapshot())


def init_app(app):
    app.add_url_rule("/team/dashboard", view_func=team_dashboard)
    app.add_url_rule("/api/team/mentor/<int:mentor_id>/calendar-events",
                     view_func=team_mentor_calendar_events)
    app.add_url_rule("/team/mentor/<int:mentor_id>", view_func=view_mentor_slots)
    app.add_url_rule("/team/book/<int:slot_id>", view_func=book, methods=["POST"])
    app.add_url_rule("/team/my_bookings", view_func=my_bookings)
    app.add_url_rule("/team/cancel/<int:booking_id>", view_func=cancel, methods=["POST"])
    app.add_url_rule("/status", view_func=status)
