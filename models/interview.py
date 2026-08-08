# In-memory interview room store for the hackathon demo.
# The technical specification does not require persistent accounts or long-term history.

from datetime import datetime

INTERVIEWS = {}


def init_db():
    # Kept as a no-op so older imports do not break.
    return None


def create_interview(room_id, role, candidate_name, candidate_id=None):
    INTERVIEWS[room_id] = {
        "room_id": room_id,
        "role": role,
        "candidate_name": candidate_name,
        "candidate_id": candidate_id,
        "answers": None,
        "qa_history": None,
        "report": None,
        "status": "active",
        "created_at": datetime.utcnow().isoformat(timespec="seconds"),
        "ended_at": None,
    }


def ensure_interview(room_id, role="AI Cohort Interview", candidate_name="Candidate", candidate_id=None):
    if room_id not in INTERVIEWS:
        create_interview(room_id, role, candidate_name, candidate_id)


def save_answers(room_id, answers):
    ensure_interview(room_id)
    INTERVIEWS[room_id]["answers"] = answers


def save_report(room_id, report, qa_history=None):
    ensure_interview(room_id)
    INTERVIEWS[room_id]["report"] = report
    INTERVIEWS[room_id]["qa_history"] = qa_history
    INTERVIEWS[room_id]["status"] = "completed"
    INTERVIEWS[room_id]["ended_at"] = datetime.utcnow().isoformat(timespec="seconds")


def end_interview(room_id):
    ensure_interview(room_id)
    INTERVIEWS[room_id]["status"] = "ended"
    INTERVIEWS[room_id]["ended_at"] = datetime.utcnow().isoformat(timespec="seconds")


def get_interview(room_id):
    return INTERVIEWS.get(room_id)
