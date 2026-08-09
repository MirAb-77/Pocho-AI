"""
Thin client for the Grok (xAI) chat completions API.

xAI exposes an OpenAI-compatible endpoint, so this is a plain requests POST.
Requires GROK_API_KEY in the environment (see README). If the key is
missing or the call fails, callers should fall back gracefully rather than
breaking the demo.

Two entry points:
  - generate_grounded_answer: phrase a KB fact as a natural answer. Used
    whenever retrieval finds a confident match — this is the only path
    allowed to state specific admissions facts (dates, fees, GPA, etc.),
    because it's the only one grounded in the knowledge base.
  - generate_chat_reply: everything else — greetings, thanks, "what can
    you do", follow-up chit-chat. No KB fact is passed in, so the system
    prompt explicitly forbids inventing admissions specifics; it should
    talk naturally but defer factual questions back to a direct question
    or the admissions contact.
"""
import os
import requests

GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = os.environ.get("GROK_MODEL", "grok-3-mini")

GROUNDED_SYSTEM_PROMPT = (
    "You are the admissions assistant for Meridian State University, a "
    "fictional university used for demo purposes. Answer the applicant's "
    "question using ONLY the fact below — do not add, invent, or assume "
    "any information that isn't in it. Keep your answer to 1-3 sentences, "
    "warm and professional, written as if replying directly to the "
    "applicant. Do not mention that you were given a 'fact' or 'context' — "
    "just answer naturally."
)

CHAT_SYSTEM_PROMPT = (
    "You are the admissions assistant for Meridian State University, a "
    "fictional university used for demo purposes. You're having a normal, "
    "friendly conversation with an applicant — greetings, thanks, small "
    "talk, or questions about what you can help with. Reply warmly and "
    "briefly (1-3 sentences), in your own voice, like a helpful person on "
    "the admissions team.\n\n"
    "CRITICAL: you have NOT been given any admissions facts for this reply "
    "(no dates, fees, GPA requirements, deadlines, document lists, etc). "
    "Never state or guess a specific admissions detail here — if the "
    "applicant asks something factual, say you'd want to check that "
    "against the official file and invite them to ask it directly (e.g. "
    "'When is the fall deadline?'), or point them to "
    "admissions@meridianstate.edu / +1 (555) 019-2028. It's fine to be "
    "conversational; it's not fine to invent a fact."
)


class GrokError(Exception):
    pass


def _sanitize_history(history):
    """Keep only well-formed {role, content} turns, capped to the last 8."""
    if not history:
        return []
    clean = []
    for turn in history[-8:]:
        if not isinstance(turn, dict):
            continue
        role = turn.get("role")
        content = turn.get("content")
        if role in ("user", "assistant") and isinstance(content, str) and content.strip():
            clean.append({"role": role, "content": content.strip()[:2000]})
    return clean


def _call_grok(system_prompt: str, user_content: str, history=None) -> str:
    api_key = os.environ.get("GROK_API_KEY")
    if not api_key:
        raise GrokError("GROK_API_KEY is not set in the environment.")

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(_sanitize_history(history))
    messages.append({"role": "user", "content": user_content})

    payload = {
        "model": GROK_MODEL,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 200,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(GROK_API_URL, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise GrokError(f"Grok API call failed: {exc}") from exc


def generate_grounded_answer(user_question: str, kb_fact: str, history=None) -> str:
    """
    Asks Grok to phrase `kb_fact` as a natural answer to `user_question`.
    Raises GrokError if the API key is missing or the request fails —
    callers should catch this and fall back to returning kb_fact directly.
    """
    user_content = f"Applicant's question: {user_question}\n\nFact: {kb_fact}"
    return _call_grok(GROUNDED_SYSTEM_PROMPT, user_content, history)


def generate_chat_reply(user_message: str, history=None) -> str:
    """
    Asks Grok for a natural, ungrounded conversational reply (greetings,
    thanks, "what can you help with", etc). Raises GrokError if the API
    key is missing or the request fails — callers should catch this and
    fall back to the static FALLBACK_MESSAGE.
    """
    return _call_grok(CHAT_SYSTEM_PROMPT, user_message, history)
