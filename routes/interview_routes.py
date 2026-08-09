from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, Response
from models.interview import (
    create_interview,
    save_answers,
    get_interview,
    save_report,
)
from services.candidate_analyzer import candidate_summary
from services.cohort_data import (
    curriculum_day_map,
    find_candidate,
    load_candidates,
)
from services.interview_engine import interview_engine
from utils.validation import (
    CohortInterviewRequest,
    CreateInterviewRequest,
    SaveAnswersRequest,
)
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

    return render_template(
        "interview_room.html",
        room_id=room_id,
        interview=dict(interview),
    )


@interview_bp.route("/api/candidates", methods=["GET"])
def candidates():
    day_map = curriculum_day_map()
    payload = []

    for candidate in load_candidates():
        member = candidate.get("member", {})
        summary = candidate_summary(candidate, day_map)

        payload.append({
            **candidate,
            "summary": summary,
            "member": member,
        })

    return jsonify({"candidates": payload})


@interview_bp.route("/api/interview", methods=["POST"])
def cohort_interview():
    try:
        data = CohortInterviewRequest(**request.get_json())

    except (ValidationError, TypeError) as e:
        return jsonify({
            "error": "Invalid input",
            "details": str(e),
            "received": request.get_json(),
        }), 400

    # Start a new adaptive interview
    if data.candidate:
        candidate = data.candidate

        if candidate.get("id"):
            found = find_candidate(candidate["id"])

            if found:
                candidate = found

        result = interview_engine.start(
            data.sessionId,
            candidate,
        )

        return jsonify({
            "reply": result["reply"],
            "done": False,
            "state": result["state"],
        })

    # Continue an existing interview
    if not data.message:
        return jsonify({
            "error": "message is required for conversation turns"
        }), 400

    result = interview_engine.turn(
        data.sessionId,
        data.message,
    )

    if isinstance(result, tuple):
        body, status = result
        return jsonify(body), status

    # Save report when interview is complete
    if result.get("done"):
        state = interview_engine.sessions.get(data.sessionId)

        if state:
            qa_history = []
            for index, item in enumerate(state.transcript):
                enriched = dict(item)
                if index < len(state.evaluations):
                    enriched["evaluation"] = state.evaluations[index]
                qa_history.append(enriched)

            save_report(
                data.sessionId,
                json.dumps(result.get("feedback", {})),
                json.dumps(qa_history),
            )

    return jsonify(result)


@interview_bp.route("/api/interview/create", methods=["POST"])
def create():
    try:
        data = CreateInterviewRequest(**request.get_json())

    except (ValidationError, TypeError) as e:
        return jsonify({
            "error": "Invalid input",
            "details": str(e),
        }), 400

    room_id = data.room_id or str(uuid.uuid4())[:8].upper()
    role = data.role
    candidate_name = data.candidate_name

    try:
        create_interview(
            room_id,
            role,
            candidate_name,
            data.candidate_id,
        )

        return jsonify({
            "status": "created",
            "room_id": room_id,
        })

    except Exception as e:
        return jsonify({
            "error": str(e),
        }), 500


@interview_bp.route("/api/interview/<room_id>", methods=["GET"])
def get(room_id):
    if not validate_room_id(room_id):
        return jsonify({
            "error": "Invalid room ID"
        }), 400

    interview = get_interview(room_id)

    if interview:
        return jsonify(dict(interview))

    return jsonify({
        "error": "Interview not found"
    }), 404


@interview_bp.route("/api/interview/<room_id>/answers", methods=["POST"])
def save(room_id):
    if not validate_room_id(room_id):
        return jsonify({
            "error": "Invalid room ID"
        }), 400

    try:
        data = SaveAnswersRequest(**request.get_json())

    except (ValidationError, TypeError) as e:
        return jsonify({
            "error": "Invalid input",
            "details": str(e),
        }), 400

    try:
        save_answers(room_id, data.answers)

        return jsonify({
            "status": "answers_saved"
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

@interview_bp.route(
    "/api/interview/<room_id>/report/download",
    methods=["GET"],
)
def download_report(room_id):
    interview = get_interview(room_id)

    if not interview or not interview["report"]:
        return jsonify({
            "error": "Report not found"
        }), 404

    try:
        feedback = json.loads(interview["report"])
    except Exception:
        feedback = {
            "summary": interview["report"],
            "strengths": [],
            "gaps": [],
            "next": [],
        }

    try:
        transcript = json.loads(interview.get("qa_history") or "[]")
    except Exception:
        transcript = []

    question_analysis = []
    total_score = 0
    scored_count = 0

    for item in transcript:
        evaluation = item.get("evaluation", {})
        score = evaluation.get("score", "N/A")

        if isinstance(score, (int, float)):
            total_score += score
            scored_count += 1

        missing = evaluation.get("missing_concepts", [])
        if isinstance(missing, list):
            missing = ", ".join(missing) if missing else "No major missing concepts detected."

        question_analysis.append({
            "day": item.get("day", "N/A"),
            "topic": item.get("topic", "Topic"),
            "module": item.get("module", "AI Cohort"),
            "question": item.get("question", ""),
            "answer": item.get("answer", ""),
            "score": score,
            "expected_direction": evaluation.get(
                "expected_direction",
                "Explain the concept, tradeoffs, and production implications."
            ),
            "missing_concepts": missing or "No major missing concepts detected.",
        })

    questions_answered = len([item for item in transcript if item.get("answer")])
    covered_days = sorted({str(item.get("day")) for item in transcript if item.get("day")})

    overall_score = (
        f"{total_score / scored_count:.1f}/5"
        if scored_count
        else "See summary"
    )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-InterviewOS-readiness-report.html"

    html = render_template(
        "report_download.html",
        filename=filename,
        candidate_name=interview.get("candidate_name") or "Candidate",
        role=interview.get("role") or "AI Cohort Interview",
        session_id=room_id,
        questions_answered=questions_answered,
        days_covered=", ".join(covered_days) if covered_days else "N/A",
        overall_score=overall_score,
        generated_at=generated_at,
        feedback=feedback,
        question_analysis=question_analysis,
    )

    return Response(
        html,
        mimetype="text/html",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        },
    )