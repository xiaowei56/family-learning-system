## ADDED Requirements

### Requirement: Upload and archive exam papers
The system SHALL allow users to upload exam paper photos and organize them by subject, exam type, and date.

#### Scenario: Upload an exam paper
- **WHEN** user uploads an exam paper photo with subject, exam type, and date
- **THEN** the system saves the image to MinIO and creates an exam paper record

#### Scenario: Browse paper library
- **WHEN** user opens the paper library
- **THEN** the system displays archived papers grouped by subject, filterable by exam type and date range

### Requirement: Erase handwriting for re-printing
The system SHALL use AI to remove handwriting from exam paper images and produce clean versions for re-printing.

#### Scenario: Generate clean version
- **WHEN** user requests "erase handwriting" on an exam paper
- **THEN** the system uses PaddleOCR + image inpainting to remove handwriting strokes and saves the cleaned image

#### Scenario: Download and print
- **WHEN** user clicks "Download Clean Version"
- **THEN** the system provides the cleaned image for download and printing

### Requirement: Online paper review with annotations
The system SHALL allow viewing exam paper originals with annotation support.

#### Scenario: View exam paper
- **WHEN** user opens an exam paper
- **THEN** the system displays the original image with zoom and page navigation

#### Scenario: Add annotation
- **WHEN** user clicks on the paper image and enters annotation text
- **THEN** the system saves the annotation with position coordinates and displays it on the image

#### Scenario: View saved annotations
- **WHEN** user re-opens an annotated exam paper
- **THEN** the system displays all previous annotations on the image
