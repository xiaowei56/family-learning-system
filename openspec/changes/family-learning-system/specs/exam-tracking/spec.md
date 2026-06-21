## ADDED Requirements

### Requirement: Record exam results
The system SHALL allow users to record exam scores with score rate calculation.

#### Scenario: Record an exam result
- **WHEN** user selects subject, exam type (日常练习/周测/月考/期中/期末), enters score, total score, and date
- **THEN** the system saves the exam result and automatically calculates score_rate = score / total_score

#### Scenario: Invalid score input
- **WHEN** user enters a score greater than the total score
- **THEN** the system shows an error message and does not save

### Requirement: Score rate trend chart
The system SHALL generate score rate trend charts per subject.

#### Scenario: View score rate curve for a subject
- **WHEN** user selects a subject
- **THEN** the system displays a line chart with x-axis = date, y-axis = score rate (%), showing all exam results for that subject

#### Scenario: Filter by exam type
- **WHEN** user selects an exam type filter
- **THEN** the system updates the chart to show only results of that exam type

### Requirement: Multi-subject comparison
The system SHALL support overlay comparison of score rates across subjects.

#### Scenario: Compare multiple subjects
- **WHEN** user selects 2 or more subjects
- **THEN** the system displays multiple score rate trend lines on the same chart with a legend
