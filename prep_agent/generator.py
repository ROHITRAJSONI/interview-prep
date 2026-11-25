"""Fresh question generation with the Claude API (optional).

Used when ANTHROPIC_API_KEY is set. Falls back to the curated bank on any failure.
"""

import json
import os
import re

from .bank import Question
from .topics import Topic

DEFAULT_MODEL = "claude-sonnet-5-5"

SYSTEM = """You are a senior Java/cloud interviewer at a large bank or fintech, hiring for a \
senior full-stack Java engineer (8-10 years experience). You write the questions that are MOST \
LIKELY to actually be asked in real interviews for the given topic: practical, scenario-based, \
the kind that separate senior engineers from mid-level ones. Avoid trivia and textbook definitions.

For each question give a model answer a strong candidate would say out loud: lead with the direct \
answer, then the reasoning, trade-offs and pitfalls, and a short code or config snippet when it \
helps. Keep each solution under ~250 words."""

PROMPT = """Topic: {topic}

Write {count} interview question(s) on this topic.
{avoid}
Return ONLY a JSON array, no prose, in this exact shape:
[{{"question": "...", "context": "optional one-line scenario or empty string", "solution": "markdown answer"}}]"""


def available() -> bool:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return False
    try:
        import anthropic  # noqa: F401
    except ImportError:
        return False
    return True


def generate(topic: Topic, count: int, already_asked: list[str]) -> list[Question]:
    import anthropic

    avoid = ""
    if already_asked:
        listed = "\n".join(f"- {t}" for t in already_asked[-40:])
        avoid = f"Do NOT repeat or closely rephrase any of these already-practised questions:\n{listed}\n"

    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.environ.get("PREP_MODEL", DEFAULT_MODEL),
        max_tokens=4000,
        system=SYSTEM,
        messages=[{"role": "user", "content": PROMPT.format(topic=topic.name, count=count, avoid=avoid)}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    items = _parse_json_array(text)
    out = []
    for it in items[:count]:
        q = str(it.get("question", "")).strip()
        s = str(it.get("solution", "")).strip()
        if q and s:
            out.append(Question(topic.id, q, s, str(it.get("context", "")).strip(), source="claude"))
    if not out:
        raise ValueError("model returned no usable questions")
    return out


def _parse_json_array(text: str) -> list[dict]:
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\[.*\])\s*```", text, re.S)
    if fenced:
        text = fenced.group(1)
    else:
        start, end = text.find("["), text.rfind("]")
        if start != -1 and end != -1:
            text = text[start : end + 1]
    data = json.loads(text)
    return [d for d in data if isinstance(d, dict)]
