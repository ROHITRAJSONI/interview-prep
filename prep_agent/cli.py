"""Interactive interview-practice agent.

    python -m prep_agent                 # daily run: confirm/change topic, practise 3 questions
    python -m prep_agent --topic kafka   # skip the prompt
    python -m prep_agent --topics        # change your rotating topic set
    python -m prep_agent --list          # show all topics
"""

import argparse
import random
import subprocess
import sys

from . import bank, generator, publisher
from .bank import Question
from .state import State
from .topics import CATEGORIES, TOPICS, Topic, by_category, resolve

BOLD, DIM, CYAN, GREEN, YELLOW, RESET = "\033[1m", "\033[2m", "\033[36m", "\033[32m", "\033[33m", "\033[0m"
if not sys.stdout.isatty():
    BOLD = DIM = CYAN = GREEN = YELLOW = RESET = ""


def ask(prompt: str, default: str = "") -> str:
    try:
        ans = input(prompt).strip()
    except EOFError:
        ans = ""
    return ans or default


# --- topic handling ---------------------------------------------------------

def print_catalog(selected: list[str] | None = None) -> None:
    n = 0
    for cat, topics in by_category().items():
        print(f"\n{BOLD}{CATEGORIES[cat]}{RESET}  {DIM}({cat}){RESET}")
        for t in topics:
            n += 1
            mark = f"{GREEN}●{RESET}" if selected and t.id in selected else " "
            print(f"  {mark} {n:>2}. {t.name:<38} {DIM}{t.id}{RESET}")
    print()


def parse_selection(text: str) -> list[Topic]:
    out: list[Topic] = []
    for token in text.replace(";", ",").split(","):
        for t in resolve(token):
            if t not in out:
                out.append(t)
    return out


def choose_topic_set(state: State) -> None:
    print_catalog(state.topics)
    print("Enter topic numbers, ids or category names, comma-separated.")
    print(f"{DIM}e.g.  1,2,kafka,multithreading   or   aws   or   all{RESET}")
    picked = parse_selection(ask("Topic set (Enter to keep current): "))
    if picked:
        state.set_topics([t.id for t in picked])
        print(f"{GREEN}Topic set saved:{RESET} " + ", ".join(TOPICS[t].name for t in state.topics))


def choose_session_topic(state: State) -> Topic:
    suggested = TOPICS[state.todays_topic()]
    print(f"\n{BOLD}Today's topic:{RESET} {CYAN}{suggested.name}{RESET}")
    print(f"{DIM}Your rotation: {', '.join(TOPICS[t].name for t in state.topics)}{RESET}")
    ans = ask("[Enter] go  ·  [c] pick a different topic  ·  [s] change the rotation set  > ").lower()
    if ans == "s":
        choose_topic_set(state)
        return TOPICS[state.todays_topic()]
    if ans == "c":
        print_catalog(state.topics)
        while True:
            picked = parse_selection(ask("Topic for this session (number, id or name): "))
            if len(picked) == 1:
                return picked[0]
            if picked:
                print(f"{YELLOW}That matched several: {', '.join(t.id for t in picked)}. Be more specific.{RESET}")
            else:
                print(f"{YELLOW}No match, try again.{RESET}")
    return suggested


# --- question selection -----------------------------------------------------

def from_bank(state: State, topic: Topic, count: int) -> list[Question]:
    pool = bank.load(topic)
    if not pool:
        return []
    seen = state.seen_ids(topic.id)
    unseen = [q for q in pool if q.id not in seen]
    picked = random.sample(unseen, min(count, len(unseen)))
    if len(picked) < count:
        # bank exhausted for this topic: start a new cycle, topping up with older questions
        print(f"{DIM}(You've been through the {topic.name} bank, so some older questions are mixed in.){RESET}")
        state.reset_seen(topic.id)
        rest = [q for q in pool if q not in picked]
        picked += random.sample(rest, min(count - len(picked), len(rest)))
    return picked


def pick_questions(state: State, topic: Topic, count: int, source: str) -> list[Question]:
    use_api = source == "api" or (source == "auto" and generator.available())
    if use_api:
        if not generator.available():
            print(f"{YELLOW}Claude API not available (set ANTHROPIC_API_KEY and `pip install anthropic`). Using the bank.{RESET}")
        else:
            try:
                print(f"{DIM}Asking Claude for fresh {topic.name} questions…{RESET}")
                return generator.generate(topic, count, state.asked_titles(topic.id))
            except Exception as e:  # network, auth, parse errors -> fall back
                print(f"{YELLOW}Claude API call failed ({e}). Falling back to the bank.{RESET}")
    return from_bank(state, topic, count)


# --- session ----------------------------------------------------------------

def run_session(questions: list[Question], topic: Topic, reveal: bool) -> None:
    print(f"\n{BOLD}── {topic.name}: {len(questions)} question(s) ──{RESET}")
    for i, q in enumerate(questions, 1):
        print(f"\n{BOLD}{CYAN}Q{i}. {q.question}{RESET}")
        if q.context:
            print(q.context)
        if not reveal:
            ask(f"{DIM}  Think it through / say it out loud, then press Enter for the solution…{RESET}")
        print(f"\n{GREEN}Solution{RESET}\n{q.solution}\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="prep_agent", description="Daily tech-interview practice agent")
    p.add_argument("--topic", help="topic id/name for this session (skips the prompt)")
    p.add_argument("--topics", action="store_true", help="change your rotating topic set and exit")
    p.add_argument("--set-topics", metavar="LIST", help="set the rotation non-interactively, e.g. 'java,kafka,aws'")
    p.add_argument("--list", action="store_true", help="list all topics and exit")
    p.add_argument("-n", "--count", type=int, choices=[1, 2, 3, 4, 5], help="questions per session (default: 2 or 3)")
    p.add_argument("--source", choices=["auto", "bank", "api"], default="auto",
                   help="auto = Claude API if ANTHROPIC_API_KEY is set, else curated bank")
    p.add_argument("--reveal", action="store_true", help="show solutions immediately (no pause)")
    p.add_argument("--no-commit", action="store_true", help="don't commit the session to its topic branch")
    p.add_argument("--no-push", action="store_true", help="commit to the topic branch locally but don't push")
    args = p.parse_args(argv)

    state = State.load()

    if args.list:
        print_catalog(state.topics)
        return 0
    if args.set_topics:
        picked = parse_selection(args.set_topics)
        if not picked:
            print("No matching topics.", file=sys.stderr)
            return 1
        state.set_topics([t.id for t in picked])
        state.save()
        print("Rotation:", ", ".join(TOPICS[t].name for t in state.topics))
        return 0
    if args.topics:
        choose_topic_set(state)
        state.save()
        return 0

    if args.topic:
        picked = parse_selection(args.topic)
        if len(picked) != 1:
            print(f"--topic must match exactly one topic (got: {[t.id for t in picked] or 'none'})", file=sys.stderr)
            return 1
        topic = picked[0]
    else:
        topic = choose_session_topic(state)

    count = args.count or random.choice([2, 3])
    questions = pick_questions(state, topic, count, args.source)
    if not questions:
        print(f"No questions available for {topic.name}. Add some to {bank.bank_file(topic)} or set ANTHROPIC_API_KEY.")
        return 1

    run_session(questions, topic, args.reveal)

    for q in questions:
        state.record(topic.id, q.id, q.question)
    state.mark_run(topic.id)
    state.save()

    session_file = publisher.save_session(topic, questions)
    print(f"{DIM}Saved: {session_file.relative_to(publisher.REPO_ROOT)}{RESET}")

    if not args.no_commit:
        try:
            branch = publisher.publish(topic, session_file, push=not args.no_push)
            verb = "Committed" if args.no_push else "Pushed"
            print(f"{GREEN}{verb} to branch {branch}{RESET}")
        except subprocess.CalledProcessError as e:
            msg = (e.stderr or e.stdout or str(e)).strip().splitlines()
            print(f"{YELLOW}Couldn't commit/push the session: {msg[-1] if msg else e}{RESET}")
            print(f"{DIM}The session file is still saved locally.{RESET}")
    return 0
