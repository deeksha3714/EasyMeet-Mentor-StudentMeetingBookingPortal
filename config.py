"""
Program Constants and Configuration.
"""
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-only-change-this-secret-before-deploying")

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
MSG_TS_FMT = '%d %b, %H:%i'
BRIEF_TS_FMT = '%d %b %Y, %H:%i'

WAIT_COLS = """SELECT w.waitlist_id, w.slot_id, w.team_id, w.reason, w.priority,
                      w.request_time,
                      TIMESTAMPDIFF(SECOND, w.request_time, NOW()) AS waited
               FROM Waiting_List w"""
