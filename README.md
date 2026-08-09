# AI Admissions FAQ Assistant (Prototype)

A retrieval-augmented FAQ assistant for a fictional university's admissions
office, built with Django and grounded generation via the Grok (xAI) API.

## How it works

1. **Retrieval** (`faq/retrieval.py`) — the user's question is scored against
   every knowledge base entry using a blend of TF-IDF cosine similarity and
   keyword overlap against each entry's curated paraphrases. This blend
   fixes two failure modes a pure TF-IDF match has on a small corpus: shared
   filler words (like "campus") over-matching unrelated questions, and very
   short queries under-matching. The blended score becomes the confidence
   used in the UI ("FILE · `entry_id` · NN% match").
2. **Grounded generation** (`faq/grok_client.py`) — if the best match clears
   `CONFIDENCE_THRESHOLD` (0.5), the matched KB entry's raw fact is sent to
   Grok with a strict system prompt: *phrase this fact naturally, don't add
   anything not in it*. This is what makes the reply read like a real
   answer instead of a canned string, while keeping it grounded (no
   hallucinated facts) — a proper RAG pattern rather than either a bare
   lookup table or an ungrounded LLM.
3. **Fallback** — if no entry clears the threshold, the LLM is never called;
   the user is shown a "not on file" message with the admissions contact
   email/phone. If the LLM *is* called but the API key is missing or the
   request fails, the app falls back gracefully to returning the raw KB
   answer text, so the demo still works without a configured key.

## Knowledge base structure

`faq/knowledge_base.py` holds `KNOWLEDGE_BASE`, a flat list of 19 entries
covering Deadlines, Fees, Requirements, Financial Aid, Campus Life,
Academics, Process, and Contact. Each entry:

```python
{
    "id": "fall_deadline",              # stable slug, shown in the match tag
    "category": "Deadlines",
    "question": "When is the fall application deadline?",
    "patterns": [...],                   # paraphrases used only for matching
    "answer": "The Fall semester application deadline is March 15. ...",
}
```

All data (dates, fees, GPA, contact info) is placeholder/fictional for
"Meridian State University."

## Running it

```bash
cd admissions_faq
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`.

### Enabling Grok (optional but recommended)

Without a key, the assistant still works — it just returns the raw KB
answer text instead of an LLM-phrased one (`generated_by: "kb"` in the API
response, visible in the match tag).

```bash
export GROK_API_KEY="your-xai-api-key"
export GROK_MODEL="grok-3-mini"   # optional, defaults to grok-3-mini
```

Get a key from https://console.x.ai. Never commit it — use an environment
variable or a `.env` file excluded from version control.

## Testing

All 19 KB questions (plus paraphrased variants) were run against `/ask/`
and correctly matched their intended entry; out-of-scope questions (e.g.
"can I bring my dog to campus", "what's the weather like") correctly fell
back to the contact-admissions message rather than being force-matched.

## API

`POST /ask/` — body `{"question": "..."}`, returns:

```json
{
  "answer": "The Fall semester application deadline is March 15.",
  "matched": true,
  "source": {"id": "fall_deadline", "category": "Deadlines", "score": 78},
  "generated_by": "grok"
}
```

`generated_by` is one of `"grok"` (LLM-phrased), `"kb"` (raw KB text, LLM
unavailable/unconfigured), or `"fallback"` (no confident match).

## Project structure

```
admissions_faq/
├── admissions_faq/        # Django project (settings, urls)
├── faq/
│   ├── knowledge_base.py  # the FAQ data + confidence threshold
│   ├── retrieval.py       # TF-IDF + keyword-overlap matching
│   ├── grok_client.py     # xAI Grok API client
│   ├── views.py           # index + ask endpoints
│   ├── urls.py
│   └── templates/faq/index.html   # chat UI (navy/cream/gold theme)
├── requirements.txt
└── README.md
```

## Possible next steps

- Swap the in-memory KB list for a database model + admin CRUD.
- Add conversation memory (multi-turn context) to Grok calls.
- Log unmatched questions to identify KB gaps.
- Add real analytics on match confidence distribution.
