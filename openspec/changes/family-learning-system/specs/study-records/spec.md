## ADDED Requirements

### Requirement: Create study record
The system SHALL allow users to record daily learning content with rich text.

#### Scenario: Create a study record
- **WHEN** user selects a subject, enters a title, writes rich text notes, and adds knowledge point tags
- **THEN** the system saves the study record and calculates the first review date (1 day later)

#### Scenario: View study records by subject
- **WHEN** user selects a subject filter
- **THEN** the system displays study records filtered by that subject, ordered by date descending

### Requirement: Memory curve review schedule
The system SHALL calculate review dates based on the Ebbinghaus forgetting curve.

#### Scenario: Automatic review schedule creation
- **WHEN** a study record is created
- **THEN** the system creates review schedule entries at intervals: 1d, 2d, 4d, 7d, 15d, 30d, 90d

#### Scenario: Daily review reminders
- **WHEN** user opens the review center
- **THEN** the system displays all records due for review today, grouped by subject

### Requirement: Mark as mastered
The system SHALL allow users to manually end the review cycle for a knowledge point.

#### Scenario: Mark a record as mastered
- **WHEN** user clicks "Mark as Mastered" on a study record
- **THEN** the system cancels all future review schedules for that record

### Requirement: Review frequency adjustment
The system SHALL offer configurable review speed modes.

#### Scenario: Change review speed
- **WHEN** user selects a speed mode (fast/medium/slow)
- **THEN** the system adjusts review intervals proportionally (fast: 0.5x, medium: 1x, slow: 1.5x)
