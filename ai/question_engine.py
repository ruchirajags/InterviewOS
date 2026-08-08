import inspect

from sarvamai import SarvamAI
from config import Config
from utils.sanitization import sanitize_model_output


def get_client():
    return SarvamAI(api_subscription_key=Config.SARVAM_API_KEY)


def _chat_completions(client, **kwargs):
    signature = inspect.signature(client.chat.completions)
    if "model" in signature.parameters:
        return client.chat.completions(**kwargs)

    kwargs.pop("model", None)
    return client.chat.completions(**kwargs)


def generate_question(role, answer=None, question_history=None):
    client = get_client()

    history_text = ""
    if question_history:
        history_text = "\n\nPrevious Q&A:\n"
        for i, qa in enumerate(question_history, 1):
            history_text += f"Q{i}: {qa.get('question', '')}\nA{i}: {qa.get('answer', '')}\n"

    if answer:
        prompt = f"""You are a professional AI interviewer conducting a real-time video call interview.

Role being interviewed for: {role}
{history_text}
The candidate just answered: "{answer}"

Based on their answer, ask ONE insightful follow-up interview question. 
Be conversational, professional, and encouraging.
Never include hidden reasoning, analysis, or any XML-like tags such as <think> or </think>.
Return ONLY the question text, nothing else."""
    else:
        prompt = f"""You are a professional AI interviewer conducting a real-time video call interview.

Role being interviewed for: {role}

Start the interview with a warm greeting and ask your first interview question.
Be conversational and professional.
Never include hidden reasoning, analysis, or any XML-like tags such as <think> or </think>.
Return ONLY the greeting + question text, nothing else."""

    response = _chat_completions(
        client,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        top_p=1,
        max_tokens=250,
        model=Config.SARVAM_CHAT_MODEL,
    )

    return sanitize_model_output(response.choices[0].message.content)