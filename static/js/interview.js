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

function initInterview() {
    roleValue = document.getElementById("metaRole")?.value || roleValue;
    candidateId = document.getElementById("metaCandidateId")?.value || "";
    sessionId = typeof roomId !== "undefined" ? roomId : crypto.randomUUID();
    document.getElementById("stopBtn").disabled = true;
    updateProgress();
}

async function fetchCandidate() {
    if (!candidateId) return { id: candidateId };
    const res = await fetch("/api/candidates");
    const data = await res.json();
    const found = data.candidates.find(c => c.member?.id === candidateId);
    return found || { id: candidateId };
}

async function startInterview() {
    if (interviewActive) return;
    interviewActive = true;
    document.getElementById("startBtn").disabled = true;
    document.getElementById("startBtn").textContent = "Interview in progress";
    document.getElementById("submitAnswerBtn").disabled = false;
    document.getElementById("recordBtn").disabled = false;
    showStatus("Creating personalized interview plan...", "info");
    setQuestionStatus("thinking");
    startCountdownTimer();

    candidatePayload = await fetchCandidate();
    const res = await fetch("/api/interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, candidate: candidatePayload })
    });
    const data = await res.json();
    handleInterviewResponse(data);
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
    if (questionHistory.length > 0) questionHistory[questionHistory.length - 1].answer = answerText;
    const answerDisplay = document.getElementById("answerDisplay");
    answerDisplay.textContent = `Your answer: "${answerText}"`;
    answerDisplay.style.display = "block";
    showStatus("Evaluating answer and deciding the next question...", "info");
    setQuestionStatus("thinking");

    const response = await fetch("/api/interview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, message: answerText })
    });
    const data = await response.json();
    handleInterviewResponse(data);
}

function handleInterviewResponse(data) {
    if (data.error) {
        showStatus(data.error, "error");
        setQuestionStatus("error");
        return;
    }

    if (data.needs_retry) {
    currentQuestion = sanitizeAiText(data.reply);
    document.getElementById("question").textContent = currentQuestion;
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
        document.getElementById("submitAnswerBtn").disabled = true;
        document.getElementById("recordBtn").disabled = true;
        document.getElementById("stopBtn").disabled = true;
        document.getElementById("question").textContent = data.reply || "Interview completed.";
        displayFeedback(data.feedback || {});
        showStatus("Interview complete. Your report is ready.", "success");
        return;
    }

    currentQuestion = sanitizeAiText(data.reply);
    questionCount = data.state?.questionCount || questionCount + 1;
    questionHistory.push({ question: currentQuestion, answer: "" });
    document.getElementById("question").textContent = currentQuestion;
    updateProgress(data.state);
    updateJourney(data.state);
    setQuestionStatus("waiting");
    showStatus("Your turn. Answer in text or use voice recording.", "info");
}

async function endInterview() {
    if (!interviewActive) {
        displayFeedback({ summary: "Interview ended before completion.", strengths: [], gaps: ["Complete the full adaptive interview for a stronger report."], next: ["Restart with a candidate profile and answer all questions."] });
        return;
    }
    while (questionCount < MAX_QUESTIONS) {
        await sendAnswer("I would approach this by checking the architecture, validating assumptions, comparing alternatives, and using concrete metrics to decide next steps.");
        if (!interviewActive) break;
    }
}

function displayFeedback(feedback) {
    const reportEl = document.getElementById("reportSection");
    const reportContent = document.getElementById("reportContent");
    reportEl.style.display = "block";
    const block = (title, items) => `<h4>${title}</h4><ul>${(items || []).map(item => `<li>${item}</li>`).join("")}</ul>`;
    reportContent.innerHTML = `
        <p>${feedback.summary || "Interview completed."}</p>
        ${block("Strengths", feedback.strengths)}
        ${block("Gaps", feedback.gaps)}
        ${block("Recommended Next Steps", feedback.next)}
    `;
    reportEl.scrollIntoView({ behavior: "smooth" });
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
    if (timerEl) timerEl.textContent = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function updateProgress(state) {
    const progressEl = document.getElementById("questionProgress");
    if (progressEl) progressEl.textContent = `Question ${questionCount} of ${MAX_QUESTIONS}`;
    const barEl = document.getElementById("progressBar");
    if (barEl) barEl.style.width = `${(questionCount / MAX_QUESTIONS) * 100}%`;
    const topic = state?.currentTopic;
    if (topic) document.getElementById("topicBadge").textContent = `${topic.topic} · Day ${topic.day}`;
}

function updateJourney(state) {
    const list = document.getElementById("journeyList");
    if (!list || !state?.plan) return;
    const currentDay = state.currentTopic?.day;
    const covered = new Set(state.coveredDays || []);
    list.innerHTML = state.plan.map(topic => {
        const cls = topic.day === currentDay ? "journey-item active" : covered.has(topic.day) ? "journey-item done" : "journey-item";
        return `<div class="${cls}"><span>Day ${topic.day}</span><strong>${topic.title}</strong></div>`;
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
        try { stopRecording(); } catch (e) { console.warn("Could not stop recording", e); }
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
    const labels = { thinking: "AI is thinking", waiting: "Waiting for answer", done: "Interview complete", error: "Error" };
    indicator.textContent = labels[state] || "Ready";
}

document.addEventListener("DOMContentLoaded", initInterview);
