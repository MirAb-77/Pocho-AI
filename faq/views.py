import json
from collections import OrderedDict

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .chitchat import local_chat_reply
from .grok_client import GrokError, generate_chat_reply, generate_grounded_answer
from .knowledge_base import CONFIDENCE_THRESHOLD, FALLBACK_MESSAGE, KNOWLEDGE_BASE
from .retrieval import best_match


def _categories():
    """Groups KNOWLEDGE_BASE by category, preserving first-seen order, for
    the sidebar's 'Browse by department' list on both pages."""
    grouped = OrderedDict()
    for entry in KNOWLEDGE_BASE:
        grouped.setdefault(entry["category"], []).append(entry)
    return grouped


def home(request):
    """Landing page: what this project is and how it works, before the visitor
    lands in the chat itself."""
    return render(
        request,
        "faq/home.html",
        {
            "categories": _categories(),
            "kb_count": len(KNOWLEDGE_BASE),
            "category_count": len(_categories()),
        },
    )


def index(request):
    """Renders the chat UI. Seeds it with the KB questions as suggestion chips."""
    suggestions = [entry["question"] for entry in KNOWLEDGE_BASE][:8]
    return render(
        request,
        "faq/index.html",
        {
            "suggestions": suggestions,
            "categories": _categories(),
        },
    )


@csrf_exempt
@require_POST
def ask(request):
    """
    POST {"question": "...", "history": [{"role": "user"|"assistant", "content": "..."}]} ->
    {
      "answer": str,
      "matched": bool,
      "source": {"id": str, "category": str, "score": float} | null,
      "generated_by": "grok" | "kb" | "chat" | "fallback"
    }

    Two branches:
      - A confident KB match -> grounded answer (Grok phrases the matched
        fact, or the raw fact if Grok is unavailable).
      - No confident match -> a conversational reply instead of a canned
        line, so greetings/thanks/"what can you do" feel like talking to
        an assistant rather than hitting a wall. The chat system prompt
        forbids inventing admissions facts, so if Grok is unavailable we
        still fall back to the static contact message.
    """
    try:
        body = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    question = (body.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "question is required."}, status=400)

    history = body.get("history") or []

    entry, score = best_match(question)

    if entry is not None and score >= CONFIDENCE_THRESHOLD:
        source = {"id": entry["id"], "category": entry["category"], "score": round(score * 100)}
        try:
            answer = generate_grounded_answer(question, entry["answer"], history)
            generated_by = "grok"
        except GrokError:
            answer = entry["answer"]
            generated_by = "kb"

        return JsonResponse(
            {
                "answer": answer,
                "matched": True,
                "source": source,
                "generated_by": generated_by,
            }
        )

    # No confident KB match -> try a natural, ungrounded conversational
    # reply before giving up. The system prompt keeps it from inventing
    # admissions facts; it should nudge unanswerable factual questions
    # toward the contact info itself.
    try:
        answer = generate_chat_reply(question, history)
        generated_by = "chat"
    except GrokError:
        # Grok unavailable -> try local, API-free small talk (greetings,
        # thanks, "who are you") before giving up entirely, so those still
        # work with no key configured. Genuine unanswerable questions
        # still land on the static fallback.
        local_reply = local_chat_reply(question)
        if local_reply is not None:
            answer = local_reply
            generated_by = "chat"
        else:
            answer = FALLBACK_MESSAGE
            generated_by = "fallback"

    return JsonResponse(
        {
            "answer": answer,
            "matched": False,
            "source": None,
            "generated_by": generated_by,
        }
    )
