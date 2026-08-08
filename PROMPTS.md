# PROMPTS.md

## Project

InterviewOS - Adaptive AI Interview Agent for AI Cohort graduates.

## AI Tools Used

- ChatGPT / Codex for architecture planning, implementation guidance, debugging, and documentation.
- Add any other tools used by the team during the hackathon here.

## Goal

Build an AI interviewer that uses curriculum and candidate journey JSON to conduct a realistic multi-turn technical interview, adapt follow-up questions, maintain context by `sessionId`, and produce structured final feedback.

## Prompt Log

### 1. Problem Understanding and Scope

**Prompt:**
We have less than 20 hours for a hackathon. The problem asks us to build an AI Interview Agent for a 31-day AI Cohort using curriculum JSON, candidate profiles, and a required API contract. What should we build to satisfy the requirements without overengineering?

**AI Output Used:**
- Use an InterviewState-driven architecture.
- Keep in-memory/session-based state for the required endpoint.
- Build text interview first; keep video/audio secondary.
- Guarantee 8+ questions and 4+ curriculum days.

**Human Decisions:**
- Reuse the existing VivaAI interview room boilerplate.
- Preserve video/audio features but make text the reliable core.

### 2. Architecture Planning

**Prompt:**
How should we structure the interviewer so it feels adaptive and not like a scripted questionnaire?

**AI Output Used:**
- Candidate Analyzer
- Curriculum Retriever
- Interview Planner
- Answer Evaluator
- Decision Engine
- Feedback Generator

**Files Changed:**
- `services/cohort_data.py`
- `services/candidate_analyzer.py`
- `services/interview_engine.py`

### 3. Candidate JSON Interpretation

**Prompt:**
How do we interpret candidate missions, attempts, skipped topics, and signals from the supplied JSON?

**AI Output Used:**
- Attempts <= 1 become strong topics.
- Attempts >= 3 become probe topics.
- Skipped topics are avoided or treated carefully.
- Missions completed and first-try count determine difficulty.

**Files Changed:**
- `services/candidate_analyzer.py`

### 4. API Contract

**Prompt:**
Implement the required `POST /api/interview` endpoint. It must start with `{ sessionId, candidate }`, continue with `{ sessionId, message }`, and end with `{ reply, done, feedback }`.

**AI Output Used:**
- Added exact endpoint.
- Kept session memory keyed by `sessionId`.
- Returned final feedback in required shape.

**Files Changed:**
- `routes/interview_routes.py`
- `utils/validation.py`

### 5. Interview Room UI

**Prompt:**
Convert the existing VivaAI interview room into a text-first adaptive cohort interview room while preserving video/audio features.

**AI Output Used:**
- Candidate-specific room creation.
- Question progress and topic badge.
- Interview journey sidebar.
- Typed answer box with optional voice recording.
- Final report rendering and download button.

**Files Changed:**
- `templates/index.html`
- `templates/interview_room.html`
- `static/js/interview.js`
- `static/css/style.css`

### 6. Report Generation

**Prompt:**
How should the final report be structured for judges and candidates?

**AI Output Used:**
- Summary
- Strengths
- Gaps
- Recommended next steps
- Downloadable text report

**Files Changed:**
- `routes/interview_routes.py`
- `models/interview.py`


