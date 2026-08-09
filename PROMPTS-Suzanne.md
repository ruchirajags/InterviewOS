# PROMPTS.md

## Project

InterviewOS - Adaptive AI Interview Agent for AI Cohort graduates.

## AI Tools Used

- ChatGPT / Codex for architecture planning, implementation guidance, debugging, UI iteration, report design, testing strategy, and documentation.
- AI assistance was used to reason about system architecture, API flow, adaptive interview logic, answer validation, scoring, report formatting, frontend polish, and deployment readiness.

## Goal

Build an AI interviewer that uses the supplied curriculum and candidate journey JSON to conduct a realistic multi-turn technical interview, adapt follow-up questions, maintain session context by `sessionId`, and produce structured final feedback with a downloadable readiness report.

## AI Usage Log

### 1. Product Architecture

**Prompt:**
Design a clean architecture for an AI Interview Agent that uses curriculum JSON, candidate profiles, and a required `POST /api/interview` endpoint.

**AI Output Used:**
- Text-first Flask architecture.
- Candidate Analyzer, Curriculum Loader, Interview Planner, Interview Engine, Answer Evaluator, Feedback Generator, and Report Download route.
- Optional voice/video kept as secondary enhancement.

**Implemented In:**
- `app.py`
- `routes/interview_routes.py`
- `services/interview_engine.py`
- `services/candidate_analyzer.py`
- `services/cohort_data.py`

---

### 2. Candidate Journey Interpretation

**Prompt:**
How should completed missions, attempts, skipped topics, and learning signals be interpreted for personalized interviews?

**AI Output Used:**
- Completed missions determine eligible interview topics.
- Strong days and weak days influence interview planning.
- Skipped or weaker areas are handled carefully.
- Candidate-specific profile summaries are generated for the dashboard and interview engine.

**Implemented In:**
- `services/candidate_analyzer.py`
- `services/cohort_data.py`

---

### 3. Adaptive Interview Planning

**Prompt:**
Create a reliable interview plan that asks at least 8 questions across at least 4 curriculum days while still feeling personalized.

**AI Output Used:**
- Use a 10-question interview flow.
- Cover multiple AI Cohort days such as embeddings, vector databases, RAG, prompt engineering, agents, MCP, deployment, and production monitoring.
- Avoid ending too early before enough planned days are covered.
- Limit follow-ups so the interview does not get stuck on one topic.

**Implemented In:**
- `services/interview_engine.py`

---

### 4. Question Generation and Follow-Ups

**Prompt:**
Make the interview feel less like a static questionnaire and more like a real technical interview.

**AI Output Used:**
- Questions are generated from curriculum day metadata and candidate-specific plan entries.
- Follow-ups are selected based on previous answer quality.
- Strong answers receive production-focused follow-ups.
- Weak answers receive grounding or clarification prompts.
- Follow-ups only happen when there is enough room left in the 10-question flow.

**Implemented In:**
- `services/interview_engine.py`

---

### 5. Answer Validation

**Prompt:**
Improve the backend so gibberish answers are rejected, but honest uncertainty such as "I am not sure" is treated as weak but valid.

**AI Output Used:**
- Empty answers are rejected.
- Random repeated text and gibberish are rejected.
- Invalid answers do not advance the question count.
- Uncertainty phrases are accepted and evaluated as weak.
- Retry messages repeat the current question clearly.

**Implemented In:**
- `services/interview_engine.py`
- `static/js/interview.js`

---

### 6. Answer Scoring

**Prompt:**
Improve scoring so answers are evaluated more fairly instead of repeatedly showing the same low score.

**AI Output Used:**
- Score answers using technical keyword coverage, depth signals, weak signals, and uncertainty signals.
- Reward concrete concepts such as latency, metrics, tradeoffs, evaluation, retrieval quality, schema validation, monitoring, and deployment reliability.
- Penalize vague or overly generic answers.
- Store per-answer evaluations for the final report.

**Implemented In:**
- `services/interview_engine.py`

---

### 7. Required API Contract

**Prompt:**
Implement the required hackathon API contract for `POST /api/interview`.

**AI Output Used:**
- Start request accepts `sessionId` and `candidate`.
- Conversation request accepts `sessionId` and `message`.
- Final response returns `done: true` and structured `feedback`.
- Errors return JSON responses instead of breaking the frontend.

**Implemented In:**
- `routes/interview_routes.py`
- `utils/validation.py`

---

### 8. Candidate Dashboard

**Prompt:**
Create a dashboard where evaluators can view all candidate profiles and start an interview for any candidate.

**AI Output Used:**
- Dashboard loads profiles from `data/candidates.json`.
- Candidate cards show learner metadata and progress.
- Selecting a candidate creates a candidate-specific interview session.
- Interview room receives candidate and session context.

**Implemented In:**
- `templates/dashboard.html`
- `static/css/dashboard.css`
- `static/js/interview.js`
- `routes/interview_routes.py`

---

### 9. Interview Room UX

**Prompt:**
Polish the interview room so it supports text-first interviews, optional media, clear answer submission, and final feedback.

**AI Output Used:**
- Text-only interview flow remains primary.
- Optional camera/microphone controls are preserved.
- Candidate answer box was improved.
- Last submitted answer was separated visually.
- End Early and completed interview states were clarified.
- Download report is only shown for completed interviews.

**Implemented In:**
- `templates/dashboard.html`
- `templates/interview_room.html`
- `static/css/dashboard.css`
- `static/css/interview_room.css`
- `static/js/interview.js`

---

### 10. Landing Page Polish

**Prompt:**
Improve the landing page so it looks more unique and polished for a hackathon demo.

**AI Output Used:**
- Centered landing page hero.
- Laptop-style dashboard preview.
- Sticky navbar.
- Marquee interaction.
- Cleaner footer and dashboard navigation.

**Implemented In:**
- `templates/index.html`
- `static/css/landing.css`

---

### 11. Feedback Generation

**Prompt:**
Generate actionable feedback at the end of the interview.

**AI Output Used:**
- Summary includes candidate name, question count, days covered, and average score.
- Strengths are generated from high-scoring areas.
- Gaps are generated from weak or missing concepts.
- Next steps are practical interview-preparation recommendations.

**Implemented In:**
- `services/interview_engine.py`

---

### 12. Downloadable Readiness Report

**Prompt:**
Create a clean downloadable HTML readiness report with candidate details, score, summary, strengths, gaps, next steps, and question-by-question analysis.

**AI Output Used:**
- HTML report instead of plain text.
- File name format: date plus app name.
- Includes candidate name, role/session, questions answered, curriculum days covered, overall score, generated date/time.
- Includes question, candidate answer, expected answer direction, missing concepts, and score for each answer.
- Supports browser Print / Save PDF.

**Implemented In:**
- `routes/interview_routes.py`
- `templates/report_download.html`
- `models/interview.py`

---

### 13. Debugging and Error Fixes

**Prompt:**
Fix runtime errors in the interview and report flow.

**AI Output Used:**
- Fixed missing answer validation method issue.
- Fixed interview start flow when the first question did not appear.
- Fixed invalid-answer retry handling.
- Fixed report route syntax issue.
- Fixed download route to return HTML instead of text.
- Confirmed Python, JavaScript, and Jinja syntax.

**Implemented In:**
- `services/interview_engine.py`
- `routes/interview_routes.py`
- `static/js/interview.js`
- `templates/report_download.html`

---

### 14. Testing Strategy

**Prompt:**
Create fast testing answers for good, weak, and invalid responses so the report and scoring can be verified quickly.

**AI Output Used:**
- Good answer set for high-score report testing.
- Mixed answer set for gap analysis testing.
- Gibberish inputs for invalid-answer testing.
- Manual test checklist for full interview completion and report download.

**Verification Performed:**
- Candidate dashboard loads.
- Candidate-specific interview starts.
- Full interview completes.
- Scores update correctly.
- Feedback appears.
- Early end does not generate ambiguous download actions.
- Downloadable HTML report works after full completion.
- Syntax checks passed for Python, JavaScript, and Jinja template files.

## Final Notes

InterviewOS is a text-first adaptive technical interviewer. Optional audio/video support is preserved as an enhancement, but the core hackathon requirements are satisfied through the curriculum-grounded interview engine, candidate-specific planning, multi-turn context, adaptive follow-ups, structured feedback, and downloadable readiness report.