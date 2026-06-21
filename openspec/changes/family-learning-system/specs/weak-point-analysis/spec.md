## ADDED Requirements

### Requirement: Weak point identification
The system SHALL analyze wrong problems and exam results to identify knowledge weak points.

#### Scenario: Run weak point analysis
- **WHEN** user opens the weak point analysis page
- **THEN** the system calculates error rate per knowledge point from wrong problems and score rate from exam results, then outputs a ranked list of weak points

#### Scenario: Visualize weak points
- **WHEN** user views weak point results
- **THEN** the system displays a radar chart or heatmap showing mastery levels across knowledge points

### Requirement: Smart practice paper generation
The system SHALL automatically generate practice papers targeting weak knowledge points.

#### Scenario: Generate practice paper
- **WHEN** user selects weak points to practice and clicks "Generate Paper"
- **THEN** the system calls LLM to create a practice paper covering selected weak points with progressive difficulty (basic → consolidation → advanced)

#### Scenario: Adjust generated paper
- **WHEN** user wants to modify the generated paper
- **THEN** the system allows adding, removing, or reordering questions before finalizing

### Requirement: Learning diagnosis report
The system SHALL generate a learning diagnosis report with study advice.

#### Scenario: View diagnosis report
- **WHEN** user requests a diagnosis report
- **THEN** the system generates a report containing:
  - Mastery level per knowledge point (薄弱/待巩固/已掌握)
  - Specific learning suggestions for each weak point (actionable study steps)
  - Study method recommendations per subject (e.g., math: practice focus, physics: concept understanding, Chinese: accumulation)
  - Memory technique recommendations (Ebbinghaus review plan, associative memory, mind maps, error cards)
