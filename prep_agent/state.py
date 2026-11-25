"""Local state: the selected topic set, rotation position, and questions already seen.

Stored in .prep_state.json at the repo root (git-ignored), so each machine keeps its own.
"""

import json
from datetime import date
from pathlib import Path

from .topics import TOPICS

STATE_FILE = Path(__file__).resolve().parent.parent / ".prep_state.json"

DEFAULT_TOPICS = ["java", "spring-boot", "microservices", "multithreading", "kafka", "lambda", "dynamodb"]


class State:
    def __init__(self, data: dict):
        self.data = data
        self.data.setdefault("topics", list(DEFAULT_TOPICS))
        self.data.setdefault("rotation_index", 0)
        self.data.setdefault("seen", {})          # topic_id -> [question ids]
        self.data.setdefault("asked_titles", {})  # topic_id -> [question text], fed to the LLM to avoid repeats
        self.data.setdefault("last_run", None)
        self.data["topics"] = [t for t in self.data["topics"] if t in TOPICS] or list(DEFAULT_TOPICS)

    @classmethod
    def load(cls) -> "State":
        if STATE_FILE.exists():
            try:
                return cls(json.loads(STATE_FILE.read_text(encoding="utf-8")))
            except (json.JSONDecodeError, OSError):
                pass
        return cls({})

    def save(self) -> None:
        STATE_FILE.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    # --- topic set -------------------------------------------------------
    @property
    def topics(self) -> list[str]:
        return self.data["topics"]

    def set_topics(self, ids: list[str]) -> None:
        seen = []
        for i in ids:
            if i in TOPICS and i not in seen:
                seen.append(i)
        if seen:
            self.data["topics"] = seen
            self.data["rotation_index"] = 0
            self.data["last_run"] = None  # start the new rotation at its first topic

    def todays_topic(self) -> str:
        """Next topic in the rotation; advances once per calendar day."""
        today = date.today().isoformat()
        idx = self.data["rotation_index"] % len(self.topics)
        if self.data["last_run"] and self.data["last_run"] != today:
            idx = (idx + 1) % len(self.topics)
        return self.topics[idx]

    def mark_run(self, topic_id: str) -> None:
        if topic_id in self.topics:
            self.data["rotation_index"] = self.topics.index(topic_id)
        self.data["last_run"] = date.today().isoformat()

    # --- history ---------------------------------------------------------
    def seen_ids(self, topic_id: str) -> set[str]:
        return set(self.data["seen"].get(topic_id, []))

    def asked_titles(self, topic_id: str) -> list[str]:
        return self.data["asked_titles"].get(topic_id, [])

    def record(self, topic_id: str, qid: str, title: str) -> None:
        self.data["seen"].setdefault(topic_id, [])
        if qid not in self.data["seen"][topic_id]:
            self.data["seen"][topic_id].append(qid)
        titles = self.data["asked_titles"].setdefault(topic_id, [])
        if title not in titles:
            titles.append(title)
            del titles[:-60]  # keep the prompt bounded

    def reset_seen(self, topic_id: str) -> None:
        self.data["seen"][topic_id] = []
