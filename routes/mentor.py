"""Mentor routes: dashboard, calendar API, availability, cancellations, policy."""
from datetime import date, datetime

from flask import flash, jsonify, redirect, render_template, request, session, url_for

from services.availability_service import (
    cancel_day_slots, create_availability, generate_slot_times,
    get_mentor_calendar_events, get_mentor_dashboard_slots, mentor_cancel_slot)
from services.waitlist_service import change_policy
from utils import login_required


@login_required("mentor")
def mentor_dashboard():
    slots = get_mentor_dashboard_slots(session["user_id"])
    return render_template("mentor_dashboard.html", slots=slots,
                           today=date.today().isoformat())


@login_required("mentor")
def mentor_calendar_events():
    """FullCalendar events for the currently logged-in mentor."""
    return jsonify(get_mentor_calendar_events(session["user_id"]))


@login_required("mentor")
def set_policy(name):
    if change_policy(name):
        flash(f"Scheduling policy set to {name}.")
    return redirect(url_for("mentor_dashboard"))


@login_required("mentor")
def cancel_slot(slot_id):
    result, had_booking, waiting = mentor_cancel_slot(session["user_id"], slot_id)
    if result == "ok":
        msg = "Slot cancelled."
        if had_booking:
            msg += " The booked team will see this in My Bookings."
        if waiting:
            msg += f" {waiting} waitlisted team(s) were removed from the queue."
        flash(msg)
    else:
        flash({
            "not_found": "Slot not found.",
            "already": "This slot is already cancelled.",
            "past": "Past slots cannot be cancelled.",
            "error": "Something went wrong. Nothing was changed.",
        }[result])
    return redirect(url_for("mentor_dashboard"))


@login_required("mentor")
def cancel_day():
    """Mentor is busy for a whole day: cancel every upcoming slot on that date."""
    try:
        day = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
    except (ValueError, KeyError):
        flash("Please choose a valid date.")
        return redirect(url_for("mentor_dashboard"))

    outcome = cancel_day_slots(session["user_id"], day)
    if outcome is None:
        flash("No upcoming slots to cancel on that date.")
        return redirect(url_for("mentor_dashboard"))

    cancelled, bookings, waiting = outcome
    flash(f"{cancelled} slot(s) cancelled on {day.strftime('%d %b %Y')}. "
          f"{bookings} booked team(s) affected, {waiting} waitlist request(s) closed.")
    return redirect(url_for("mentor_dashboard"))


@login_required("mentor")
def add_availability():
    mentor_id = session["user_id"]

    try:
        slot_date = datetime.strptime(request.form["date"], "%Y-%m-%d").date()
        free_from = datetime.strptime(request.form["free_from"], "%H:%M").time()
        free_to = datetime.strptime(request.form["free_to"], "%H:%M").time()
        duration = int(request.form["duration"])
    except (ValueError, KeyError):
        flash("Invalid input. Please check all fields.")
        return redirect(url_for("mentor_dashboard"))

    if slot_date < date.today():
        flash("Date cannot be in the past.")
        return redirect(url_for("mentor_dashboard"))
    if free_to <= free_from:
        flash("'Free to' must be later than 'Free from'.")
        return redirect(url_for("mentor_dashboard"))
    if duration < 5 or duration > 120:
        flash("Duration must be between 5 and 120 minutes.")
        return redirect(url_for("mentor_dashboard"))

    slot_times = generate_slot_times(slot_date, free_from, free_to, duration)
    if not slot_times:
        flash("The time window is shorter than one meeting duration.")
        return redirect(url_for("mentor_dashboard"))

    ok, created, skipped = create_availability(
        mentor_id, slot_date, free_from, free_to, duration, slot_times)
    if ok:
        flash(f"{created} new slot(s) created, {skipped} skipped (overlap/duplicate).")
    else:
        flash("Something went wrong. No slots were saved.")
    return redirect(url_for("mentor_dashboard"))


def init_app(app):
    app.add_url_rule("/mentor/dashboard", view_func=mentor_dashboard)
    app.add_url_rule("/api/mentor/calendar-events", view_func=mentor_calendar_events)
    app.add_url_rule("/mentor/policy/<name>", view_func=set_policy, methods=["POST"])
    app.add_url_rule("/mentor/cancel_slot/<int:slot_id>", view_func=cancel_slot, methods=["POST"])
    app.add_url_rule("/mentor/cancel_day", view_func=cancel_day, methods=["POST"])
    app.add_url_rule("/mentor/add_availability", view_func=add_availability, methods=["POST"])
