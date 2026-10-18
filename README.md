# Mentor Booking Portal

A web-based mentor booking and scheduling system built using **Python, Flask, MySQL, HTML, CSS, and JavaScript**. The portal allows teams to view mentor availability, book meeting slots, manage bookings, and join waiting lists when slots are unavailable.

The project demonstrates practical applications of **Operating Systems (OS)** and **Database Management Systems (DBMS)** concepts in a real-world scheduling application.

## Features

### 1. User Authentication and Authorization
- Separate roles for mentors and teams.
- User registration and login.
- Password hashing and session management.
- Role-based access to dashboards and features.

### 2. Mentor Availability Management
- Mentors can define their available dates and time ranges.
- Automatic generation of bookable time slots.
- Detection of overlapping availability.
- Slot availability and booking status management.

### 3. Booking Management
- Teams can view available mentors and book meeting slots.
- Prevents duplicate bookings and conflicting requests.
- Supports booking cancellation.
- Updates slot status when bookings are created or cancelled.

### 4. Waiting List and Scheduling
- Teams can join the waiting list when a slot is unavailable.
- Displays waiting-list positions and request details.
- Supports **FCFS (First Come, First Served)** and **Priority Scheduling**.
- Uses **Aging** to increase the priority of requests waiting longer.
- Automatically promotes an eligible waiting team when a confirmed booking is cancelled.

### 5. Dashboards and Status Tracking
- Separate dashboards for mentors and teams.
- View mentor availability and booking details.
- Track confirmed bookings and waiting-list requests.
- View live booking status and slot availability.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend logic and scheduling |
| Flask | Web application and routing |
| MySQL | Persistent data storage |
| HTML5 | Web page structure |
| CSS3 | Styling and responsive UI |
| JavaScript | Client-side interactions |
| Git and GitHub | Version control and team collaboration |

## Operating Systems (OS) Concepts

- **FCFS Scheduling:** Processes waiting requests in arrival order.
- **Priority Scheduling:** Selects waiting requests based on priority.
- **Aging:** Helps reduce starvation by increasing the effective priority of requests that wait longer.
- **Concurrency:** Handles multiple users attempting to book or cancel slots.
- **Mutual Exclusion:** Database locking helps prevent conflicting updates to the same slot.
- **Starvation Prevention:** Aging helps lower-priority requests receive attention over time.

## Database Management Systems (DBMS) Concepts

- Relational database design and relationships.
- Primary keys and foreign keys.
- SQL queries, joins, and constraints.
- ACID transactions.
- Row-level locking using `SELECT ... FOR UPDATE`.
- Duplicate-request validation.
- Transaction commit and rollback.
- Consistency of booking and slot status.

## Project Structure

```text
mentor_booking_portal/
│
├── app.py                      # Flask application and routes
├── config.py                   # store common global constants
├── test_concurrency.py
├── routes/
│   ├── auth.py             # Login / register
│   ├── mentor.py           # Mentor dashboard, slot management
│   ├── booking.py          # Booking and cancellation
│   └── waitlist.py         # Waitlist endpoints
├── services/
│   ├── availability_service.py   # Slot generation and capacity
│   ├── booking_service.py        # Locking and booking logic
│   └── waitlist_service.py       # Queue handling and promotion
├── database
│   ├── schema.sql              # Database schema and table definitions
│   ├── setup_script.sh
│
├── db_config.py                # MySQL connection configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── mentor_dashboard.html
│   ├── team_dashboard.html
│   ├── mentor_slots.html
│   └── my_bookings.html
│
├── static/
│   └── style.css
│
├── tests/                  # Test cases, if configured
└── venv/                   # Local virtual environment (not committed)
```

*Note: Update the structure above if your actual project uses different filenames or folders.*

## Installation and Setup

### Prerequisites

Install the following before running the application:

- Python 3.10 or a compatible version.
- MySQL Server.
- Git.
- A code editor such as Visual Studio Code.

### Step 1: Clone the Repository

```bash
git clone git@github.com:deeksha3714/EasyMeet-Mentor-StudentMeetingBookingPortal.git
cd mentor_booking_portal
```

Replace the placeholder with your repository's actual URL.

### Step 2: Create and Activate a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

If you use Command Prompt instead:

```cmd
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure MySQL

Start your MySQL service and create the project database.

```sql
CREATE DATABASE mentor_booking_portal;
```

Import the schema from `schema.sql` using MySQL Workbench or the MySQL command line.

For example:

```bash
mysql -u root -p mentor_booking_portal < schema.sql
```

Configure your database host, port, username, password, and database name in `db_config.py` or the environment variables supported by your application.

**Security note:** Never commit real database passwords, secret keys, or other credentials to GitHub.

### Step 5: Run the Application

Start MySQL first. On Windows, if your service is named `MySQL80`, you can use:

```powershell
net start MySQL80
```

Then activate your virtual environment and run:

```bash
python app.py
```

Open the local URL printed by Flask in your browser. The default is commonly:

```text
http://127.0.0.1:5000
```

Use the actual URL and port configured by your application.

## How the System Works

1. A mentor registers or logs in and configures availability.
2. The application generates bookable time slots.
3. A team logs in and views available mentors and slots.
4. The team books an available slot or joins a waiting list.
5. The system stores booking and waiting-list information in MySQL.
6. Scheduling logic determines the next eligible waiting request according to the selected policy.
7. When a confirmed booking is cancelled, the system can promote a waiting team and update the booking records within a transaction.
8. Dashboards display the updated booking and waiting-list status.

## Team Contributions

This project is developed collaboratively by four team members.

| Team Member | Primary Responsibility |
|---|---|
| Deeksha | Database schema, MySQL integration, booking transactions, slot locking, and team dashboard integration |
| Lavanya | Authentication, sessions, role-based access, shared UI layout, styling, and status interface |
| Aditya | Mentor availability, slot generation, overlap detection, and concurrency testing |
| Aryan | Waiting-list management, FCFS and priority scheduling, aging, queue positions, cancellation, auto-promotion, and My Bookings interface |

All members should coordinate changes to shared files, especially `app.py`, database schema files, and shared templates.

## Future Enhancements

- Email notifications for booking confirmations and cancellations.
- Calendar integration and reminders.
- Improved dashboard analytics.
- Automated tests for scheduling and concurrent booking.
- Deployment to a cloud hosting platform.
- Enhanced access control and audit logging.

## Learning Outcomes

This project provides practical experience with:

- Full-stack web development using Flask.
- Relational database design and SQL.
- Transaction management and concurrency control.
- Scheduling algorithms and starvation prevention.
- Git-based collaborative development.
- Integrating OS and DBMS concepts into a working application.
