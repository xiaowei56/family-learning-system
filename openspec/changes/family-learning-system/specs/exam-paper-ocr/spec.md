## ADDED Requirements

### Requirement: Upload exam paper photo
The system SHALL allow users to upload photos of exam papers and wrong problems.

#### Scenario: Upload a photo
- **WHEN** user uploads a photo (JPG/PNG) of an exam paper or wrong problem
- **THEN** the system stores the image in MinIO and queues it for OCR processing

### Requirement: OCR text extraction
The system SHALL use PaddleOCR to extract text from uploaded images.

#### Scenario: OCR processing completes
- **WHEN** PaddleOCR finishes processing an image
- **THEN** the system saves extracted text content and associates it with the image

#### Scenario: OCR processing failure
- **WHEN** PaddleOCR fails to extract meaningful text
- **THEN** the system notifies the user and allows manual text input

### Requirement: AI problem evaluation
The system SHALL use LLM to determine whether a problem answer is correct.

#### Scenario: Evaluate problem correctness
- **WHEN** user submits a problem with their answer via OCR or manual input
- **THEN** the system calls local LLM API to determine correctness and returns the result

### Requirement: AI solution generation with diagrams
The system SHALL generate step-by-step solutions with prioritized visual diagrams.

#### Scenario: View problem solution
- **WHEN** user requests the solution for a problem
- **THEN** the system returns:
  - Step-by-step text solution
  - For geometry problems: SVG diagram with labeled shapes
  - For function/algebra problems: MathJax formula + Chart.js graph
  - For physics/chemistry problems: flowchart or schematic diagram

### Requirement: Wrong problem auto-collection
The system SHALL automatically collect wrong problems into a dedicated notebook.

#### Scenario: Wrong problem is auto-saved
- **WHEN** a problem is marked or evaluated as incorrect
- **THEN** the system automatically saves it to the wrong problem notebook with subject and knowledge point tags

### Requirement: Browse wrong problems
The system SHALL allow browsing wrong problems by subject and knowledge point.

#### Scenario: Filter wrong problems
- **WHEN** user selects a subject and optionally a knowledge point
- **THEN** the system displays matching wrong problems with their original images and solutions
