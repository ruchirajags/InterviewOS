# PROMPTS.md

## Project

InterviewOS - Adaptive AI Interview Agent for AI Cohort graduates.

## AI Tools Used

- ChatGPT / Codex for architecture planning, implementation guidance, debugging support, and documentation refinement.
- AI assistance was used to reason about system design, API flow, prompt structure, adaptive interview logic, and report formatting.

## Goal

Build an AI interviewer that uses the supplied curriculum and candidate journey JSON to conduct a realistic multi-turn technical interview, adapt follow-up questions, maintain session context by `sessionId`, and produce structured final feedback.

## AI Usage Log

### 1. Product Architecture

**Prompt:**
Design a clean architecture for an AI Interview Agent that uses curriculum JSON, candidate profiles, and a required `POST /api/interview` endpoint. The system must conduct an adaptive multi-turn interview and return structured feedback.

**AI Output Used:**
- InterviewState-based architecture.
- Candidate Analyzer, Curriculum Retriever, Interview Planner, Answer Evaluator, Decision Engine, and Feedback Generator.
- Text-first interview flow with optional voice/video enhancement.

**Implemented In:**
- `services/interview_engine.py`
- `services/candidate_analyzer.py`
- `services/cohort_data.py`

---

### 2. Candidate Journey Interpretation

**Prompt:**
How should candidate profile data such as completed missions, attempts, skipped topics, and learning signals be interpreted for personalized technical interviews?

**AI Output Used:**
- Completed missions determine eligible interview topics.
- First-attempt missions indicate stronger areas.
- High-attempt or failed missions become probe topics.
- Skipped topics are avoided or asked only at a high-level awareness depth.
- Candidate difficulty is derived from completion and first-try signals.

**Implemented In:**
- `services/candidate_analyzer.py`

---

### 3. Interview Planning

**Prompt:**
Create a reliable interview plan that guarantees at least 8 questions across at least 4 curriculum days while still feeling personalized.

**AI Output Used:**
- Plan around high-value AI engineering days such as embeddings, vector databases, retrieval, prompting, backend APIs, agents, MCP, deployment, and observability.
- Use a 10-question flow to comfortably exceed the minimum requirement.
- Include adaptive follow-ups without allowing the interview to get stuck on one topic.

**Implemented In:**
- `services/interview_engine.py`

---

### 4. Adaptive Follow-Up Logic

**Prompt:**
Design a simple decision engine for technical interview follow-ups based on answer quality.

**AI Output Used:**
- Evaluate answers using topic-specific signals.
- Strong answers lead to deeper production-focused questions.
- Partial answers lead to clarification questions.
- Weak answers lead to foundational probes.
- Topic depth limits prevent infinite follow-ups.

**Implemented In:**
- `services/interview_engine.py`

---

### 5. API Contract

**Prompt:**
Implement the required hackathon API contract for `POST /api/interview` with start, conversation, and final feedback responses.

**AI Output Used:**
- Start request accepts `sessionId` and `candidate`.
- Conversation request accepts `sessionId` and `message`.
- Final response returns `done: true` and a `feedback` object containing `summary`, `strengths`, `gaps`, and `next`.

**Implemented In:**
- `routes/interview_routes.py`
- `utils/validation.py`

---

### 6. Interview Room Experience

**Prompt:**
Design a clean interface for a personalized technical interview with candidate selection, interview progress, current topic, typed answers, optional voice input, and final report output.

**AI Output Used:**
- Candidate dashboard generated from candidate JSON.
- Candidate-specific interview room.
- Topic and question progress indicators.
- Interview journey sidebar.
- Text answer flow with optional voice recording.
- Final report section with download support.

**Implemented In:**
- `templates/index.html`
- `templates/interview_room.html`
- `static/js/interview.js`
- `static/css/style.css`

---

### 7. Feedback Report

**Prompt:**
Create a final technical readiness report format that is concise, actionable, and aligned with the required feedback schema.

**AI Output Used:**
- Summary of interview performance.
- Strengths based on strong answer areas.
- Gaps based on weak or missing concepts.
- Recommended next steps for interview preparation.
- Downloadable report route.

**Implemented In:**
- `services/interview_engine.py`
- `routes/interview_routes.py`

---

### 8. Validation and Testing

**Prompt:**
How should the project be verified against the minimum requirements?

**AI Output Used:**
- Confirm `/api/interview` starts with a candidate object.
- Confirm subsequent turns use only `sessionId` and `message`.
- Confirm interview reaches completion after 10 questions.
- Confirm final feedback includes `summary`, `strengths`, `gaps`, and `next`.
- Confirm candidate dashboard loads from JSON.

**Verification Performed:**
- Python syntax compilation.
- Flask test-client smoke test for `/api/interview`.
- Candidate API smoke test for `/api/candidates`.

