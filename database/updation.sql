USE easymeet;

ALTER TABLE Chat_Messages
    MODIFY COLUMN sender
    ENUM('mentor', 'student', 'team') NOT NULL;

UPDATE Chat_Messages
SET sender = 'team'
WHERE sender = 'student';

ALTER TABLE Chat_Messages
    MODIFY COLUMN sender
    ENUM('mentor', 'team') NOT NULL;

CREATE TABLE IF NOT EXISTS Meeting_Briefings (
    briefing_id INT PRIMARY KEY AUTO_INCREMENT,
    booking_id INT NOT NULL UNIQUE,
    briefing_text TEXT,
    generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (booking_id)
        REFERENCES Booking(booking_id) ON DELETE CASCADE
);
