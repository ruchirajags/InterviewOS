Project

InterviewOS - Adaptive AI Interview Agent for AI Cohort graduates.

AI Tools Used

ChatGPT / Codex for architecture planning, implementation guidance, debugging support, and documentation refinement.

Claude (Anthropic) for the landing-page rebuild, dashboard/landing split, and frontend-backend architecture audit documented in entries 11-15 below.

AI assistance was used to reason about system design, API flow, prompt structure, adaptive interview logic, and report formatting.

Goal

Build an AI interviewer that uses the supplied curriculum and candidate journey JSON to conduct a realistic multi-turn technical interview, adapt follow-up questions, maintain session context by sessionId, and produce structured final feedback.

AI Usage Log

1. Product Architecture

Prompt: Design a clean architecture for an AI Interview Agent that uses curriculum JSON, candidate profiles, and a required POST /api/interview endpoint. The system must conduct an adaptive multi-turn interview and return structured feedback.

AI Output Used:

InterviewState-based architecture.

Candidate Analyzer, Curriculum Retriever, Interview Planner, Answer Evaluator, Decision Engine, and Feedback Generator.

Text-first interview flow with optional voice/video enhancement.

Implemented In:

services/interview_engine.py

services/candidate_analyzer.py

services/cohort_data.py

2. Candidate Journey Interpretation

Prompt: How should candidate profile data such as completed missions, attempts, skipped topics, and learning signals be interpreted for personalized technical interviews?

AI Output Used:

Completed missions determine eligible interview topics.

First-attempt missions indicate stronger areas.

High-attempt or failed missions become probe topics.

Skipped topics are avoided or asked only at a high-level awareness depth.

Candidate difficulty is derived from completion and first-try signals.

Implemented In:

services/candidate_analyzer.py

3. Interview Planning

Prompt: Create a reliable interview plan that guarantees at least 8 questions across at least 4 curriculum days while still feeling personalized.

AI Output Used:

Plan around high-value AI engineering days such as embeddings, vector databases, retrieval, prompting, backend APIs, agents, MCP, deployment, and observability.

Use a 10-question flow to comfortably exceed the minimum requirement.

Include adaptive follow-ups without allowing the interview to get stuck on one topic.

Implemented In:

services/interview_engine.py

4. Adaptive Follow-Up Logic

Prompt: Design a simple decision engine for technical interview follow-ups based on answer quality.

AI Output Used:

Evaluate answers using topic-specific signals.

Strong answers lead to deeper production-focused questions.

Partial answers lead to clarification questions.

Weak answers lead to foundational probes.

Topic depth limits prevent infinite follow-ups.

Implemented In:

services/interview_engine.py

5. API Contract

Prompt: Implement the required hackathon API contract for POST /api/interview with start, conversation, and final feedback responses.

AI Output Used:

Start request accepts sessionId and candidate.

Conversation request accepts sessionId and message.

Final response returns done: true and a feedback object containing summary, strengths, gaps, and next.

Implemented In:

routes/interview_routes.py

utils/validation.py

6. Interview Room Experience

Prompt: Design a clean interface for a personalized technical interview with candidate selection, interview progress, current topic, typed answers, optional voice input, and final report output.

AI Output Used:

Candidate dashboard generated from candidate JSON.

Candidate-specific interview room.

Topic and question progress indicators.

Interview journey sidebar.

Text answer flow with optional voice recording.

Final report section with download support.

Implemented In:

templates/index.html

templates/interview_room.html

static/js/interview.js

static/css/style.css

7. Feedback Report

Prompt: Create a final technical readiness report format that is concise, actionable, and aligned with the required feedback schema.

AI Output Used:

Summary of interview performance.

Strengths based on strong answer areas.

Gaps based on weak or missing concepts.

Recommended next steps for interview preparation.

Downloadable report route.

Implemented In:

services/interview_engine.py

routes/interview_routes.py

8. Validation and Testing

Prompt: How should the project be verified against the minimum requirements?

AI Output Used:

Confirm /api/interview starts with a candidate object.

Confirm subsequent turns use only sessionId and message.

Confirm interview reaches completion after 10 questions.

Confirm final feedback includes summary, strengths, gaps, and next.

Confirm candidate dashboard loads from JSON.

Verification Performed:

Python syntax compilation.

Flask test-client smoke test for /api/interview.

Candidate API smoke test for /api/candidates.

9. Answer Validation and Retry Handling

Status: Implemented Files updated:

services/interview_engine.py

static/js/interview.js

Prompt / AI Assistance Used: Help improve the interview engine so that unclear gibberish answers are rejected without advancing the interview, while honest uncertainty such as "I am not sure" is treated as a weak but valid answer.

Implemented Logic:

Empty or random responses are rejected.

Repeated meaningless text is rejected.

Very short non-technical answers are rejected.

Uncertainty phrases are accepted as weak answers.

Weak answers are evaluated and included in the final report.

Invalid answers do not increase the question count.

The same question is repeated after an invalid response.

Reasoning: A real interviewer should distinguish between a candidate who is unsure and a candidate who has not provided a usable answer. This makes the interview more realistic and prevents unfair scoring.

Verification: Tested with:

Gibberish input

Repeated words

Short unclear answers

"I am not sure"

Short technical answers

Normal technical answers

10. Interview Start and Retry Flow

Status: Implemented Files updated:

services/interview_engine.py

static/js/interview.js

Prompt / AI Assistance Used: Fix the interview flow so the first question appears correctly and retry messages are clear for the candidate.

Implemented Logic:

The interview starts by creating a personalized session state.

The first question is returned from the generated interview plan.

Retry messages are displayed clearly.

The current question is repeated below the retry message.

Invalid responses no longer break the interview flow.

Reasoning: The candidate should never lose track of the question after an invalid answer. Repeating the question makes the experience smoother and closer to a real interview.

11. Editorial Landing Page Rebuild (Reference-Image Source of Truth)

Status: Implemented Files updated:

static/css/landing.css (new)

templates/index.html

Prompt / AI Assistance Used: Rebuild the landing page to match a supplied reference image exactly: warm off-white/black editorial visual language, Bebas Neue + DM Sans typography, lime/pink/purple/beige flat accents, no gradients/glassmorphism. Required sections: header, two-column hero with a live-interview-preview mock, metrics strip, candidate dashboard table (later split out, see #12), "How InterviewOS Works" 3-step flow, footer.

Implemented Logic:

New isolated stylesheet scoped entirely under .landing-page so none of it leaks into interview_room.html / create_interview.html, which keep using style.css's existing dark theme.

Header: wordmark with lime accent, nav, pill CTA.

Hero: eyebrow, condensed headline with a skewed lime highlight, CTA, three signal items, and a black "Live Interview Preview" mock card (question/response/follow-up/progress bar) with a CSS dot-grid decoration.

Metrics strip with three colored icon blocks.

Candidate dashboard rendered as a real <table> (not cards) inside a full-bleed black section, populated from the existing /api/candidates endpoint — search filter and a "view all" toggle added client-side.

"How InterviewOS Works" 3-step flow with a pink/lime SVG dot-and-line decoration.

Footer with brand mark, link columns, and bottom bar.

Reasoning: The person explicitly required pixel-level fidelity to the reference image and rejected generic AI-SaaS visual patterns (gradients, glassmorphism, rounded cards everywhere). Isolating styles under .landing-page was necessary because style.css is shared with the interview room and must not be repainted.

Verification: Manual visual comparison against the reference image; confirmed /api/candidates and /api/interview/create calls and the createRoom() redirect flow were carried over unchanged from the previous index.html.

12. ABTalks Marquee, Dashboard/Landing Split, Navbar Reroute

Status: Implemented Files updated:

static/css/landing.css

templates/index.html

templates/dashboard.html (new)

routes/interview_routes.py (one additive route)

Prompt / AI Assistance Used: Remove the candidate dashboard table from the landing page (landing page should end at Header → Hero → Marquee → Metrics → How It Works → Footer), add a scrolling ABTalks hackathon marquee below the hero, and change the navbar CTA from "COHORT DEMO →" to "DASHBOARD →", pointing both it and the hero's "OPEN CANDIDATE DASHBOARD →" CTA at a real dashboard destination.

Implemented Logic:

Moved the entire candidate-table section and its rendering script out of index.html into a new templates/dashboard.html, unchanged in behavior (same /api/candidates fetch, same createRoom() → /api/interview/create → redirect flow).

Added a new, purely additive Flask route (GET /dashboard → render_template("dashboard.html")) since no dashboard-only route previously existed — nothing else in routes/interview_routes.py was touched.

Added .l-marquee — a CSS-only (no JS library) horizontally scrolling ticker with duplicated content for a seamless loop, pause-on-hover, and a prefers-reduced-motion override. "EXPLORE THE HACKATHON →" links to https://www.abtalks.in/hackathon/submission.

Updated both CTAs (l-header-cta, hero l-cta-primary) to href="/dashboard".

Reasoning: Keeping the candidate table's logic in one place (now dashboard.html) avoids duplicating interview-creation logic across two templates, and the marquee needed to be genuinely dependency-free per instructions.

Verification: Confirmed balanced HTML tags after the section move; confirmed no #candidates references remained in index.html; confirmed /dashboard count and route wiring.

13. Landing Page Centering & Subtle Animation Pass

Status: Implemented Files updated:

static/css/landing.css

templates/index.html

Prompt / AI Assistance Used: Narrow/centralize the overall page composition (page felt too spread out on wide viewports) without flattening the asymmetric two-column hero into generic centered SaaS layout, and add restrained entrance/reveal animation — hero staggered fade-up, live-preview card fade/scale-in, progress bar growing from 0, and scroll-triggered fade-up for metrics/how-it-works/footer. Desktop/laptop-only; no new responsive breakpoints.

Implemented Logic:

Single shared .l-container narrowed from 1240px/32px padding to 1120px/40px padding, reused consistently by header, hero, metrics, how-it-works, and footer (no per-section overrides).

@keyframes l-fade-up staggered across .l-hero-left > * (eyebrow → headline → copy → CTA → signals) via nth-child delays.

@keyframes l-preview-in for the live-preview card; @keyframes l-bar-grow for the session-progress bar, switched from a hard-coded inline width:37% to a CSS-variable-driven --fill so the keyframe can animate it.

New .l-reveal / .l-reveal--visible utility + a small vanilla IntersectionObserver script (added before </body>) applied to the metrics, how-it-works, and footer sections — one-shot, unobserves after firing.

All of the above disabled under prefers-reduced-motion: reduce.

Reasoning: The marquee's top/bottom border lines were deliberately kept full-bleed (edge-to-edge) rather than joining the narrowed container, since a horizontally-scrolling ticker loses its effect if width-constrained — everything else joined the same grid.

Verification: Confirmed tag balance in index.html after edits; confirmed --fill:37% present in the preview markup; confirmed l-reveal classes applied to exactly the three intended sections.

14. Dashboard + Interview Room Visual Redesign — INVESTIGATION ONLY, NOT YET IMPLEMENTED

Status: Inspected, not implemented Files reviewed:

templates/dashboard.html

templates/interview_room.html

static/js/interview.js, static/js/audio.js, static/js/webrtc.js, static/js/socket.js

data/candidates.json (level/difficulty field already available via services/candidate_analyzer.py)

Prompt / AI Assistance Used: Redesign the dashboard into a left candidate sidebar (search + level filter: All/Advanced/Intermediate/Foundational) + compact candidate header + interview-workspace CTA on the right, and simplify interview_room.html from many separate rounded cards into one cohesive workspace panel — visual only, all existing IDs/routes/JS behavior preserved.

Status of work: No files were modified for this item. The architecture decision was made to keep the dashboard linking out to interview_room.html (per instruction, to avoid a duplicate interview implementation) rather than embedding the live interview inside the dashboard page. Every DOM id interview.js/audio.js/webrtc.js/socket.js depend on (startBtn, question, journeyList, aiIndicator, localVideo, muteBtn, statusMsg, etc.) was catalogued so a future redesign pass doesn't break existing behavior. Implementation is pending.

15. Frontend–Backend Connection Audit — INVESTIGATION ONLY, NOT YET IMPLEMENTED

Status: Inspected, not implemented Files reviewed:

app.py, routes/interview_routes.py, routes/ai_routes.py

services/interview_engine.py, services/candidate_analyzer.py, services/cohort_data.py

models/interview.py, utils/validation.py

templates/index.html, templates/dashboard.html, templates/interview_room.html, static/js/interview.js

Prompt / AI Assistance Used: Map the full frontend → backend architecture: which routes exist, which are actually called by the frontend, what's hardcoded vs. dynamic, and what (if anything) needs connecting.

Findings (see conversation for full detail):

The core flow (candidates → room creation → POST /api/interview adaptive engine → evaluation → feedback → report download) is already genuinely wired end-to-end, not mocked.

Landing page's "Live Interview Preview" is intentionally static marketing content (left untouched, per instruction).

create_interview.html's free-text flow silently falls back to a generic interview plan when no real candidate_id is available.

/api/ai/question, /api/ai/report (Sarvam-based) and the #aiVoice TTS element exist but have no caller in interview.js — orphaned, left untouched per instruction (no /api/ai/speak was created).

Status of work: Investigation only. Explicit implementation instructions were received (dashboard/candidate loading, candidate-ID-aware room creation, dynamic UI updates, answer submission, completion/report handling) but no code changes have been made yet for this item — pending the next implementation pass.

16. Frontend–Backend Connection Debugging

Tool: ChatGPTDate: 2026-08-09

Prompt:

I want to connect my frontend with the backend. The existing architecture already has the dashboard, interview room, Flask routes, adaptive interview engine, candidate API, answer submission, and report flow. Help me identify why the frontend is returning 400 Invalid input when starting the interview and how to connect the existing frontend correctly without duplicating the backend logic.

Purpose: Debug the existing frontend-to-backend interview flow without rebuilding the interview engine.

AI Output Used:

Inspected the existing frontend/backend request flow.

Identified that the browser was sending {'sessionId': '', 'candidate': {'id': ''}}.

Identified the backend validation failure: sessionId must contain at least one character.

Confirmed that the adaptive interview engine already exists; the frontend was failing to provide the required session/candidate identifiers.

Recommended using the existing room ID as the interview sessionId and ensuring the selected candidate's real ID is passed to the start request.

17. Backend Validation Error Diagnostics

Tool: ChatGPTDate: 2026-08-09

Prompt:

Add temporary validation diagnostics around CohortInterviewRequest so the backend prints the validation error and the exact JSON received from the frontend, then return the error details as JSON with HTTP 400.

Purpose: Make the frontend/backend contract failure visible instead of returning only a generic Invalid input message.

AI Output Used:

Added validation logging around CohortInterviewRequest.

Printed VALIDATION ERROR and REQUEST JSON.

Returned structured JSON containing error, details, and received.

This exposed the failing payload: sessionId: "" and candidate.id: "".

Implemented In:

routes/interview_routes.py

18. Frontend Start-Interview Debugging

Tool: ChatGPTDate: 2026-08-09

Prompt:

The browser console shows POST /api/interview returning 400, followed by Start interview failed: Error: Invalid input. The Flask log says sessionId is empty and candidate.id is empty. Explain what needs to be fixed in the frontend and give me an Antigravity prompt to fix it without changing the UI.

Purpose: Translate the backend validation output into a concrete frontend fix.

AI Output Used:

Traced the request from interview.js to /api/interview.

Confirmed that the start request must contain a valid sessionId and candidate ID.

Recommended fixing the source of those values rather than weakening Pydantic validation.

Preserved InterviewEngine.start() as the single source of truth.

19. Git Branch, Commit, and Pull Request Workflow

Tool: ChatGPTDate: 2026-08-09

Prompt:

I want to push these changes to Git from my branch. Tell me the steps and give me a good commit message. This is my first PR and the changes include the landing page, dashboard UI/UX, and the frontend/backend connection fixes.

Purpose: Safely commit the completed work to a feature branch and raise a PR against the teammate's main repository.

AI Output Used:

Recommended checking the current branch and working tree before committing.

Recommended staging only the intended changes.

Suggested a descriptive commit message covering the frontend/UI and integration work.

Explained the fork → feature branch → push → PR workflow.

Explained that after the teammate merges the PR into main, the fork should be synchronized before future work.

20. Landing Page Animation

Tool: ChatGPTDate: 2026-08-09

Prompt:

I want to add animation to the laptop/live interview preview on the current InterviewOS landing page. Maybe typing movements inside the laptop or candidates' names switching. Keep the existing design and make the animation subtle and polished.

Purpose: Add motion to the landing-page product preview without turning it into a generic animated SaaS page.

AI Output Used:

Recommended lightweight CSS/vanilla-JS animation.

Suggested rotating candidate names/details and simulating a typing effect inside the laptop preview.

Preserved the existing editorial landing-page style and layout.

Implemented In / Intended For:

templates/index.html

static/css/landing.css

21. InterviewOS Logo Integration

Tool: ChatGPTDate: 2026-08-09

Prompt:

I added static/images/interviewos-logo.png. Help me replace the existing text-only InterviewOS branding in index.html and landing.css, and adjust the logo size so it properly occupies the navbar height instead of appearing tiny.

Purpose: Replace the temporary text branding with the new InterviewOS logo while keeping the navbar balanced.

AI Output Used:

Recommended loading the logo through Flask's static path.

Recommended controlling the rendered size through navbar image CSS.

Adjusted sizing guidance so the logo visually fills the navbar height while remaining proportional.

Applied the same branding approach to the dashboard navbar.

Implemented In / Intended For:

templates/index.html

templates/dashboard.html

static/css/landing.css

static/css/dashboard.css

static/images/interviewos-logo.png

22. Prompt Documentation Structure

Tool: ChatGPTDate: 2026-08-09

Prompt:

I want to maintain prompts.md for myself and my teammate in the same folder. I want a prompts directory with individual Markdown files such as ruchira.md so each contributor can collect their real Claude/GPT prompts without mixing them together.

Purpose: Establish a shared prompt-audit structure for the project.

AI Output Used:

Recommended structure:

prompts/
├── ruchira.md
├── teammate.md
└── ...

Each contributor keeps their own prompt log in a Markdown file. The files contain real prompts used during development, together with their purpose and concrete implementation decision/output.

Current File:

prompts/ruchira.md

23. Combined AI Prompt Log

Tool: ChatGPTDate: 2026-08-09

Prompt:

I have a PROMPTS.md containing the Claude prompt history. Add the ChatGPT prompts/conversations used during the InterviewOS development and combine them into one Markdown file while keeping the existing Claude entries.

Purpose: Maintain one auditable record of AI-assisted development across Claude and ChatGPT.

AI Output Used:

Preserved the existing Claude prompt history.

Added ChatGPT entries for frontend-backend debugging, validation diagnostics, Git/PR workflow, landing animation, logo integration, and prompt documentation.

Kept entries focused on the prompt, purpose, concrete output/decision, and affected files rather than reproducing full chat transcripts.

