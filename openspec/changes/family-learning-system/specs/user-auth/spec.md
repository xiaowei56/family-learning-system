## ADDED Requirements

### Requirement: User registration and login
The system SHALL support user registration and login within the local network.

#### Scenario: Register a new user
- **WHEN** a parent enters username, password, and student grade level (小学/初中/高中)
- **THEN** the system creates a user account and returns a JWT token

#### Scenario: Login with valid credentials
- **WHEN** user provides correct username and password
- **THEN** the system returns a JWT token with 24-hour expiry

#### Scenario: Login with invalid credentials
- **WHEN** user provides incorrect username or password
- **THEN** the system returns 401 Unauthorized

### Requirement: Multi-student management
The system SHALL support one parent account managing multiple student profiles.

#### Scenario: Add a student profile
- **WHEN** parent adds a new student with name and grade level
- **THEN** the system creates a student profile under the parent account

#### Scenario: Switch grade level
- **WHEN** user changes a student's grade level
- **THEN** the system updates the grade level and adjusts subject options accordingly

### Requirement: Subject management
The system SHALL allow users to configure which subjects they study.

#### Scenario: Configure subjects
- **WHEN** user selects subjects from a preset list (数学/物理/化学/语文/英语/生物/历史/地理/政治)
- **THEN** the system saves the subject list for that student
