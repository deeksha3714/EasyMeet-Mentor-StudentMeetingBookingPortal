
{% extends "base.html" %}

{% block title %}Mentor Calendar | MentorMeet{% endblock %}

{% block head %}
<style>
    .mentor-slots-page {
        display: grid;
        gap: 22px;
        color: #202b43;
    }

    [data-theme="dark"] .mentor-slots-page {
        color: var(--ink);
    }

    [data-theme="dark"] .slots-section {
        background: var(--surface);
        border-color: var(--line);
    }

    [data-theme="dark"] .section-heading h2,
    [data-theme="dark"] .filter-panel h2 {
        color: var(--ink);
    }

    [data-theme="dark"] .slot-card {
        background: var(--surface);
        border-color: var(--line);
    }

    [data-theme="dark"] .slot-card.is-booked {
        background: color-mix(in srgb, var(--surface) 92%, var(--red));
    }

    [data-theme="dark"] .slot-time {
        color: var(--ink);
    }

    [data-theme="dark"] .slot-divider {
        background: var(--line);
    }

    [data-theme="dark"] .slot-card input,
    [data-theme="dark"] .slot-card select,
    [data-theme="dark"] .filter-controls input {
        background: var(--page);
        border-color: var(--line);
        color: var(--ink);
    }

    [data-theme="dark"] #team-calendar .fc-toolbar-title,
    [data-theme="dark"] #team-calendar .fc-daygrid-day-number {
        color: var(--ink);
    }

    [data-theme="dark"] #team-calendar .fc-daygrid-day.fc-day-today {
        background: var(--blue-soft);
    }

    [data-theme="dark"] #team-calendar .fc-theme-standard td,
    [data-theme="dark"] #team-calendar .fc-theme-standard th,
    [data-theme="dark"] #team-calendar .fc-scrollgrid {
        border-color: var(--line);
    }

    [data-theme="dark"] .my-booking-note {
        background: var(--blue-soft);
        color: var(--blue);
    }

    [data-theme="dark"] .queue-box {
        background: #332610;
        border-color: #5c4419;
        color: var(--amber);
    }

    [data-theme="dark"] .section-icon {
        background: var(--blue-soft);
        color: var(--blue);
    }

    .mentor-slots-page * {
        box-sizing: border-box;
    }

    .mentor-back {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        width: fit-content;
        font-size: 13px;
        font-weight: 700;
        text-decoration: none;
    }

    .mentor-hero {
        position: relative;
        overflow: hidden;
        padding: 28px;
        border-radius: 20px;
        color: white;
        background: linear-gradient(120deg, #172747, #3157d5);
        box-shadow: 0 12px 30px rgba(34,55,110,.14);
    }

    .mentor-hero::before,
    .mentor-hero::after {
        content: "";
        position: absolute;
        border: 1px solid #ffffff20;
        border-radius: 50%;
        pointer-events: none;
    }

    .mentor-hero::before {
        width: 230px;
        height: 230px;
        right: -65px;
        top: -125px;
    }

    .mentor-hero::after {
        width: 155px;
        height: 155px;
        right: 15px;
        top: 75px;
    }

    .mentor-hero-content {
        position: relative;
        z-index: 1;
    }

    .hero-label {
        color: #cbd8ff;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.6px;
    }

    .mentor-hero h1 {
        margin: 9px 0;
        font-size: clamp(25px, 4vw, 35px);
        letter-spacing: -.8px;
    }

    .mentor-hero p {
        margin: 0;
        color: #dce5ff;
        font-size: 13px;
    }

    .hero-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 19px;
    }

    .hero-meta span {
        padding: 8px 12px;
        border: 1px solid #ffffff30;
        border-radius: 9px;
        background: #ffffff13;
        font-size: 11px;
        font-weight: 700;
    }

    .slots-section {
        padding: 22px;
        border: 1px solid #e7eaf1;
        border-radius: 17px;
        background: white;
        box-shadow: 0 5px 20px rgba(25,40,75,.045);
    }

    .section-heading {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
        margin-bottom: 18px;
    }

    .section-heading h2 {
        margin: 0;
        font-size: 20px;
        color: #202b43;
    }

    .section-heading p {
        margin: 5px 0 0;
        color: #778197;
        font-size: 12px;
    }

    .section-label {
        margin-bottom: 5px;
        color: #3157d5;
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1.3px;
    }

    .section-icon {
        display: grid;
        place-items: center;
        width: 40px;
        height: 40px;
        border-radius: 11px;
        background: #eef2ff;
        color: #3157d5;
        font-size: 20px;
    }

    .policy-info {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        padding: 7px 11px;
        border-radius: 30px;
        background: #eef2ff;
        color: #3157d5;
        font-size: 11px;
        font-weight: 750;
    }

    .calendar-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 17px;
        margin-bottom: 15px;
    }

    .legend-item {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        color: #68748b;
        font-size: 11px;
        font-weight: 650;
    }

    .legend-dot {
        width: 9px;
        height: 9px;
        border-radius: 50%;
    }

    .calendar-hint {
        margin: 0 0 16px;
        padding: 12px 14px;
        border: 1px solid #dfe6ff;
        border-radius: 10px;
        background: #f3f6ff;
        color: #344b91;
        font-size: 12px;
    }

    #team-calendar {
        min-height: 300px;
    }

    #team-calendar .fc-button-primary {
        background: #3157d5;
        border-color: #3157d5;
    }

    #team-calendar .fc-button-primary:hover {
        background: #2446bb;
        border-color: #2446bb;
    }

    #team-calendar .fc-button-primary:disabled {
        opacity: .55;
    }

    #team-calendar .fc-toolbar-title {
        font-size: 19px;
        font-weight: 800;
    }

    #team-calendar .fc-daygrid-day-number {
        color: #34405a;
        text-decoration: none;
        font-size: 12px;
    }

    #team-calendar .fc-event {
        border-radius: 5px;
        font-size: 11px;
    }

    #team-calendar .fc-daygrid-day.fc-day-today {
        background: #f1f5ff;
    }

    .filter-panel {
        display: flex;
        justify-content: space-between;
        align-items: end;
        flex-wrap: wrap;
        gap: 14px;
    }

    .filter-panel h2 {
        margin: 0;
        font-size: 19px;
    }

    .filter-panel p {
        margin: 5px 0 0;
        color: #778197;
        font-size: 12px;
    }

    .filter-controls {
        display: flex;
        align-items: end;
        flex-wrap: wrap;
        gap: 9px;
    }

    .filter-controls label {
        display: block;
        margin-bottom: 6px;
        color: #59657b;
        font-size: 11px;
        font-weight: 750;
    }

    .filter-controls input {
        min-width: 170px;
    }

    .slot-toolbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        margin-bottom: 17px;
    }

    .slot-search {
        flex: 1 1 220px;
    }

    .slot-search input {
        width: 100%;
    }

    .slot-count {
        color: #778197;
        font-size: 12px;
        font-weight: 700;
    }

    .slot-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 15px;
    }

    .slot-card {
        position: relative;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        gap: 13px;
        padding: 18px;
        border: 1px solid #e7eaf1;
        border-radius: 15px;
        background: white;
        transition: transform .2s, box-shadow .2s, border-color .2s;
    }

    .slot-card:hover {
        transform: translateY(-4px);
        border-color: #c9d5ff;
        box-shadow: 0 12px 25px rgba(35,55,100,.09);
    }

    .slot-card.is-booked {
        background: #fffefe;
    }

    .slot-card-top {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 8px;
    }

    .slot-date {
        color: #778197;
        font-size: 11px;
        font-weight: 650;
    }

    .slot-id {
        color: #8490a6;
        font-size: 10px;
        font-weight: 750;
    }

    .slot-time {
        color: #202b43;
        font-size: 23px;
        font-weight: 850;
        letter-spacing: -.7px;
    }

    .slot-time-label {
        color: #8a94a8;
        font-size: 10px;
        font-weight: 650;
    }

    .slot-status {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        width: fit-content;
        padding: 6px 10px;
        border-radius: 30px;
        font-size: 10px;
        font-weight: 800;
        text-transform: capitalize;
    }

    .slot-status.available {
        color: #087443;
        background: #e6f8ee;
    }

    .slot-status.booked {
        color: #b42318;
        background: #ffeded;
    }

    .slot-status.cancelled {
        color: #667085;
        background: #f0f1f3;
    }

    .slot-divider {
        height: 1px;
        background: #edf0f5;
    }

    .slot-card form {
        display: grid;
        gap: 9px;
        margin-top: auto;
    }

    .slot-card label {
        color: #59657b;
        font-size: 11px;
        font-weight: 750;
    }

    .slot-card input,
    .slot-card select {
        width: 100%;
        min-width: 0;
        font-size: 12px;
    }

    .slot-card button {
        width: 100%;
        justify-content: center;
    }

    .slot-card .muted {
        color: #778197;
        font-size: 11px;
    }

    .my-booking-note {
        padding: 11px;
        border-radius: 9px;
        background: #eef4ff;
        color: #3157a4;
        font-size: 11px;
        font-weight: 650;
    }

    .queue-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        padding: 11px;
        border: 1px solid #f4e2b8;
        border-radius: 10px;
        background: #fff9ed;
    }

    .queue-position {
        color: #946200;
        font-size: 12px;
        font-weight: 850;
    }

    .queue-total {
        color: #947e55;
        font-size: 10px;
    }

    .queue-none {
        color: #778197;
        font-size: 11px;
    }

    .empty-state {
        padding: 40px 18px;
        text-align: center;
        border: 1px dashed #d6dbe6;
        border-radius: 14px;
        background: #fafbff;
    }

    .empty-icon {
        display: grid;
        place-items: center;
        width: 58px;
        height: 58px;
        margin: 0 auto 14px;
        border-radius: 16px;
        background: #eef2ff;
        color: #3157d5;
        font-size: 25px;
    }

    .empty-state h3 {
        margin: 0 0 6px;
        color: #202b43;
        font-size: 17px;
    }

    .empty-state p {
        margin: 0;
        color: #778197;
        font-size: 12px;
    }

    .hidden-slot {
        display: none !important;
    }

    .slot-footer {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 10px;
        color: #8490a6;
        font-size: 11px;
    }

    @media(max-width: 1000px) {
        .slot-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
    }

    @media(max-width: 650px) {
        .mentor-hero {
            padding: 22px;
        }

        .slots-section {
            padding: 16px;
        }

        .slot-grid {
            grid-template-columns: 1fr;
        }

        .filter-panel {
            align-items: stretch;
        }

        .filter-controls {
            width: 100%;
        }

        .filter-controls > div {
            flex: 1 1 100%;
        }

        .filter-controls input {
            width: 100%;
        }

        #team-calendar .fc-toolbar {
            flex-direction: column;
            gap: 10px;
        }

        #team-calendar .fc-toolbar-title {
            font-size: 17px;
        }
    }
</style>
{% endblock %}


{% block content %}

<div class="mentor-slots-page">

    <!-- BACK BUTTON -->
    <a class="btn btn-ghost btn-sm mentor-back"
       href="{{ url_for('team_dashboard') }}">
        ← Back to mentors
    </a>


    <!-- MENTOR INTRODUCTION -->
    <section class="mentor-hero">
        <div class="mentor-hero-content">

            <div class="hero-label">MENTOR AVAILABILITY</div>

            <h1>{{ mentor.name }}</h1>

            <p>
                {{ mentor.department or 'Department not set' }}
            </p>

            <div class="hero-meta">
                <span>📅 Meeting calendar</span>
                <span>⚙ {{ policy|default('FCFS') }} scheduling</span>
                {% if assigned_mentor_id and mentor.mentor_id != assigned_mentor_id %}
                <span style="color: var(--amber, #d97706); font-weight: 600;">ℹ View-only (Not assigned mentor)</span>
                {% elif assigned_mentor_id and mentor.mentor_id == assigned_mentor_id %}
                <span style="color: var(--green, #16a34a); font-weight: 600;">✓ Assigned Mentor</span>
                {% endif %}
            </div>

        </div>
    </section>


    <!-- CALENDAR -->
    <section class="slots-section">

        <div class="section-heading">
            <div>
                <div class="section-label">VISUAL SCHEDULE</div>
                <h2>Availability calendar</h2>
                <p>Explore available dates and scheduled meetings.</p>
            </div>

            <div class="section-icon">▦</div>
        </div>

        <div class="calendar-legend">

            <span class="legend-item">
                <i class="legend-dot" style="background:#16a34a"></i>
                Available
            </span>

            <span class="legend-item">
                <i class="legend-dot" style="background:#dc2626"></i>
                Booked by another team
            </span>

            <span class="legend-item">
                <i class="legend-dot" style="background:#2563eb"></i>
                Your meeting
            </span>

        </div>

        <div class="calendar-hint">
            💡 Select a date to filter the meeting slots below.
            Calendar events are view-only and cannot be clicked or changed.
        </div>

        <div
            id="team-calendar"
            data-events-url="{{ url_for('team_mentor_calendar_events', mentor_id=mentor.mentor_id) }}">
        </div>

    </section>


    <!-- SLOT FILTERS -->
    <section class="slots-section">

        <div class="filter-panel">

            <div>
                <div class="section-label">FIND A MEETING</div>
                <h2>Meeting slots</h2>
                <p>Book an available slot or join the waitlist for a booked slot.</p>
            </div>

            <div class="filter-controls">

                <div>
                    <label for="slot-date-filter">Filter by date</label>
                    <input
                        type="date"
                        id="slot-date-filter"
                    >
                </div>

                <button
                    class="btn btn-ghost btn-sm"
                    type="button"
                    id="clear-date-filter"
                >
                    Show all dates
                </button>

            </div>

        </div>

    </section>


    <!-- SLOT CARDS -->
    <section class="slots-section">

        <div class="slot-toolbar">

            <div>
                <div class="section-label">BOOKING OPTIONS</div>
                <h2 style="margin:0;font-size:19px;">Available sessions</h2>
            </div>

            {% if slots %}
            <span class="slot-count" id="slot-count">
                {{ slots|length }} slots available in this list
            </span>
            {% endif %}

        </div>


        {% if slots %}

        <div class="slot-toolbar">
            <div class="slot-search">
                <input
                    type="search"
                    id="slot-search"
                    placeholder="Search by date, time or status..."
                    aria-label="Search meeting slots"
                >
            </div>

            <select id="slot-status-filter" aria-label="Filter by availability">
                <option value="all">All slots</option>
                <option value="available">Available</option>
                <option value="booked">Booked</option>
            </select>
        </div>


        <div class="slot-grid" id="slot-list">

            {% for s in slots %}

            <article
                class="slot-card {{ 'is-booked' if s.status == 'booked' else '' }}"
                id="slot-{{ s.slot_id }}"
                data-slot-id="{{ s.slot_id }}"
                data-date="{{ s.slot_iso }}"
                data-status="{{ s.status|lower }}"
            >

                <div class="slot-card-top">

                    <span class="slot-date">
                        📅 {{ s.slot_date }}
                    </span>

                    <span class="slot-id">
                        SLOT #{{ s.slot_id }}
                    </span>

                </div>


                <div>
                    <div class="slot-time">
                        {{ s.start_t }} – {{ s.end_t }}
                    </div>

                    <div class="slot-time-label">
                        Meeting time
                    </div>
                </div>


                <span class="slot-status {{ s.status|lower }}">
                    ● {{ s.status }}
                </span>


                <div class="slot-divider"></div>


                {% if s.booked_by == my_team_id %}

                <!-- ALREADY BOOKED BY THIS TEAM -->
                <div class="my-booking-note">
                    ✓ This slot is already booked by your team.
                </div>

                {% elif assigned_mentor_id and mentor.mentor_id != assigned_mentor_id %}

                <!-- VIEW ONLY NOTICE FOR UNASSIGNED MENTOR -->
                <div class="my-booking-note" style="background: var(--surface); color: var(--muted); border: 1px dashed var(--line); font-size: 13px;">
                    ℹ You can only book slots with your assigned mentor.
                </div>

                {% elif s.status == 'available' %}

                <!-- BOOK AVAILABLE SLOT -->
                <form
                    method="POST"
                    action="{{ url_for('book', slot_id=s.slot_id) }}"
                >

                    <label for="reason-{{ s.slot_id }}">
                        Reason for meeting
                    </label>

                    <input
                        id="reason-{{ s.slot_id }}"
                        type="text"
                        name="reason"
                        placeholder="What would you like to discuss?"
                        maxlength="500"
                        required
                    >

                    <button class="btn btn-sm" type="submit">
                        Book this slot →
                    </button>

                </form>


                {% else %}

                <!-- JOIN WAITLIST -->
                {% if s.my_pos %}

                <div class="queue-box">

                    <span class="queue-position">
                        Your position: #{{ s.my_pos }}
                    </span>

                    <span class="queue-total">
                        {{ s.queue_len }} waiting
                    </span>

                </div>

                {% else %}

                <div class="queue-box">
                    <span class="queue-position">
                        Join the queue
                    </span>

                    <span class="queue-total">
                        {{ s.queue_len }} waiting
                    </span>
                </div>

                {% endif %}


                <form
                    method="POST"
                    action="{{ url_for('waitlist', slot_id=s.slot_id) }}"
                >

                    <label for="wait-reason-{{ s.slot_id }}">
                        Reason for meeting
                    </label>

                    <input
                        id="wait-reason-{{ s.slot_id }}"
                        type="text"
                        name="reason"
                        placeholder="What would you like to discuss?"
                        maxlength="500"
                        required
                    >

                    <label for="priority-{{ s.slot_id }}">
                        Request priority
                    </label>

                    <select
                        id="priority-{{ s.slot_id }}"
                        name="priority"
                    >
                        <option value="1">General</option>
                        <option value="2">Review</option>
                        <option value="3">Urgent</option>
                    </select>

                    <button class="btn btn-ghost btn-sm" type="submit">
                        {% if s.my_pos %}
                            Update waitlist request
                        {% else %}
                            Join waitlist →
                        {% endif %}
                    </button>

                </form>

                {% endif %}

            </article>

            {% endfor %}

        </div>


        <!-- NO SEARCH RESULTS -->
        <div class="empty-state hidden-slot" id="no-slot-results">
            <div class="empty-icon">⌕</div>
            <h3>No matching slots found</h3>
            <p>Try another date, search term or availability filter.</p>
        </div>


        {% else %}

        <div class="empty-state">
            <div class="empty-icon">▦</div>
            <h3>No upcoming slots</h3>
            <p>This mentor has not added any upcoming availability yet.</p>
        </div>

        {% endif %}

    </section>


    <div class="slot-footer">
        <span>MentorMeet · Meeting booking system</span>
        <span>Calendar events are view-only.</span>
    </div>

</div>

{% endblock %}


{% block scripts %}

<script>
document.addEventListener("DOMContentLoaded", function () {

    const calendarEl =
        document.getElementById("team-calendar");

    const dateFilter =
        document.getElementById("slot-date-filter");

    const clearButton =
        document.getElementById("clear-date-filter");

    const searchInput =
        document.getElementById("slot-search");

    const statusFilter =
        document.getElementById("slot-status-filter");

    const slotCards = Array.from(
        document.querySelectorAll("#slot-list [data-slot-id]")
    );

    const slotCount =
        document.getElementById("slot-count");

    const noResults =
        document.getElementById("no-slot-results");


    // APPLY DATE, SEARCH AND STATUS FILTERS
    function applyFilters() {

        const selectedDate =
            dateFilter ? dateFilter.value : "";

        const searchText =
            searchInput
                ? searchInput.value.toLowerCase().trim()
                : "";

        const selectedStatus =
            statusFilter ? statusFilter.value : "all";

        let visibleCount = 0;

        slotCards.forEach(function (card) {

            const cardDate =
                (card.dataset.date || "").slice(0, 10);

            const cardStatus =
                card.dataset.status || "";

            const cardText =
                card.innerText.toLowerCase();

            const matchesDate =
                !selectedDate || cardDate === selectedDate;

            const matchesSearch =
                cardText.includes(searchText);

            const matchesStatus =
                selectedStatus === "all" ||
                selectedStatus === cardStatus;

            const show =
                matchesDate &&
                matchesSearch &&
                matchesStatus;

            card.classList.toggle(
                "hidden-slot",
                !show
            );

            if (show) {
                visibleCount++;
            }

        });


        if (slotCount) {
            slotCount.textContent =
                visibleCount + " matching slots";
        }

        if (noResults) {
            noResults.classList.toggle(
                "hidden-slot",
                visibleCount !== 0
            );
        }

    }


    if (dateFilter) {
        dateFilter.addEventListener("change", applyFilters);
    }

    if (searchInput) {
        searchInput.addEventListener("input", applyFilters);
    }

    if (statusFilter) {
        statusFilter.addEventListener("change", applyFilters);
    }


    // CLEAR DATE FILTER
    if (clearButton) {

        clearButton.addEventListener("click", function () {

            if (dateFilter) {
                dateFilter.value = "";
            }

            applyFilters();

        });

    }


    // CALENDAR
    if (!calendarEl) return;

    const eventsUrl =
        calendarEl.dataset.eventsUrl;


    if (!window.FullCalendar) {
        console.error(
            "FullCalendar is not loaded. Check base.html."
        );
        return;
    }


    const calendar = new FullCalendar.Calendar(calendarEl, {

        initialView: "dayGridMonth",

        height: "auto",

        fixedWeekCount: false,

        dayMaxEvents: 3,

        nowIndicator: true,

        selectable: false,

        editable: false,

        eventStartEditable: false,

        eventDurationEditable: false,

        eventDisplay: "block",

        headerToolbar: {
            left: "prev,next today",
            center: "title",
            right: "dayGridMonth,timeGridWeek,listMonth"
        },


        // LOAD EVENTS FROM EXISTING FLASK API
        events: function (
            fetchInfo,
            successCallback,
            failureCallback
        ) {

            const separator =
                eventsUrl.includes("?") ? "&" : "?";

            const requestUrl =
                eventsUrl +
                separator +
                "start=" +
                encodeURIComponent(fetchInfo.startStr) +
                "&end=" +
                encodeURIComponent(fetchInfo.endStr);


            fetch(requestUrl)
                .then(function (response) {

                    if (!response.ok) {
                        throw new Error(
                            "HTTP " + response.status
                        );
                    }

                    return response.json();

                })
                .then(function (events) {

                    const coloredEvents = events.map(
                        function (event) {

                            const props =
                                event.extendedProps || {};

                            const status = String(
                                props.status || event.status || ""
                            ).toLowerCase();

                            const isMine =
                                props.mine === true ||
                                props.mine === 1 ||
                                props.mine === "true";

                            let color;

                            if (isMine) {
                                color = "#2563eb";
                            }
                            else if (
                                status === "booked" ||
                                status === "unavailable" ||
                                status === "reserved"
                            ) {
                                color = "#dc2626";
                            }
                            else if (status === "cancelled") {
                                color = "#6b7280";
                            }
                            else {
                                color = "#16a34a";
                            }

                            return {
                                ...event,
                                backgroundColor: color,
                                borderColor: color,
                                textColor: "#ffffff"
                            };

                        }
                    );

                    successCallback(coloredEvents);

                })
                .catch(function (error) {

                    console.error(
                        "Could not load mentor calendar:",
                        error
                    );

                    failureCallback(error);

                });

        },


        // KEEP CALENDAR EVENTS NON-INTERACTIVE
        eventDidMount: function (info) {

            info.el.style.cursor = "default";

            info.el.style.pointerEvents = "none";

            info.el.setAttribute(
                "aria-disabled",
                "true"
            );

        },


        // CLICKING A DATE FILTERS THE SLOT CARDS
        dateClick: function (info) {

            const selectedDate =
                info.dateStr.slice(0, 10);

            if (dateFilter) {
                dateFilter.value = selectedDate;
            }

            applyFilters();

            const slotList =
                document.getElementById("slot-list");

            if (slotList) {

                slotList.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        }

    });


    calendar.render();

});
</script>

{% endblock %}
