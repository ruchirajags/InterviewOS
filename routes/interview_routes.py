from flask import Blueprint, request, jsonify, render_template, Response
from models.interview import create_interview, save_answers, get_interview, save_report
from services.candidate_analyzer import candidate_summary
from services.cohort_data import curriculum_day_map, find_candidate, load_candidates
from services.interview_engine import interview_engine
from utils.validation import CohortInterviewRequest, CreateInterviewRequest, SaveAnswersRequest
from pydantic import ValidationError
import uuid
import re
import json

interview_bp = Blueprint("interview", __name__)

def validate_room_id(room_id):
    if not room_id or not re.match(r"^[A-Z0-9-]{1,80}$", room_id, re.I):
        return False
    return True

@interview_bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@interview_bp.route("/interview/create", methods=["GET"])
def create_page():
    return render_template("create_interview.html")

@interview_bp.route("/interview/<room_id>")
def room_page(room_id):
    if not validate_room_id(room_id):
        return render_template("index.html")
    interview = get_interview(room_id)
    if not interview:
        return render_template("index.html")
    return render_template("interview_room.html", room_id=room_id, interview=dict(interview))

@interview_bp.route("/api/candidates", methods=["GET"])
def candidates():
    day_map = curriculum_day_map()
    payload = []
    for candidate in load_candidates():
        member = candidate.get("member", {})
        summary = candidate_summary(candidate, day_map)
        payload.append({**candidate, "summary": summary, "member": member})
    return jsonify({"candidates": payload})

@interview_bp.route("/api/interview", methods=["POST"])
def cohort_interview():
    try:
        data = CohortInterviewRequest(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400

    if data.candidate:
        candidate = data.candidate
        if candidate.get("id"):
            found = find_candidate(candidate["id"])
            if found:
                candidate = found
        result = interview_engine.start(data.sessionId, candidate)
        return jsonify({"reply": result["reply"], "done": False, "state": result["state"]})

    if not data.message:
        return jsonify({"error": "message is required for conversation turns"}), 400

    result = interview_engine.turn(data.sessionId, data.message)
    if isinstance(result, tuple):
        body, status = result
        return jsonify(body), status

    if result.get("done"):
        state = interview_engine.sessions.get(data.sessionId)
        if state:
            save_report(data.sessionId, json.dumps(result.get("feedback", {})), json.dumps(state.transcript))
    return jsonify(result)

@interview_bp.route("/api/interview/create", methods=["POST"])
def create():
    try:
        data = CreateInterviewRequest(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400

    room_id = data.room_id or str(uuid.uuid4())[:8].upper()
    role = data.role
    candidate_name = data.candidate_name
    try:
        create_interview(room_id, role, candidate_name, data.candidate_id)
        return jsonify({"status": "created", "room_id": room_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@interview_bp.route("/api/interview/<room_id>", methods=["GET"])
def get(room_id):
    if not validate_room_id(room_id):
        return jsonify({"error": "Invalid room ID"}), 400
    interview = get_interview(room_id)
    if interview:
        return jsonify(dict(interview))
    return jsonify({"error": "Interview not found"}), 404

@interview_bp.route("/api/interview/<room_id>/answers", methods=["POST"])
def save(room_id):
    if not validate_room_id(room_id):
        return jsonify({"error": "Invalid room ID"}), 400
    try:
        data = SaveAnswersRequest(**request.get_json())
    except (ValidationError, TypeError) as e:
        return jsonify({"error": "Invalid input", "details": str(e)}), 400
    try:
        save_answers(room_id, data.answers)
        return jsonify({"status": "answers_saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@interview_bp.route("/api/interview/<room_id>/report/download", methods=["GET"])
def download_report(room_id):
    interview = get_interview(room_id)
    if not interview or not interview["report"]:
        return jsonify({"error": "Report not found"}), 404
    try:
        feedback = json.loads(interview["report"])
    except Exception:
        feedback = {"summary": interview["report"], "strengths": [], "gaps": [], "next": []}
    lines = [
        "AI Engineering Readiness Report",
        f"Candidate: {interview['candidate_name']}",
        f"Session: {room_id}",
        "",
        "Summary:", feedback.get("summary", ""),
        "",
        "Strengths:", *[f"- {item}" for item in feedback.get("strengths", [])],
        "",
        "Gaps:", *[f"- {item}" for item in feedback.get("gaps", [])],
        "",
        "Next Steps:", *[f"- {item}" for item in feedback.get("next", [])],
    ]
    content = "\n".join(lines)
    return Response(content, mimetype="text/plain", headers={"Content-Disposition": f"attachment; filename={room_id}-readiness-report.txt"})
