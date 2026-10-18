"""
Program Constants.
"""
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-to-any-long-random-string")

DEMO_DELAY = 0

# ---------- scheduling policy ----------
DEFAULT_POLICY = "PRIORITY"  
AGING_SECONDS = 60            
PRIORITY_LABELS = {3: "Urgent", 2: "Review", 1: "General"}
URGENCY_TAG = {3: "urgent", 2: "review", 1: "general"}

# date/time format strings, passed to MySQL as parameters
D_FMT = '%d %b %Y'
T_FMT = '%H:%i'
TS_FMT = '%H:%i:%s'

WAIT_COLS = """SELECT w.waitlist_id, w.slot_id, w.team_id, w.reason, w.priority,
                      w.request_time,
                      TIMESTAMPDIFF(SECOND, w.request_time, NOW()) AS waited
               FROM Waiting_List w"""
