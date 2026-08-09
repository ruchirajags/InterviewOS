import re
from dataclasses import dataclass, field
from typing import Any

from services.candidate_analyzer import IMPORTANT_DAYS, analyze_candidate
from services.cohort_data import curriculum_day_map, module_for_day

QUESTION_BANK = {
    7: "In the RAG systems you built, what do embeddings actually represent, and how would you choose between two embedding models?",
    8: "Suppose your vector database returns semantically similar but irrelevant results. How would you tune search, indexing, and metadata filtering?",
    10: "Your RAG answer is wrong even though the retrieved chunks look related. How would you debug chunking, retrieval, reranking, and answer generation?",
    12: "How would you design a production prompt that must return valid JSON while reducing hallucination and ambiguity?",
    13: "When would you use structured outputs or function calling instead of plain text generation, and what failure cases would you guard against?",
    16: "You are exposing an AI workflow through an API. What validation, timeout, retry, and error-handling decisions would you make?",
    22: "When is a multi-agent design justified over one agent with tools, and how would you evaluate whether agent handoffs are working?",
    23: "Explain MCP as if you were designing a tool server for an AI assistant. What belongs in the tool schema, and where do permissions matter?",
    27: "What security and privacy risks appear in an enterprise AI assistant, and what guardrails would you implement first?",
    28: "How would you containerize and deploy an AI service so it remains reliable during model latency spikes?",
    29: "A production AI feature becomes slower and less accurate. What traces, metrics, and eval signals would you inspect first?",
    30: "How would you design fallback behavior for an AI system when the model provider is unavailable or quality regresses?",
    31: "Walk me through one system you built in the cohort. What were the key engineering tradeoffs and what would you improve next?",
}

KEYWORDS = {
    7: ["embedding", "vector", "semantic", "similarity", "dimension", "model"],
    8: ["index", "metadata", "filter", "cosine", "ann", "latency", "namespace"],
    10: ["chunk", "rerank", "recall", "precision", "query", "retrieval", "eval", "context"],
    12: ["schema", "json", "few-shot", "guardrail", "hallucination", "temperature", "prompt"],
    13: ["schema", "function", "tool", "validation", "json", "structured", "contract"],
    16: ["validation", "timeout", "retry", "async", "pydantic", "error", "rate limit", "fallback"],
    22: ["agent", "planner", "handoff", "tool", "role", "memory", "orchestration"],
    23: ["server", "client", "tool", "schema", "permission", "json-rpc", "resource"],
    27: ["privacy", "security", "guardrail", "pii", "prompt injection", "access", "policy"],
    28: ["docker", "container", "kubernetes", "deployment", "scaling", "health", "rollback"],
    29: ["trace", "metric", "cost", "latency", "eval", "monitor", "regression", "logging"],
    30: ["fallback", "deployment", "rollback", "cache", "queue", "reliability", "safety"],
    31: ["tradeoff", "architecture", "evaluation", "deployment", "improve", "system"],
}


@dataclass
class InterviewState:
    session_id: str
    candidate: dict[str, Any]
    analysis: dict[str, Any]
    plan: list[int]
    current_topic_index: int = 0
    question_count: int = 0
    topic_depth: int = 0
    transcript: list[dict[str, Any]] = field(default_factory=list)
    evaluations: list[dict[str, Any]] = field(default_factory=list)
    last_question: dict[str, Any] | None = None
    done: bool = False


class InterviewEngine:
    def __init__(self):
        self.sessions: dict[str, InterviewState] = {}
        self.day_map = curriculum_day_map()

    def start(self, session_id, candidate):
        analysis = analyze_candidate(candidate)
        plan = self._build_plan(analysis)
        state = InterviewState(session_id=session_id, candidate=candidate, analysis=analysis, plan=plan)
        self.sessions[session_id] = state
        reply = self._ask_question(state, opening=True)
        return {"reply": reply, "done": False, "state": self.public_state(state)}

    def turn(self, session_id, message):
            state = self.sessions.get(session_id)
            if not state:
                return {"error": "Unknown sessionId. Start the interview with a candidate object."}, 404
            if state.done:
                return {"reply": "Interview completed.", "done": True, "feedback": self._feedback(state)}

            quality = self._validate_answer_quality(message)
            if not quality["valid"]:
                current_question = state.last_question.get("question", "Please answer the previous question.")
                return {
                    "reply": (
                        "I couldn't understand that response clearly. "
                        "Please retry with a complete, grammatical answer.\n\n"
                        f"Question: {current_question}"
                    ),
                    "done": False,
                    "state": self.public_state(state),
                    "needs_retry": True,
                    "quality": quality,
            }

            self._record_answer(state, message)

            if self._should_complete(state):
                state.done = True
                return {
                    "reply": "Interview completed.",
                    "done": True,
                    "feedback": self._feedback(state),
                    "transcript": state.transcript,
                }

            evaluation = state.evaluations[-1]
            remaining_questions = max(0, 10 - state.question_count)
            remaining_topics = max(0, len(state.plan) - state.current_topic_index - 1)

            should_follow = (
                state.topic_depth < 2
                and remaining_questions > remaining_topics + 1
                and (evaluation["score"] <= 2 or evaluation["score"] >= 4)
            )

            if should_follow:
                reply = self._ask_question(state, followup=self._followup(evaluation))
            else:
                state.topic_depth = 0
                state.current_topic_index = min(state.current_topic_index + 1, len(state.plan) - 1)
                reply = self._ask_question(state)

            return {"reply": reply, "done": False, "state": self.public_state(state)}

    def public_state(self, state):
        candidate = state.candidate.get("member", {})
        return {
            "candidate": candidate,
            "analysis": state.analysis,
            "plan": [self._topic(day) for day in state.plan],
            "questionCount": state.question_count,
            "currentTopic": state.last_question,
            "coveredDays": sorted({item["day"] for item in state.transcript if item.get("day")}),
        }

    def _build_plan(self, analysis):
        completed = set(analysis["completed_days"])
        skipped = set(analysis["skipped_days"])
        probe = set(analysis["probe_days"])

        preferred_ai_order = [7, 8, 10, 12, 13, 16, 22, 23, 27, 28, 29, 30, 31]

        plan = []

        # 1. Add completed AI-core days in natural interview order.
        for day in preferred_ai_order:
            if day in completed and day not in skipped and day in self.day_map:
                plan.append(day)

        # 2. Add candidate-specific probe days not already included.
        for day in sorted(probe):
            if day in completed and day not in skipped and day in self.day_map and day not in plan:
                plan.append(day)

        # 3. Add any other completed candidate days.
        for day in sorted(completed):
            if day not in skipped and day in self.day_map and day not in plan:
                plan.append(day)

        # 4. If sparse candidate, add awareness-level important topics.
        if len(plan) < 8:
            for day in preferred_ai_order:
                if day not in skipped and day in self.day_map and day not in plan:
                    plan.append(day)

        return plan[:9] or [7, 8, 10, 12, 16, 22, 23, 29]

    def _topic(self, day):
        item = self.day_map.get(day, {})
        return {
            "day": day,
            "title": item.get("title", f"Day {day}"),
            "module": module_for_day(day),
            "objectives": item.get("objectives", [])[:3],
            "tools": item.get("tools", [])[:4],
        }

    def _ask_question(self, state, opening=False, followup=None):
        day = state.plan[min(state.current_topic_index, len(state.plan) - 1)]
        topic = self._topic(day)
        state.question_count += 1
        state.topic_depth += 1
        name = state.candidate.get("member", {}).get("name", "there")
        difficulty = state.analysis.get("difficulty", "intermediate")

        if followup:
            text = followup
        else:
            prefix = f"Welcome {name}. " if opening else ""
            level = "Let's move beyond definitions. " if difficulty == "advanced" else ""
            text = prefix + level + QUESTION_BANK.get(
                day,
                f"Explain the key engineering decisions behind {topic['title']}.",
            )

        state.last_question = {
            "number": state.question_count,
            "day": day,
            "topic": topic["title"],
            "module": topic["module"],
            "difficulty": difficulty,
            "question": text,
        }
        state.transcript.append({**state.last_question, "answer": ""})
        return text

    def _validate_answer_quality(self, answer):
        text = (answer or "").strip()
        lowered = text.lower()

        uncertainty_phrases = [
            "i don't know",
            "i dont know",
            "i am not sure",
            "i'm not sure",
            "not sure",
            "i have no idea",
            "no idea",
            "i am unsure",
            "i'm unsure",
            "will work on this",
            "will do some research",
            "will study on this topic better",
            "sorry"
        ]

        if any(phrase in lowered for phrase in uncertainty_phrases):
            return {"valid": True, "reason": "candidate expressed uncertainty"}

        words = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]*", lowered)
        unique_words = set(words)

        technical_terms = {
            "agent", "agents", "task", "tasks", "rag", "retrieval",
            "embedding", "embeddings", "vector", "database", "prompt",
            "api", "mcp", "tool", "tools", "model", "chunk", "chunks",
            "metadata", "deployment", "monitoring", "latency", "eval",
            "evaluation", "schema", "json", "fallback", "tradeoff",
            "tradeoffs", "system", "workflow", "automation"
        }

        if not text:
            reason = "empty answer"
        elif len(words) < 5:
            if any(word in technical_terms for word in words):
                return {"valid": True, "reason": "short technical answer"}
            reason = "too short to evaluate"

        elif len(unique_words) <= 2 and len(words) >= 5:
            reason = "mostly repeated words"
        elif re.search(r"(.)\1{5,}", lowered):
            reason = "repeated characters"
        elif len(re.sub(r"[^a-zA-Z]", "", text)) < max(8, len(text) * 0.35):
            reason = "not enough recognizable language"
        else:
            return {"valid": True, "reason": "answer is evaluable"}

        return {
            "valid": False,
            "reason": reason,
            "retry_prompt": "I couldn't understand that response clearly. Please retry with a complete, grammatical answer.",     
            }

    def _record_answer(self, state, answer):
        if state.transcript:
            state.transcript[-1]["answer"] = answer
        state.evaluations.append(self._evaluate(state.last_question["day"], answer))

    def _evaluate(self, day, answer):
        text = (answer or "").lower()
        hits = [kw for kw in KEYWORDS.get(day, []) if kw in text]
        length_bonus = 1 if len(text.split()) >= 35 else 0
        score = min(5, max(1, len(hits) // 2 + length_bonus + 1))
        understanding = "excellent" if score == 5 else "strong" if score >= 4 else "partial" if score >= 2 else "weak"
        missing = [kw for kw in KEYWORDS.get(day, []) if kw not in text][:3]

        return {
            "day": day,
            "score": score,
            "understanding": understanding,
            "strengths": hits[:3],
            "missing_concepts": missing,
        }

    def _should_complete(self, state: InterviewState) -> bool:
        answered = [item for item in state.transcript if item.get("answer")]
        covered_days = {item["day"] for item in answered if item.get("day")}

        minimum_days = min(8, len(state.plan))

        return len(answered) >= 10 and len(covered_days) >= minimum_days

    def _followup(self, evaluation):
        day = evaluation["day"]
        topic = self._topic(day)
        missing = evaluation["missing_concepts"][0] if evaluation["missing_concepts"] else "tradeoffs"

        if evaluation["score"] >= 4:
            return f"Good. Let's make {topic['title']} more production-focused: what failure mode would you expect, and what signal would prove your diagnosis?"
        if evaluation["score"] >= 2:
            return f"Let's stay with {topic['title']}. You touched part of it, but say more about {missing}: how would it affect your design decision?"
        return f"Let's ground this first. In {topic['title']}, what is the purpose of {missing}, and why does it matter in the system?"

    def _feedback(self, state):
        avg = sum(item["score"] for item in state.evaluations) / max(len(state.evaluations), 1)
        strong_days = sorted({item["day"] for item in state.evaluations if item["score"] >= 4})
        weak = [item for item in state.evaluations if item["score"] <= 2]

        strengths = [
            f"Strong reasoning in {self._topic(day)['title']}"
            for day in strong_days[:3]
        ] or ["Stayed engaged across multiple AI engineering topics"]

        gaps = [
            f"Review {self._topic(item['day'])['title']}, especially {', '.join(item['missing_concepts'][:2])}"
            for item in weak[:3]
        ] or ["Add more explicit metrics, tradeoffs, and production failure-mode analysis"]

        return {
            "summary": f"{state.candidate.get('member', {}).get('name', 'The candidate')} completed a {state.question_count}-question adaptive interview across {len(set(q['day'] for q in state.transcript))} curriculum days with an average answer score of {avg:.1f}/5.",
            "strengths": strengths,
            "gaps": gaps,
            "next": [
                "Prepare one end-to-end RAG architecture explanation from ingestion to monitoring",
                "Practice diagnosing weak answers with concrete metrics and traces",
                "Rehearse MCP, agents, and deployment tradeoffs using examples from the cohort",
            ],
        }


interview_engine = InterviewEngine()