## 1. Infrastructure & Project Scaffold

- [x] 1.1 Create Docker Compose skeleton (Nginx + FastAPI + PostgreSQL + MinIO + Redis)
- [x] 1.2 Initialize FastAPI backend project (project structure, config, dependency management)
- [x] 1.3 Initialize Web frontend project (Vue3 + Element Plus + Vite)
- [ ] 1.4 Initialize Flutter Android project (deferred to Phase 2)
- [x] 1.5 Set up PostgreSQL database migration tool (Alembic)
- [x] 1.6 Set up MinIO client and image upload/download service

## 2. User Authentication (user-auth spec)

- [x] 2.1 Create User and Student models + migration
- [x] 2.2 Implement user registration API (POST /api/v1/auth/register)
- [x] 2.3 Implement user login API with JWT (POST /api/v1/auth/login)
- [x] 2.4 Implement student profile CRUD API
- [x] 2.5 Implement subject configuration API
- [x] 2.6 Build login/register page (Web frontend)
- [x] 2.7 Build user settings page (grade level, subject management)

## 3. Study Records & Memory Curve (study-records spec)

- [x] 3.1 Create StudyRecord and ReviewSchedule models + migration
- [x] 3.2 Implement study record CRUD API (with subject filter)
- [x] 3.3 Implement Ebbinghaus forgetting curve algorithm (review date calculator)
- [x] 3.4 Implement review schedule generation on study record creation
- [x] 3.5 Implement daily review query API (grouped by subject)
- [x] 3.6 Implement "mark as mastered" API
- [x] 3.7 Implement review speed adjustment API
- [x] 3.8 Build study record page (Web frontend: rich text editor, create/view)
- [x] 3.9 Build review center page (Web frontend: today's review list, group by subject)

## 4. Exam Score Tracking (exam-tracking spec)

- [x] 4.1 Create ExamResult model + migration
- [x] 4.2 Implement exam result CRUD API (with exam_type filter)
- [x] 4.3 Implement score_rate calculation (auto-compute on save)
- [x] 4.4 Implement score rate trend chart data API (per subject, multi-subject comparison)
- [x] 4.5 Build exam score entry page (Web frontend)
- [x] 4.6 Build score tracking chart page (Web frontend: line chart with filters)

## 5. Dashboard

- [x] 5.1 Implement dashboard summary API (today's reviews, recent wrong problems, score summary)
- [x] 5.2 Build dashboard page (Web frontend)

## 6. Exam Paper OCR & Problem Recognition (exam-paper-ocr spec)

- [x] 6.1 Deploy PaddleOCR service (Docker container, REST API wrapper)
- [x] 6.2 Create WrongProblem model + migration
- [x] 6.3 Implement image upload API (save to MinIO)
- [x] 6.4 Implement OCR recognition API (call PaddleOCR, return text)
- [x] 6.5 Implement AI problem evaluation API (call LLM to judge correctness)
- [x] 6.6 Implement AI solution generation API (text solution + diagram generation)
- [ ] 6.7 Implement SVG geometry diagram generator (for math problems) — _deferred_
- [ ] 6.8 Implement MathJax formula + Chart.js graph integration (for function problems) — _deferred_
- [ ] 6.9 Implement flowchart/schematic generator (for physics/chemistry problems) — _deferred_
- [x] 6.10 Implement wrong problem auto-collection API
- [x] 6.11 Build paper photo upload page (Web frontend: camera/gallery + preview)
- [x] 6.12 Build wrong problem notebook page (Web frontend: browse by subject/knowledge point)
- [x] 6.13 Build problem solution page (Web frontend: steps + diagrams)

## 7. Paper Management (paper-management spec)

- [x] 7.1 Create ExamPaper and PaperAnnotation models + migration
- [x] 7.2 Implement exam paper upload and archive API
- [x] 7.3 Implement paper library query API (filter by subject/exam type/date)
- [x] 7.4 Implement handwriting erasure API (PaddleOCR + image inpainting)
- [x] 7.5 Implement clean version download API
- [x] 7.6 Implement paper annotation CRUD API
- [x] 7.7 Build paper library page (Web frontend: grid/list view, filters)
- [x] 7.8 Build paper detail page (Web frontend: image viewer + annotation toolbar)
- [x] 7.9 Build "erase handwriting" feature page (Web frontend: before/after comparison)

## 8. Similar Problems (similar-problems spec)

- [x] 8.1 Create SimilarProblem model + migration
- [x] 8.2 Implement similar problem generation API (LLM call)
- [x] 8.3 Implement solution approach API (step-by-step + diagram)
- [x] 8.4 Build similar problem page (Web frontend: practice card with show/hide solution)

## 9. Weak Point Analysis & Smart Exam Generation (weak-point-analysis spec)

- [x] 9.1 Create WeakPoint, PracticePaper, LearningAdvice models + migration
- [x] 9.2 Implement weak point analysis engine (aggregate wrong problems + exam data)
- [x] 9.3 Implement weak point visualization data API (radar chart / heatmap)
- [x] 9.4 Implement smart practice paper generation API (LLM call, progressive difficulty)
- [x] 9.5 Implement learning diagnosis report API (suggestions, study methods, memory techniques)
- [x] 9.6 Build weak point analysis page (Web frontend: radar chart, mastery level table)
- [x] 9.7 Build smart paper generation page (Web frontend: weak point selection, preview, adjust)
- [x] 9.8 Build learning diagnosis report page (Web frontend: structured report view)

## 10. Android App (Flutter)

- [ ] 10.1 Build Flutter API client layer (auto-generated from FastAPI OpenAPI)
- [ ] 10.2 Build Flutter login/register pages
- [ ] 10.3 Build Flutter dashboard page
- [ ] 10.4 Build Flutter study records pages
- [ ] 10.5 Build Flutter exam score tracking pages
- [ ] 10.6 Build Flutter paper upload and library pages
- [ ] 10.7 Build Flutter wrong problem and solution pages
- [ ] 10.8 Build Flutter review center page
- [ ] 10.9 Build Flutter weak point analysis and smart paper pages
