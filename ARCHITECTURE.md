# InterviewOS File Architecture

This project is a trimmed hackathon build based on the VivaAI interview-room boilerplate.

## Tech Stack

- Flask: Python web server, HTML template rendering, and API routes.
- Flask-SocketIO: real-time signaling support for the existing video/WebRTC room.
- Vanilla HTML/CSS/JavaScript: no frontend build step, fast to deploy/debug.
- Pydantic: request validation for API payloads.
- Sarvam AI SDK: optional TTS/STT support inherited from VivaAI.
- In-memory Python dictionaries: session/report state for the hackathon demo.
- JSON files: supplied curriculum and candidate profiles.

## Why Flask Is Relevant

Flask is useful here because the boilerplate already uses it and the hackathon API contract is small. We only need:

- A landing/dashboard page.
- An interview room page.
- `POST /api/interview`.
- A few helper API routes.
- Optional audio/video endpoints.

Using Flask avoids adding React/Vite/FastAPI migration work when the remaining time is tight.

## Required Product Flow

```text
/                          -> candidate dashboard
/api/candidates             -> candidate cards from candidates.json
/api/interview/create       -> creates a room for a selected candidate
/interview/<room_id>        -> candidate-specific interview room
/api/interview              -> required adaptive interview endpoint
/api/interview/<id>/report/download -> downloadable readiness report
```

## Root Files

### app.py

Creates the Flask app, registers blueprints, registers WebRTC socket events, and starts the server.

It no longer initializes SQLite because persistent accounts/history are out of scope.

### config.py

Central configuration for host, port, debug mode, Sarvam API settings, audio output folders, and WebRTC STUN server.

`DATABASE_PATH` can be ignored now; it is leftover config and not used by the current runtime.

### requirements.txt

Python dependencies required to run the app.

### README.md

Judge-facing project explanation: problem, solution, architecture, API contract, run instructions, and demo flow.

### PROMPTS.md

AI usage log required by the hackathon authenticity review. Keep adding entries as you use AI.

### technical-spec.md

Copied official API contract/spec from the hackathon.

### .env / .env.example

Environment variables. `.env` may contain local keys and should not be committed if it has secrets. `.env.example` is safe to keep as a template.

### .gitignore

Prevents generated files, virtual environments, audio outputs, and secrets from being committed.

### LICENSE

Can be kept if you want the public repo to have clear usage terms. It is not required by the hackathon, but harmless.

## data/

### data/curriculum.json

Official 31-day AI Cohort curriculum. Used as the interview knowledge source.

### data/candidates.json

Official synthetic candidate profiles. Used by the dashboard and candidate analyzer.

## services/

### services/cohort_data.py

Loads curriculum and candidate JSON files. Also maps curriculum days to modules and finds candidates by ID.

Used by:

- `routes/interview_routes.py`
- `services/candidate_analyzer.py`
- `services/interview_engine.py`

### services/candidate_analyzer.py

Turns raw candidate missions into interviewer metadata:

- completed days
- skipped days
- failed days
- strong days
- probe days
- difficulty

This is what makes the interview personalized.

### services/interview_engine.py

The core product brain.

Responsible for:

- creating `InterviewState`
- planning 8 curriculum topics
- asking 10 questions
- evaluating each answer
- deciding follow-up vs next topic
- generating final structured feedback

This is the file that satisfies most of the problem statement.

## routes/

### routes/interview_routes.py

Main product routes.

Important endpoints:

- `GET /api/candidates`
- `POST /api/interview`
- `POST /api/interview/create`
- `GET /interview/<room_id>`
- `GET /api/interview/<room_id>/report/download`

### routes/ai_routes.py

Legacy VivaAI optional AI routes:

- `/api/ai/question`
- `/api/ai/report`
- `/api/ai/transcribe`

The new core flow does not depend on these, but they are kept for optional voice/STT/TTS enhancement.

## models/

### models/interview.py

In-memory room/report store.

Stores:

- room ID
- candidate name
- candidate ID
- report
- transcript
- status

This replaced SQLite to keep the hackathon build lean.

## templates/

### templates/index.html

Landing page plus candidate dashboard. Fetches `/api/candidates` and creates candidate-specific rooms.

### templates/create_interview.html

Legacy create-interview page. Not central to the current flow, but harmless if someone visits `/interview/create`.

### templates/interview_room.html

Main interview UI.

Contains:

- optional video panels
- topic/question progress
- interview journey sidebar
- typed answer box
- optional voice recording controls
- final report section
- download report button

## static/

### static/css/style.css

Design system and page styling.

Includes old VivaAI styles plus new candidate dashboard, journey, typed-answer, and report styles.

### static/js/interview.js

Frontend interview loop.

Calls:

- `GET /api/candidates`
- `POST /api/interview`

Updates:

- current question
- progress bar
- topic badge
- journey sidebar
- final report

### static/js/audio.js

Optional voice recording and speech-to-text path. It eventually calls `sendAnswer(answer)`, so voice and typed answers share the same interview engine.

### static/js/webrtc.js

Existing browser media/video logic.

### static/js/socket.js

Socket.IO connection helper for WebRTC signaling.

### static/audio/

Generated audio files for TTS and recorded answers if the optional audio path is used.

## ai/

### ai/question_engine.py

Legacy generic question generator using Sarvam. Not used by the new required `/api/interview` flow.

Kept only as optional fallback/extension.

### ai/report_engine.py

Legacy generic report generator using Sarvam. Not used by the new required feedback path.

Kept only as optional fallback/extension.

### ai/stt_engine.py

Optional speech-to-text helper for recorded candidate answers.

### ai/tts_engine.py

Optional text-to-speech helper for AI interviewer voice.

## utils/

### utils/validation.py

Pydantic request models for both legacy VivaAI endpoints and the required hackathon endpoint.

### utils/sanitization.py

Cleans AI output and removes hidden reasoning tags.

### utils/timer.py

Legacy timer utility. The current frontend also manages its own timer.

### utils/audio_recorder.py

Legacy audio helper. Kept because the audio path is still a secondary enhancement.

## webrtc/

### webrtc/signaling.py

Socket.IO signaling events for browser video rooms.

### webrtc/room_manager.py

Tracks WebRTC rooms/participants.

### webrtc/__init__.py

Package marker.

## Removed Files

These were removed because they are not needed for the hackathon submission:

- `.github/`
- `CODE_OF_CONDUCT.md`
- `CONTRIBUTING.md`
- `Security.md`
- `setup.py`
- `database/`
- `__pycache__/`

## What To Keep For Final Submission

Keep:

- `README.md`
- `PROMPTS.md`
- `technical-spec.md`
- `data/`
- `services/`
- `routes/`
- `templates/`
- `static/`
- `ai/`
- `webrtc/`
- `utils/`
- `models/`
- `requirements.txt`
- `app.py`
- `config.py`

Do not commit:

- `.env` if it contains real keys
- `venv/`
- generated audio files unless needed for demo screenshots
