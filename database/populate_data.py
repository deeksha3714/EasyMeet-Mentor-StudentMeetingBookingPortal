#!/usr/bin/env python3
"""
Populate easymeet database with high-quality, realistic Indian academic test data.
Clean, authentic engineering capstone projects with natural student-faculty interactions.
"""

from datetime import datetime, date, time, timedelta
from werkzeug.security import generate_password_hash
from db_config import get_db_connection

def populate():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    print("Deleting existing rows in tables...")
    cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
    tables = [
        "Meeting_Briefings",
        "Chat_Messages",
        "Waiting_List",
        "Booking",
        "Slot",
        "Mentor_Availability",
        "Team",
        "Mentor"
    ]
    for table in tables:
        cur.execute(f"DELETE FROM {table};")
    cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
    conn.commit()

    common_password = generate_password_hash("password123")

    # 1. Insert Mentors (Realistic Indian faculty members)
    print("Inserting Mentors...")
    mentors_data = [
        (1, "Dr. Rajesh Sharma", "rajesh.sharma@university.edu", common_password, "Computer Science & Engineering"),
        (2, "Prof. Ananya Deshmukh", "ananya.deshmukh@university.edu", common_password, "Information Technology"),
        (3, "Dr. Vikram Malhotra", "vikram.malhotra@university.edu", common_password, "Electronics & Telecommunication"),
        (4, "Prof. Sunita Nair", "sunita.nair@university.edu", common_password, "Computer Engineering"),
        (5, "Dr. Arvind Swaminathan", "arvind.swaminathan@university.edu", common_password, "Data Science & Applications"),
    ]
    for m in mentors_data:
        cur.execute("""
            INSERT INTO Mentor (mentor_id, name, email, password, department)
            VALUES (%s, %s, %s, %s, %s)
        """, m)
    conn.commit()

    # 2. Insert Teams (Indian student capstone teams with assigned mentors)
    print("Inserting Teams...")
    teams_data = [
        (1, "Team CampusPulse", "Aarav Sharma (Lead), Sneha Patel, Rohan Joshi", "campuspulse@students.university.edu", common_password, 1),
        (2, "Team AgroConnect", "Pooja Kulkarni (Lead), Aditya Verma, Nihal Reddy", "agroconnect@students.university.edu", common_password, 2),
        (3, "Team MediTrack", "Kavya Iyer (Lead), Siddharth Nair, Meera Menon", "meditrack@students.university.edu", common_password, 3),
        (4, "Team KiranaPay", "Varun Agarwal (Lead), Ritu Singhania, Aman Gupta", "kiranapay@students.university.edu", common_password, 4),
        (5, "Team ShikshaSetu", "Neha Chawla (Lead), Tanmay Bansal, Aniket Sen", "shikshasetu@students.university.edu", common_password, 5),
        (6, "Team GreenRoute", "Harshvardhan Rao (Lead), Divya Krishnan, Pranav Hegde", "greenroute@students.university.edu", common_password, 1),
    ]
    for t in teams_data:
        cur.execute("""
            INSERT INTO Team (team_id, team_name, members, email, password, assigned_mentor_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, t)
    conn.commit()

    # 3. Insert Mentor Availability
    print("Inserting Mentor Availability...")
    availabilities = [
        # Dr. Rajesh Sharma: Mon (10-13) & Wed (14-17)
        (1, "Monday", "10:00:00", "13:00:00", 30),
        (1, "Wednesday", "14:00:00", "17:00:00", 30),
        # Prof. Ananya Deshmukh: Tue (11-14) & Thu (14:30-17)
        (2, "Tuesday", "11:00:00", "14:00:00", 30),
        (2, "Thursday", "14:30:00", "17:00:00", 30),
        # Dr. Vikram Malhotra: Mon (14-17) & Fri (10-13)
        (3, "Monday", "14:00:00", "17:00:00", 30),
        (3, "Friday", "10:00:00", "13:00:00", 30),
        # Prof. Sunita Nair: Wed (10:30-13) & Fri (14-16:30)
        (4, "Wednesday", "10:30:00", "13:00:00", 30),
        (4, "Friday", "14:00:00", "16:30:00", 30),
        # Dr. Arvind Swaminathan: Tue (14-17) & Thu (10-13)
        (5, "Tuesday", "14:00:00", "17:00:00", 30),
        (5, "Thursday", "10:00:00", "13:00:00", 30),
    ]
    for a in availabilities:
        cur.execute("""
            INSERT INTO Mentor_Availability (mentor_id, day, free_from, free_to, meeting_duration)
            VALUES (%s, %s, %s, %s, %s)
        """, a)
    conn.commit()

    # 4. Insert Slots (Past completed slots + current/upcoming available/booked slots)
    print("Inserting Slots...")
    # Reference date is around late November 2026
    slots = [
        # Dr. Rajesh Sharma (mentor_id = 1)
        # Past:
        (1, 1, "2026-11-16", "10:00:00", "10:30:00", "booked"),
        (2, 1, "2026-11-16", "10:30:00", "11:00:00", "booked"),
        (3, 1, "2026-11-18", "14:00:00", "14:30:00", "booked"),
        # Upcoming:
        (4, 1, "2026-11-25", "14:00:00", "14:30:00", "booked"),
        (5, 1, "2026-11-25", "14:30:00", "15:00:00", "booked"),
        (6, 1, "2026-11-25", "15:00:00", "15:30:00", "available"),
        (7, 1, "2026-11-25", "15:30:00", "16:00:00", "available"),
        (8, 1, "2026-11-30", "10:00:00", "10:30:00", "available"),
        (9, 1, "2026-11-30", "10:30:00", "11:00:00", "available"),
        (10, 1, "2026-11-30", "11:00:00", "11:30:00", "available"),
        (11, 1, "2026-12-02", "14:00:00", "14:30:00", "available"),

        # Prof. Ananya Deshmukh (mentor_id = 2)
        # Past:
        (12, 2, "2026-11-17", "11:00:00", "11:30:00", "booked"),
        # Upcoming:
        (13, 2, "2026-11-24", "11:00:00", "11:30:00", "booked"),
        (14, 2, "2026-11-24", "11:30:00", "12:00:00", "available"),
        (15, 2, "2026-11-24", "12:00:00", "12:30:00", "available"),
        (16, 2, "2026-11-26", "14:30:00", "15:00:00", "available"),
        (17, 2, "2026-11-26", "15:00:00", "15:30:00", "available"),
        (18, 2, "2026-12-01", "11:00:00", "11:30:00", "available"),

        # Dr. Vikram Malhotra (mentor_id = 3)
        # Past:
        (19, 3, "2026-11-20", "10:00:00", "10:30:00", "booked"),
        # Upcoming:
        (20, 3, "2026-11-27", "10:00:00", "10:30:00", "booked"),
        (21, 3, "2026-11-27", "10:30:00", "11:00:00", "available"),
        (22, 3, "2026-11-27", "11:00:00", "11:30:00", "available"),
        (23, 3, "2026-11-30", "14:00:00", "14:30:00", "available"),

        # Prof. Sunita Nair (mentor_id = 4)
        # Past:
        (24, 4, "2026-11-18", "10:30:00", "11:00:00", "booked"),
        # Upcoming:
        (25, 4, "2026-11-25", "10:30:00", "11:00:00", "booked"),
        (26, 4, "2026-11-25", "11:00:00", "11:30:00", "available"),
        (27, 4, "2026-11-25", "11:30:00", "12:00:00", "available"),
        (28, 4, "2026-11-27", "14:00:00", "14:30:00", "available"),

        # Dr. Arvind Swaminathan (mentor_id = 5)
        # Past:
        (29, 5, "2026-11-19", "10:00:00", "10:30:00", "booked"),
        # Upcoming:
        (30, 5, "2026-11-26", "10:00:00", "10:30:00", "booked"),
        (31, 5, "2026-11-26", "10:30:00", "11:00:00", "available"),
        (32, 5, "2026-11-26", "11:00:00", "11:30:00", "available"),
        (33, 5, "2026-12-01", "14:00:00", "14:30:00", "available"),
    ]
    for s in slots:
        cur.execute("""
            INSERT INTO Slot (slot_id, mentor_id, date, start_time, end_time, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, s)
    conn.commit()

    # 5. Insert Bookings
    print("Inserting Bookings...")
    bookings = [
        # (booking_id, team_id, mentor_id, slot_id, reason, status, urgency_tag, booking_time)
        (1, 1, 1, 1, "Project Synopsis & Database Schema Discussion for Mess Feedback System", "completed", "general", "2026-11-14 10:15:00"),
        (2, 6, 1, 2, "Campus Shuttle Route Mapping & Sensor Placement Review", "completed", "general", "2026-11-14 11:30:00"),
        (3, 1, 1, 3, "Rating Scale Normalization & Daily Feedback Input Simplification", "completed", "general", "2026-11-17 15:45:00"),
        (4, 1, 1, 4, "Midterm Demo: Hostel Mess Rating & Feedback Wireframes", "confirmed", "urgent", "2026-11-22 09:30:00"),
        (5, 6, 1, 5, "Shuttle GPS Tracking Interval & Battery Optimization Review", "confirmed", "review", "2026-11-23 11:00:00"),

        (6, 2, 2, 12, "Farmer Survey Review & Mandi Price Integration Flow", "completed", "general", "2026-11-15 14:20:00"),
        (7, 2, 2, 13, "Farmer Market Survey Analysis & WhatsApp Notification Integration", "confirmed", "review", "2026-11-22 16:30:00"),

        (8, 3, 3, 19, "Primary Health Centre OPD Workflow & Patient Queue Architecture", "completed", "general", "2026-11-18 11:10:00"),
        (9, 3, 3, 20, "Prescription QR Code & Patient OTP Verification Flow", "confirmed", "urgent", "2026-11-23 14:00:00"),

        (10, 4, 4, 24, "Kirana Store Inventory Database Design & Barcode Integration Plan", "completed", "general", "2026-11-16 16:00:00"),
        (11, 4, 4, 25, "Local Kirana Store Barcode Scanning & Quick-Billing UI Feedback", "confirmed", "general", "2026-11-23 17:15:00"),

        (12, 5, 5, 29, "Bilingual Content Structure & Question Bank Taxonomy for Rural Schools", "completed", "general", "2026-11-17 12:00:00"),
        (13, 5, 5, 30, "Bilingual Quiz Engine & Web Speech API Demonstration", "confirmed", "urgent", "2026-11-23 10:45:00"),
    ]
    for b in bookings:
        cur.execute("""
            INSERT INTO Booking (booking_id, team_id, mentor_id, slot_id, reason, status, urgency_tag, booking_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, b)
    conn.commit()

    # 6. Insert Waiting List
    print("Inserting Waiting List...")
    # Team 1 is waitlisted on slot 5 (Dr. Rajesh Sharma, Nov 25 14:30-15:00)
    cur.execute("""
        INSERT INTO Waiting_List (waitlist_id, slot_id, team_id, reason, priority, request_time, status)
        VALUES (1, 5, 1, 'Quick 5-minute clarification on database migration script before the departmental lab session', 2, '2026-11-23 15:20:00', 'waiting')
    """)
    conn.commit()

    # 7. Insert Chat Messages (Authentic Indian academic student-mentor correspondence)
    print("Inserting Chat Messages...")
    messages = [
        # Team 1 (CampusPulse) <-> Mentor 1 (Dr. Rajesh Sharma)
        (1, 1, "team", "Good afternoon Sir. We have drafted the initial ER diagram and user authentication flow for the hostel mess feedback module. Should we include daily meal rating or stick to weekly reviews?", "2026-11-14 14:20:00"),
        (1, 1, "mentor", "Good progress, Team CampusPulse. Daily meal rating is fine, but keep the input simple—a 3-tap rating with optional remarks. Avoid lengthy survey forms as students will skip them. Bring your schema draft to our session on Monday.", "2026-11-14 16:05:00"),
        (1, 1, "team", "Thank you Sir! We have simplified the form to a quick tap rating and added food category tags (Breakfast, Lunch, Dinner). We will demonstrate the wireframe in our scheduled slot.", "2026-11-17 16:30:00"),
        (1, 1, "mentor", "Noted. Ensure you test the wireframe on mobile screen sizes as well. Most hostel students will access it directly from their phones.", "2026-11-17 17:10:00"),
        (1, 1, "team", "Yes Sir, we tested it with 10 students in Hostel 3 yesterday. The mobile response was smooth. We have prepared the Figma prototype for tomorrow's review.", "2026-11-24 18:25:00"),
        (1, 1, "mentor", "Good to hear. Bring your laptop with the prototype loaded so we can go through the admin dashboard for mess contractors as well.", "2026-11-24 19:15:00"),

        # Team 6 (GreenRoute) <-> Mentor 1 (Dr. Rajesh Sharma)
        (6, 1, "team", "Respected Sir, we tested GPS location polling from the campus shuttle driver app. Sending updates every 5 seconds drains the phone battery quickly over a 4-hour shift.", "2026-11-22 14:10:00"),
        (6, 1, "mentor", "Hello Harshvardhan. You do not need to poll every 5 seconds when the bus is stationary at a designated campus stop. Implement adaptive polling—poll every 15 seconds while in motion, and increase to 60 seconds when halted.", "2026-11-22 15:30:00"),
        (6, 1, "team", "Thank you Sir! That will reduce battery drain significantly. We are also testing distance-based triggers instead of pure time intervals. We will present the benchmark numbers in our slot on Wednesday.", "2026-11-23 09:40:00"),
        (6, 1, "mentor", "Excellent engineering trade-off. Be sure to document the battery consumption comparison table in your midterm documentation.", "2026-11-23 10:20:00"),

        # Team 2 (AgroConnect) <-> Mentor 2 (Prof. Ananya Deshmukh)
        (2, 2, "team", "Respected Ma'am, we surveyed 15 local vegetable growers near the APMC market. Most requested an SMS or WhatsApp alert for daily wholesale prices because mobile internet connectivity is irregular in the farm yards.", "2026-11-20 11:15:00"),
        (2, 2, "mentor", "Very good field insight, Pooja. SMS gateway integration might have recurring cost implications, so consider WhatsApp notifications via a free tier API or offline caching with SMS fallback. Let's discuss this during our project review.", "2026-11-20 14:00:00"),
        (2, 2, "team", "Understood Ma'am. We have prepared a comparative cost analysis between Twilio SMS and WhatsApp Cloud API for our discussion today.", "2026-11-24 09:10:00"),
        (2, 2, "mentor", "Great. Also prepare a 5-minute slide deck summarizing the farmer survey findings for the department midterm panel.", "2026-11-24 10:00:00"),

        # Team 3 (MediTrack) <-> Mentor 3 (Dr. Vikram Malhotra)
        (3, 3, "team", "Hello Sir, we are finalizing the doctor consultation module. We noticed that elderly patients often misplace paper prescriptions, so we are adding a QR code on the printed slip that links to their test reports.", "2026-11-21 16:30:00"),
        (3, 3, "mentor", "That is a thoughtful feature, Kavya. However, make sure medical records are not openly accessible through a plain QR scan. The link should prompt for a 4-digit OTP sent to the patient's registered phone number for basic privacy.", "2026-11-22 10:15:00"),
        (3, 3, "team", "Yes Sir, we have added mobile OTP verification before displaying sensitive lab reports. We have booked a review slot for Friday to show the patient workflow.", "2026-11-23 11:45:00"),
        (3, 3, "mentor", "Good. Bring your laptop with the local server running so we can test the token generation live.", "2026-11-23 13:00:00"),

        # Team 4 (KiranaPay) <-> Mentor 4 (Prof. Sunita Nair)
        (4, 4, "team", "Good evening Ma'am. We ran a test of the barcode scanning module with a local grocery store owner in Sector 4. The camera scan is fast, but manual quantity entry takes too long during rush hours.", "2026-11-22 17:30:00"),
        (4, 4, "mentor", "Hello Varun. In busy retail settings, shopkeepers prefer quick increment buttons (+1, +5) or repeat barcode scanning rather than typing numbers on a touch keypad. Try implementing keyboard shortcuts and quick-tap quantity chips.", "2026-11-23 09:20:00"),
        (4, 4, "team", "That makes a lot of sense Ma'am. We added +1 and +5 quick buttons, and it cut the checkout time by almost half. We will demo this in Wednesday's session.", "2026-11-23 14:15:00"),
        (4, 4, "mentor", "Glad to hear that. Keep track of your user feedback notes in your project logbook.", "2026-11-23 15:00:00"),

        # Team 5 (ShikshaSetu) <-> Mentor 5 (Dr. Arvind Swaminathan)
        (5, 5, "team", "Sir, for the Hindi-English bilingual quiz engine, we have created 60 sample science questions for Grade 7 and 8 students. Should we also include voice narration for students who have difficulty reading?", "2026-11-21 15:00:00"),
        (5, 5, "mentor", "Text-to-speech is a valuable addition, Neha, but use the browser's built-in Web Speech API rather than third-party cloud APIs to keep the app lightweight and free. Have you checked speech synthesis support on low-end Android tablets?", "2026-11-22 11:30:00"),
        (5, 5, "team", "We tested Web Speech API on an Android 10 tablet and it worked smoothly for Hindi text. We're preparing the demo for Thursday.", "2026-11-23 10:00:00"),
        (5, 5, "mentor", "Good work. Make sure the font size toggle is prominent on the quiz interface as well.", "2026-11-23 12:15:00"),
    ]

    for m in messages:
        cur.execute("""
            INSERT INTO Chat_Messages (team_id, mentor_id, sender, message_text, is_ai_draft, timestamp)
            VALUES (%s, %s, %s, %s, FALSE, %s)
        """, m)
    conn.commit()

    # 8. Insert Meeting Briefings (Executive briefings for past and confirmed meetings)
    print("Inserting Meeting Briefings...")
    briefings = [
        (
            1,
            """### Meeting Briefing: Project Synopsis & Database Schema Review
**Meeting Date:** November 16, 2026 | 10:00 – 10:30 AM
**Participants:** Dr. Rajesh Sharma (Mentor) & Team CampusPulse (Aarav Sharma, Sneha Patel, Rohan Joshi)

#### 1. Discussion Summary
- Reviewed the core data model for the Hostel Mess Feedback & Meal Rating Portal.
- Discussed the granularity of student feedback: agreed that daily per-meal (Breakfast, Lunch, Dinner) star ratings with pre-defined feedback tags (e.g., 'Cold Food', 'Hygiene Issue', 'Well Prepared') will yield higher student engagement than lengthy text surveys.
- Evaluated authentication: verified roll number validation to prevent duplicate ratings for the same meal session while keeping comments anonymous to mess staff.

#### 2. Key Decisions
- Adopt a 1-to-5 star rating system with 3 mandatory category tags.
- Keep feedback submission strictly within 2 hours of meal completion.
- Provide hostel mess wardens with a real-time analytics dashboard showing daily satisfaction trends.

#### 3. Action Items for Next Review
- [x] Refine database schema to include Meal_Sessions and Feedback_Tags tables.
- [x] Create mobile-responsive wireframes for student view in Figma.
- [ ] Prepare preliminary demo for midterm review scheduled for November 25."""
        ),
        (
            2,
            """### Meeting Briefing: Campus Shuttle Tracking & Sensor Interval Review
**Meeting Date:** November 16, 2026 | 10:30 – 11:00 AM
**Participants:** Dr. Rajesh Sharma (Mentor) & Team GreenRoute (Harshvardhan Rao, Divya Krishnan, Pranav Hegde)

#### 1. Discussion Summary
- Evaluated driver smartphone app architecture for live campus shuttle tracking.
- Addressed driver phone battery drain during peak morning and evening shifts.
- Discussed GPS drift when shuttles are parked under concrete bus stop shelters.

#### 2. Key Decisions
- Transition from constant 5-second polling to an adaptive strategy: 15 seconds during transit, 60 seconds when stationary at stops.
- Implement distance-based trigger (every 25 meters of displacement) to smooth trajectory lines on the campus map.

#### 3. Action Items for Next Review
- [x] Implement adaptive geofence polling on the driver test device.
- [ ] Record battery drain percentage over a simulated 2-hour loop.
- [ ] Prepare live tracking map demo for the November 25 review slot."""
        ),
        (
            4,
            """### Executive Meeting Briefing: Midterm Wireframe Demo & Feedback Workflow
**Meeting Date:** November 25, 2026 | 02:00 – 02:30 PM
**Participants:** Dr. Rajesh Sharma (Mentor) & Team CampusPulse (Aarav Sharma, Sneha Patel, Rohan Joshi)

#### 1. Objective & Agenda
Review the completed student mobile UI prototype, test rating submission latency, and inspect the mess warden administrative oversight panel.

#### 2. Pre-Meeting Progress Notes
- Team completed mobile-first wireframes and conducted an informal pilot with 10 hostel residents.
- Average rating submission time was under 8 seconds.
- Identified need for multilingual support (English / Hindi) on the rating screen.

#### 3. Discussion Points & Checklist
1. **Pilot Feedback Analysis:** Review student responses regarding meal satisfaction tags.
2. **Admin Moderation:** Verify that abusive or non-constructive remarks can be flagged by the hostel warden before appearing on public mess noticeboards.
3. **Midterm Deliverables:** Finalize project report chapters 1 through 3 and architecture diagrams."""
        ),
        (
            6,
            """### Meeting Briefing: APMC Mandi Survey & Produce Marketplace Architecture
**Meeting Date:** November 17, 2026 | 11:00 – 11:30 AM
**Participants:** Prof. Ananya Deshmukh (Mentor) & Team AgroConnect (Pooja Kulkarni, Aditya Verma, Nihal Reddy)

#### 1. Discussion Summary
- Reviewed field survey findings from 15 agricultural producers across the local APMC yard.
- Confirmed that regional vegetable and fruit farmers primarily rely on voice calls and WhatsApp rather than complex web dashboards.
- Discussed price discovery mechanism: syncing wholesale prices daily from data.gov.in AGMARKNET API.

#### 2. Key Decisions
- Prioritize high-contrast mobile UI with regional language labels (Marathi & Hindi).
- Use local device storage for price lists so farmers can check yesterday's rates even when offline.

#### 3. Action Items for Next Review
- [x] Compile cost comparison between Twilio SMS and WhatsApp Cloud API.
- [ ] Connect prototype to AGMARKNET sample price feed.
- [ ] Prepare 5-minute presentation for department midterm evaluation."""
        ),
        (
            8,
            """### Meeting Briefing: Primary Health Centre OPD Architecture & Queue Management
**Meeting Date:** November 20, 2026 | 10:00 – 10:30 AM
**Participants:** Dr. Vikram Malhotra (Mentor) & Team MediTrack (Kavya Iyer, Siddharth Nair, Meera Menon)

#### 1. Discussion Summary
- Analyzed patient waiting times at rural Primary Health Centres (PHCs).
- Reviewed digital token generation flow to prevent physical crowding at OPD registration counters.
- Discussed privacy regulations concerning prescription storage and diagnostic reports.

#### 2. Key Decisions
- Digital tokens will be displayed on a lobby TV monitor via a lightweight browser dashboard.
- Prescription QR codes must require a 4-digit SMS OTP verification before unlocking patient medical history.

#### 3. Action Items for Next Review
- [x] Integrate OTP verification screen in the patient lookup portal.
- [ ] Implement live queue token calling sound alert for the doctor desk view.
- [ ] Demo end-to-end patient registration and prescription generation on Friday."""
        ),
        (
            10,
            """### Meeting Briefing: Neighborhood Kirana Store Inventory & Quick Billing
**Meeting Date:** November 18, 2026 | 10:30 – 11:00 AM
**Participants:** Prof. Sunita Nair (Mentor) & Team KiranaPay (Varun Agarwal, Ritu Singhania, Aman Gupta)

#### 1. Discussion Summary
- Evaluated barcode scanning performance using standard webcams and smartphone cameras.
- Identified bottleneck during peak grocery store footfall: typing item quantities slowed down billing.
- Discussed daily ledger (Khata) functionality for credit customers.

#### 2. Key Decisions
- Add quick increment buttons (+1, +5, +10) and keyboard shortcuts to drastically speed up item entry.
- Implement SQLite/IndexedDB local caching so the billing counter works during internet outages.

#### 3. Action Items for Next Review
- [x] Benchmark billing time per 10 items before and after quick quantity chips.
- [ ] Implement PDF receipt download and WhatsApp share link for customers.
- [ ] Present live billing demonstration in Wednesday's review."""
        ),
        (
            12,
            """### Meeting Briefing: Bilingual Educational Content & Quiz Engine Taxonomy
**Meeting Date:** November 19, 2026 | 10:00 – 10:30 AM
**Participants:** Dr. Arvind Swaminathan (Mentor) & Team ShikshaSetu (Neha Chawla, Tanmay Bansal, Aniket Sen)

#### 1. Discussion Summary
- Structured Grade 7 & 8 Science curriculum question bank in bilingual format (English and Hindi).
- Evaluated voice narration for students with literacy challenges in rural schools.
- Reviewed quiz performance tracking and gamified achievement badges.

#### 2. Key Decisions
- Utilize the browser's built-in Web Speech API to enable zero-cost text-to-speech for Hindi narration.
- Ensure the app layout maintains readability on low-cost 7-inch Android tablets.

#### 3. Action Items for Next Review
- [x] Test Web Speech API Hindi pronunciation across Chrome and Firefox on mobile.
- [ ] Finalize 60-question sample science quiz set.
- [ ] Prepare live speech synthesis demo for Thursday's scheduled slot."""
        ),
    ]

    for b in briefings:
        cur.execute("""
            INSERT INTO Meeting_Briefings (booking_id, briefing_text)
            VALUES (%s, %s)
        """, b)
    conn.commit()

    cur.close()
    conn.close()
    print("Database population completed successfully!")

if __name__ == "__main__":
    populate()
