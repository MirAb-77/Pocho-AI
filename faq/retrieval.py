"""
Retrieval layer: scores the user's question against every knowledge base
entry using TF-IDF cosine similarity, blended with a keyword-overlap score
against each entry's curated patterns. The blend matters because with a
small corpus, TF-IDF alone over- or under-weights generic shared words
(e.g. "campus" pulling unrelated questions toward campus_visit) and can
miss very short queries. Keyword overlap keeps the score anchored to the
specific phrases we know real applicants use.

The returned score is what drives the "FILE · <id> · NN% match" tag in
the UI, and decides whether we call the LLM (grounded) or fall back.
"""
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .knowledge_base import KNOWLEDGE_BASE

_STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "i", "my", "for", "to",
    "of", "in", "on", "at", "and", "or", "what", "when", "how", "can",
    "you", "your", "it", "this", "that", "please", "me", "will", "be",
}


def _keywords(text: str) -> set:
    words = re.findall(r"[a-z]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


# Build one search string per KB entry: question + patterns + category,
# so a user's phrasing has more surface area to match against.
_CORPUS = [
    " ".join([entry["question"], entry["category"], " ".join(entry["patterns"])])
    for entry in KNOWLEDGE_BASE
]
_ENTRY_KEYWORDS = [_keywords(text) for text in _CORPUS]

_VECTORIZER = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
_MATRIX = _VECTORIZER.fit_transform(_CORPUS)


def best_match(user_question: str):
    """
    Returns (entry: dict, score: float) for the closest KB entry to
    `user_question`, where score is a 0-1 blended confidence: the average
    of TF-IDF cosine similarity and keyword-overlap ratio (overlap /
    query keyword count) against that entry's question+patterns.
    """
    if not user_question or not user_question.strip():
        return None, 0.0

    query_vec = _VECTORIZER.transform([user_question])
    cosine_scores = cosine_similarity(query_vec, _MATRIX)[0]

    query_kw = _keywords(user_question)
    blended = []
    for i, cosine_score in enumerate(cosine_scores):
        if query_kw:
            overlap = len(query_kw & _ENTRY_KEYWORDS[i]) / len(query_kw)
        else:
            overlap = 0.0
        blended.append((float(cosine_score) + overlap) / 2)

    best_idx = max(range(len(blended)), key=lambda i: blended[i])
    return KNOWLEDGE_BASE[best_idx], blended[best_idx]
