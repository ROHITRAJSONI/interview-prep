"""Write a practice session to Markdown and commit it to a per-topic branch.

Branch naming: practice/<topic-id>, e.g. practice/kafka, practice/spring-boot.
Uses a temporary git worktree so your current checkout (daily-practice) is never switched.
"""

import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from .bank import Question
from .topics import Topic

REPO_ROOT = Path(__file__).resolve().parent.parent
SESSIONS_DIR = REPO_ROOT / "sessions"


def branch_for(topic: Topic) -> str:
    return f"practice/{topic.id}"


def render(topic: Topic, questions: list[Question], when: datetime) -> str:
    lines = [f"# {topic.name} — {when:%Y-%m-%d}", ""]
    for i, q in enumerate(questions, 1):
        lines.append(f"## Q{i}: {q.question}")
        if q.context:
            lines += ["", q.context]
        lines += ["", "<details><summary>Solution</summary>", "", q.solution, "", "</details>", ""]
        lines.append(f"<sub>source: {q.source}</sub>")
        lines.append("")
    return "\n".join(lines)


def save_session(topic: Topic, questions: list[Question]) -> Path:
    now = datetime.now()
    SESSIONS_DIR.mkdir(exist_ok=True)
    path = SESSIONS_DIR / topic.id / f"{now:%Y-%m-%d_%H%M%S}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(topic, questions, now), encoding="utf-8")
    return path


def _git(*args: str, cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=check, text=True, capture_output=True)


def _remote_branch_exists(branch: str) -> bool:
    r = _git("ls-remote", "--heads", "origin", branch, check=False)
    return r.returncode == 0 and bool(r.stdout.strip())


def publish(topic: Topic, session_file: Path, push: bool = True) -> str:
    """Commit session_file onto practice/<topic> and optionally push. Returns the branch name."""
    branch = branch_for(topic)
    rel = session_file.relative_to(REPO_ROOT)
    tmp = Path(tempfile.mkdtemp(prefix="prep-wt-"))
    try:
        if _remote_branch_exists(branch):
            _git("fetch", "--depth=1", "origin", f"{branch}:refs/remotes/origin/{branch}")
            _git("worktree", "add", "-B", branch, str(tmp), f"origin/{branch}")
        elif _git("rev-parse", "--verify", "--quiet", branch, check=False).returncode == 0:
            _git("worktree", "add", str(tmp), branch)
        else:
            # new topic branch starts from the current commit (the agent code on daily-practice)
            _git("worktree", "add", "-b", branch, str(tmp), "HEAD")

        dest = tmp / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(session_file, dest)
        _git("add", "-f", str(rel), cwd=tmp)  # sessions/ is git-ignored on daily-practice
        _git("commit", "-m", f"practice({topic.id}): {session_file.stem}", cwd=tmp)
        if push:
            _git("push", "-u", "origin", branch, cwd=tmp)
        return branch
    finally:
        _git("worktree", "remove", "--force", str(tmp), check=False)
        shutil.rmtree(tmp, ignore_errors=True)
