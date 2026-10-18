"""Small shared helpers: DB query helper, MySQL time conversion, auth decorator."""
from datetime import timedelta, time as datetime_time
from functools import wraps

from flask import flash, redirect, session, url_for

from db_config import get_db_connection

"""Convert MySQL TIME values returned as timedelta into datetime.time."""
def mysql_time_to_time(value):
    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds()) % (24 * 60 * 60)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return datetime_time(hours, minutes, seconds)
    return value

"""
Run a SELECT and return all rows as dicts.
Date/time format strings are passed as parameters, never typed inside the SQL.
"""
def query_all(sql, params=()):    
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def login_required(role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("role") != role:
                flash("Please log in first.")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return wrapper
    return decorator
