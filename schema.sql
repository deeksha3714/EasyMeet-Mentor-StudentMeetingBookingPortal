-- =========================================
-- Mentor-Student Meeting Booking Portal
-- Database Schema
-- =========================================

-- 1. Mentor
CREATE TABLE IF NOT EXISTS Mentor (
    mentor_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    department VARCHAR(100)
);

-- 2. Team
CREATE TABLE IF NOT EXISTS Team (
    team_id INT PRIMARY KEY AUTO_INCREMENT,
    team_name VARCHAR(100) NOT NULL,
    members TEXT,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- 3. Mentor_Availability
CREATE TABLE IF NOT EXISTS Mentor_Availability (
    availability_id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_id INT NOT NULL,
    day VARCHAR(10) NOT NULL,
    free_from TIME NOT NULL,
    free_to TIME NOT NULL,
    meeting_duration INT NOT NULL,
    FOREIGN KEY (mentor_id) REFERENCES Mentor(mentor_id) ON DELETE CASCADE
);

-- 4. Slot
CREATE TABLE IF NOT EXISTS Slot (
    slot_id INT PRIMARY KEY AUTO_INCREMENT,
    mentor_id INT NOT NULL,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    status ENUM('available', 'booked', 'cancelled') DEFAULT 'available',
    FOREIGN KEY (mentor_id) REFERENCES Mentor(mentor_id) ON DELETE CASCADE
);

-- 5. Booking
CREATE TABLE IF NOT EXISTS Booking (
    booking_id INT PRIMARY KEY AUTO_INCREMENT,
    team_id INT NOT NULL,
    mentor_id INT NOT NULL,
    slot_id INT NOT NULL UNIQUE,
    reason TEXT,
    status ENUM('confirmed', 'cancelled', 'completed') DEFAULT 'confirmed',
    urgency_tag VARCHAR(20) DEFAULT 'general',
    booking_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE,
    FOREIGN KEY (mentor_id) REFERENCES Mentor(mentor_id) ON DELETE CASCADE,
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id) ON DELETE CASCADE
);

-- 6. Waiting_List
CREATE TABLE IF NOT EXISTS Waiting_List (
    waitlist_id INT PRIMARY KEY AUTO_INCREMENT,
    slot_id INT NOT NULL,
    team_id INT NOT NULL,
    reason TEXT,
    priority TINYINT NOT NULL DEFAULT 1,          -- 1 General, 2 Review, 3 Urgent
    request_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('waiting', 'promoted', 'expired', 'cancelled') DEFAULT 'waiting',
    FOREIGN KEY (slot_id) REFERENCES Slot(slot_id) ON DELETE CASCADE,
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE
);

-- 7. Chat_Messages (used in next phase)
CREATE TABLE IF NOT EXISTS Chat_Messages (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    team_id INT NOT NULL,
    mentor_id INT NOT NULL,
    sender ENUM('mentor', 'student') NOT NULL,
    message_text TEXT NOT NULL,
    is_ai_draft BOOLEAN DEFAULT FALSE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (team_id) REFERENCES Team(team_id) ON DELETE CASCADE,
    FOREIGN KEY (mentor_id) REFERENCES Mentor(mentor_id) ON DELETE CASCADE
);

-- 8. Meeting_Briefings (used in next phase)
CREATE TABLE IF NOT EXISTS Meeting_Briefings (
    briefing_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL UNIQUE,
    briefing_text TEXT,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id) REFERENCES Booking(booking_id) ON DELETE CASCADE
);

-- Indexes
CREATE INDEX idx_mentor_slot ON Slot(mentor_id, date);
CREATE INDEX idx_team_mentor_booking ON Booking(team_id, mentor_id);
CREATE INDEX idx_team_mentor_chat ON Chat_Messages(team_id, mentor_id);
CREATE INDEX idx_waitlist_order ON Waiting_List(slot_id, request_time);
