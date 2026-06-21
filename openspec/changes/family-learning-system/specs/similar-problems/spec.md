## ADDED Requirements

### Requirement: Generate similar problems from wrong problems
The system SHALL generate similar practice problems based on a user's wrong problem.

#### Scenario: Generate similar problems
- **WHEN** user clicks "Generate Similar Problems" on a wrong problem
- **THEN** the system calls LLM to generate 3-5 similar problems with the same knowledge point and progressive difficulty

#### Scenario: View generated problems
- **WHEN** user opens the generated problem set
- **THEN** the system displays problems with answer fields and a "Show Solution" button for each

### Requirement: Provide structured solution approaches
The system SHALL provide general problem-solving strategies for each problem type.

#### Scenario: View solution approach
- **WHEN** user clicks "Show Solution Approach" on a similar problem
- **THEN** the system displays:
  - Step-by-step solution method
  - Key formulas or principles
  - Related diagram if applicable
