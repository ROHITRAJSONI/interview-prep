"""Curated question bank, stored as readable Markdown under bank/<category>/<topic>.md.

File format:

    # Topic title
    ## Q: The question?
    Optional extra context for the question.
    ### Solution
    The answer, any Markdown or code.
    ## Q: Next question...
"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from .topics import Topic

BANK_DIR = Path(__file__).resolve().parent.parent / "bank"


@dataclass
class Question:
    topic_id: str
    question: str
    solution: str
    context: str = ""
    source: str = "bank"
    id: str = field(default="")

    def __post_init__(self):
        if not self.id:
            self.id = question_id(self.topic_id, self.question)


def question_id(topic_id: str, text: str) -> str:
    norm = " ".join(text.lower().split())
    return f"{topic_id}:{hashlib.sha1(norm.encode()).hexdigest()[:10]}"


def bank_file(topic: Topic) -> Path:
    return BANK_DIR / topic.category / f"{topic.id}.md"


def load(topic: Topic) -> list[Question]:
    path = bank_file(topic)
    if not path.exists():
        return []
    questions: list[Question] = []
    current_q: str | None = None
    context: list[str] = []
    solution: list[str] = []
    in_solution = False

    def flush():
        if current_q:
            questions.append(
                Question(
                    topic_id=topic.id,
                    question=current_q,
                    context="\n".join(context).strip(),
                    solution="\n".join(solution).strip(),
                )
            )

    in_code = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            in_code = not in_code
        if not in_code and line.startswith("## Q:"):
            flush()
            current_q = line[len("## Q:"):].strip()
            context, solution, in_solution = [], [], False
        elif not in_code and line.strip().lower() == "### solution":
            in_solution = True
        elif current_q is not None:
            (solution if in_solution else context).append(line)
    flush()
    return questions
