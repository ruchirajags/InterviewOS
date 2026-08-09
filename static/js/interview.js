let questionHistory = [];
let currentQuestion = "";
let questionCount = 0;
let interviewActive = false;
let interviewTimer = null;
let timeRemaining = 0;
let roleValue = "AI Cohort Graduate";
let candidateId = "";
let sessionId = "";
let candidatePayload = null;
let mediaMode = false;

const MAX_QUESTIONS = 10;
const DURATION_SECONDS = 1200;

function sanitizeAiText(text) {
    if (!text) return "";
    return String(text)
        .replace(/<think\b[^>]*>[\s\S]*?<\/think>/gi, "")
        .replace(/<analysis\b[^>]*>[\s\S]*?<\/analysis>/gi, "")
        .replace(/<reasoning\b[^>]*>[\s\S]*?<\/reasoning>/gi, "")
        .replace(/<\/?(think|analysis|reasoning)\b[^>]*>/gi, "")
        .replace(/\n{3,}/g, "\n\n")
        .trim();
}

function escapeHtml(text) {
    return String(text || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function initInterview() {
    roleValue = document.getElementById("metaRole")?.value || roleValue;
    candidateId = document.getElementById("metaCandidateId")?.value || "";
    sessionId = typeof roomId !== "undefined" ? roomId : crypto.randomUUID();

    const stopBtn = document.getElementById("stopBtn");
    if (stopBtn) stopBtn.disabled = true;

    updateProgress();
}

async function fetchCandidate() {
    if (candidatePayload) return candidatePayload;

    if (candidateId) {
        return { id: candidateId };
    }

    return { id: "" };
}

async function startInterview() {
    if (interviewActive) return;

    const currentCandidateId = document.getElementById("metaCandidateId")?.value?.trim();
    const currentSessionId = window.sessionId || (typeof roomId !== "undefined" && roomId ? roomId : sessionId);

    if (!currentCandidateId || !currentSessionId) {
        showStatus("Error: Missing Candidate ID or Session ID. Please select a candidate first.", "error");
        setQuestionStatus("error");
        return;
    }

    candidateId = currentCandidateId;
    sessionId = currentSessionId;
    candidatePayload = null;

    const modal = document.getElementById("permissionModal");
    if (modal) modal.style.display = "none";

    interviewActive = true;

    const startBtn = document.getElementById("startBtn");
    if (startBtn) {
        startBtn.disabled = true;
        startBtn.textContent = "Interview in progress";
    }

    const submitBtn = document.getElementById("submitAnswerBtn");
    const recordBtn = document.getElementById("recordBtn");

    if (submitBtn) submitBtn.disabled = false;
    if (recordBtn) recordBtn.disabled = false;

    showStatus("Creating personalized interview plan...", "info");
    setQuestionStatus("thinking");
    startCountdownTimer();

    try {
        candidatePayload = await fetchCandidate();

        const res = await fetch("/api/interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sessionId, candidate: candidatePayload })
        });

        const data = await res.json();
        console.log("Start interview response:", data);

        if (!res.ok) {
            throw new Error(data.error || "Could not start interview");
        }

        handleInterviewResponse(data);
    } catch (err) {
        console.error("Start interview failed:", err);
        interviewActive = false;
        clearInterval(interviewTimer);

        if (startBtn) {
            startBtn.disabled = false;
            startBtn.textContent = "Start Interview";
        }

        showStatus("Could not start interview: " + err.message, "error");
        setQuestionStatus("error");
    }
}

async function submitTypedAnswer() {
    const input = document.getElementById("typedAnswer");
    const answer = input.value.trim();

    if (!answer) {
        showStatus("Type an answer before submitting.", "warning");
        input.focus();
        return;
    }

    input.value = "";
    await sendAnswer(answer);
}

async function sendAnswer(answerText) {
    if (!interviewActive) return;

    if (questionHistory.length > 0) {
        questionHistory[questionHistory.length - 1].answer = answerText;
    }

    const answerDisplay = document.getElementById("answerDisplay");
    if (answerDisplay) {
        answerDisplay.classList.remove("answer-display-muted");
        answerDisplay.innerHTML = `
            <span class="submitted-label">Last submitted answer</span>
            <p>${escapeHtml(answerText)}</p>
        `;
        answerDisplay.style.display = "block";
    }

    showStatus("Evaluating answer and deciding the next question...", "info");
    setQuestionStatus("thinking");

    try {
        const response = await fetch("/api/interview", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ sessionId, message: answerText })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Could not evaluate answer");
        }

        handleInterviewResponse(data);
    } catch (err) {
        console.error("Answer submission failed:", err);
        showStatus("Could not evaluate answer: " + err.message, "error");
        setQuestionStatus("error");

        const input = document.getElementById("typedAnswer");
        if (input) {
            input.value = answerText;
            input.focus();
        }
    }
}

function handleInterviewResponse(data) {
    if (data.error) {
        showStatus(data.error, "error");
        setQuestionStatus("error");
        return;
    }

    if (data.needs_retry) {
        currentQuestion = sanitizeAiText(data.reply);

        const questionEl = document.getElementById("question");
        if (questionEl) {
            questionEl.innerHTML = "";

            const parts = currentQuestion.split("Question:");

            const msg = document.createElement("div");
            msg.textContent = parts[0].trim();

            const spacer = document.createElement("div");
            spacer.style.height = "14px";

            const q = document.createElement("div");
            q.textContent = parts.length > 1
                ? "Question:" + parts.slice(1).join("Question:").trim()
                : "";

            questionEl.appendChild(msg);
            questionEl.appendChild(spacer);
            questionEl.appendChild(q);
        }

        updateProgress(data.state);
        updateJourney(data.state);
        setQuestionStatus("waiting");

        const input = document.getElementById("typedAnswer");
        if (input) input.focus();

        showStatus(`Please retry: ${data.quality?.reason || "answer was unclear"}.`, "warning");
        return;
    }

    if (data.done) {
        interviewActive = false;
        clearInterval(interviewTimer);

        setQuestionStatus("done");

        const submitBtn = document.getElementById("submitAnswerBtn");
        const recordBtn = document.getElementById("recordBtn");
        const stopBtn = document.getElementById("stopBtn");
        const questionEl = document.getElementById("question");

        if (submitBtn) submitBtn.disabled = true;
        if (recordBtn) recordBtn.disabled = true;
        if (stopBtn) stopBtn.disabled = true;
        if (questionEl) questionEl.textContent = data.reply || "Interview completed.";

        displayFeedback(data.feedback || {});
        showStatus("Interview complete. Your report is ready.", "success");
        return;
    }

    currentQuestion = sanitizeAiText(data.reply);
    questionCount = data.state?.questionCount || questionCount + 1;
    questionHistory.push({ question: currentQuestion, answer: "" });

    const questionEl = document.getElementById("question");
    if (questionEl) questionEl.textContent = currentQuestion;

    const answerDisplay = document.getElementById("answerDisplay");
    if (answerDisplay) {
        answerDisplay.classList.add("answer-display-muted");
    }

    updateProgress(data.state);
    updateJourney(data.state);
    setQuestionStatus("waiting");
    showStatus("Your turn. Answer in text or use voice recording.", "info");
}

async function endInterview() {
    interviewActive = false;
    clearInterval(interviewTimer);

    setQuestionStatus("done");

    const submitBtn = document.getElementById("submitAnswerBtn");
    const recordBtn = document.getElementById("recordBtn");
    const stopBtn = document.getElementById("stopBtn");
    const startBtn = document.getElementById("startBtn");

    if (submitBtn) submitBtn.disabled = true;
    if (recordBtn) recordBtn.disabled = true;
    if (stopBtn) stopBtn.disabled = true;

    if (startBtn) {
        startBtn.disabled = true;
        startBtn.textContent = "Interview ended";
    }

    displayFeedback({
        summary: "Interview ended before completion. Complete the full adaptive interview to generate a scored readiness report.",
        strengths: questionHistory.length
            ? ["Started the interview and engaged with the technical prompts."]
            : ["No evaluated answers were submitted."],
        gaps: ["The interview was ended before enough evidence was collected."],
        next: ["Restart the interview and answer all questions to receive a complete report."]
    });

    showStatus("Interview ended. No additional answers were generated.", "warning");
}

function displayFeedback(feedback) {
    const reportEl = document.getElementById("reportSection");
    const reportContent = document.getElementById("reportContent");

    if (!reportEl || !reportContent) return;

    reportEl.style.display = "block";

    const block = (title, items) => `
        <h4>${escapeHtml(title)}</h4>
        <ul>${(items || []).map(item => `<li>${escapeHtml(item)}</li>`).join("")}</ul>
    `;

    reportContent.innerHTML = `
        <p>${escapeHtml(feedback.summary || "Interview completed.")}</p>
        ${block("Strengths", feedback.strengths)}
        ${block("Gaps", feedback.gaps)}
        ${block("Recommended Next Steps", feedback.next)}
    `;

    reportEl.scrollIntoView({ behavior: "smooth", block: "start" });
}

function startCountdownTimer() {
    timeRemaining = DURATION_SECONDS;
    updateTimerDisplay();

    interviewTimer = setInterval(() => {
        timeRemaining--;
        updateTimerDisplay();

        if (timeRemaining <= 0) {
            clearInterval(interviewTimer);
            endInterview();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const mins = Math.floor(timeRemaining / 60);
    const secs = timeRemaining % 60;
    const timerEl = document.getElementById("timer");

    if (timerEl) {
        timerEl.textContent = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }
}

function updateProgress(state) {
    const progressEl = document.getElementById("questionProgress");
    const barEl = document.getElementById("progressBar");
    const topic = state?.currentTopic;

    if (progressEl) progressEl.textContent = `Question ${questionCount} of ${MAX_QUESTIONS}`;
    if (barEl) barEl.style.width = `${(questionCount / MAX_QUESTIONS) * 100}%`;

    if (topic) {
        const topicBadge = document.getElementById("topicBadge");
        if (topicBadge) topicBadge.textContent = `${topic.topic} · Day ${topic.day}`;
    }
}

function updateJourney(state) {
    const list = document.getElementById("journeyList");
    if (!list || !state?.plan) return;

    const currentDay = state.currentTopic?.day;
    const covered = new Set(state.coveredDays || []);

    list.innerHTML = state.plan.map(topic => {
        const cls = topic.day === currentDay
            ? "journey-item active"
            : covered.has(topic.day)
                ? "journey-item done"
                : "journey-item";

        return `<div class="${cls}"><span>Day ${topic.day}</span><strong>${escapeHtml(topic.title)}</strong></div>`;
    }).join("");
}

function setMediaMode(enabled) {
    mediaMode = Boolean(enabled);

    const recordBtn = document.getElementById("recordBtn");
    const stopBtn = document.getElementById("stopBtn");
    const textOnlyBtn = document.getElementById("textOnlyBtn");

    if (recordBtn) recordBtn.style.display = mediaMode ? "inline-flex" : "none";
    if (stopBtn) stopBtn.style.display = mediaMode ? "inline-flex" : "none";
    if (textOnlyBtn) textOnlyBtn.textContent = mediaMode ? "Text Only" : "Text Mode Active";
}

function switchToTextOnly(showMessage = true) {
    if (typeof stopRecording === "function" && typeof isRecording !== "undefined" && isRecording) {
        try {
            stopRecording();
        } catch (e) {
            console.warn("Could not stop recording", e);
        }
    }

    if (typeof stopMedia === "function") stopMedia();

    const localVideo = document.getElementById("localVideo");
    const remoteVideo = document.getElementById("remoteVideo");

    if (localVideo) localVideo.srcObject = null;
    if (remoteVideo) remoteVideo.srcObject = null;

    setMediaMode(false);

    const submitBtn = document.getElementById("submitAnswerBtn");
    if (submitBtn) submitBtn.disabled = !interviewActive;

    if (showMessage) {
        showStatus("Text-only mode enabled. You can continue the same interview by typing answers.", "success");
    }
}

function enableMediaMode() {
    setMediaMode(true);

    const recordBtn = document.getElementById("recordBtn");
    if (recordBtn) recordBtn.disabled = !interviewActive;
}

function setQuestionStatus(state) {
    const indicator = document.getElementById("aiIndicator");
    if (!indicator) return;

    indicator.className = `ai-indicator ai-${state}`;

    const labels = {
        thinking: "AI is thinking",
        waiting: "Waiting for answer",
        done: "Interview complete",
        error: "Error"
    };

    indicator.textContent = labels[state] || "Ready";
}

document.addEventListener("DOMContentLoaded", initInterview);