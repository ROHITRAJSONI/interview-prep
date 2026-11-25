# interview-prep

A daily tech-interview practice agent. Each run picks a topic from your rotation (or asks you to change it), serves **2–3 likely interview questions with model answers**, and commits the session to a per-topic branch (`practice/<topic>`) so your practice history lives in Git.

## Quick start

```bash
git clone -b daily-practice https://github.com/ROHITRAJSONI/interview-prep
cd interview-prep
python3 -m prep_agent            # works offline with the curated bank
```

Optional: fresh, never-repeating questions from Claude:

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python3 -m prep_agent
```

## A session

```
Today's topic: Apache Kafka
Your rotation: Java (8 / 11 / 17), Spring Boot, Microservices Architecture, ...
[Enter] go  ·  [c] pick a different topic  ·  [s] change the rotation set  >

Q1. Your consumer lag keeps growing. How do you troubleshoot it?
  Think it through / say it out loud, then press Enter for the solution…
```

## Commands

| Command | What it does |
|---|---|
| `python3 -m prep_agent` | Daily run: confirm or change today's topic, then practise |
| `python3 -m prep_agent --topic kafka` | Practise a specific topic, no prompt |
| `python3 -m prep_agent --topics` | Interactively change your rotating topic set |
| `python3 -m prep_agent --set-topics "java,kafka,aws"` | Set the rotation in one go (ids, names, or category names) |
| `python3 -m prep_agent --list` | Show every topic and which are in your rotation |
| `-n 3` | Number of questions (default: 2 or 3) |
| `--source bank \| api \| auto` | Force the curated bank or the Claude API (default `auto`) |
| `--reveal` | Show solutions without pausing |
| `--no-push` / `--no-commit` | Commit locally only / don't commit at all |

Topic sets accept ids (`spring-boot`), numbers from `--list`, partial names (`sqs`), or a whole category: `languages`, `aws`, `design`, `data`, `devops`, `all`.

## How it works

- **Topics:** 38 topics across Languages & Frameworks, AWS Cloud, Design & Concurrency, Data & Messaging, and DevOps & Tools (`prep_agent/topics.py`).
- **Curated bank:** `bank/<category>/<topic>.md`, readable Markdown, 2–3 senior-level questions per topic with model answers. Add your own using the same `## Q:` / `### Solution` format.
- **Claude API (optional):** when `ANTHROPIC_API_KEY` is set, the agent asks Claude for the questions *most likely* to be asked for that topic, at senior level, and passes your recent questions so it doesn't repeat them. Override the model with `PREP_MODEL`. Any API failure falls back to the bank.
- **No repeats:** `.prep_state.json` (git-ignored) tracks your rotation and which questions you've seen. The bank recycles only once you've seen every question for a topic.
- **Branches:**
  - `daily-practice`: the agent code (this branch).
  - `practice/<topic>`: one branch per topic, created automatically. Each session is committed as `sessions/<topic>/<date>.md`. The agent uses a temporary git worktree, so your checkout is never switched.

## Run it every day (optional)

macOS/Linux cron, 8:30 every weekday, solutions shown inline:

```cron
30 8 * * 1-5 cd ~/interview-prep && /usr/bin/python3 -m prep_agent --reveal >> ~/interview-prep.log 2>&1
```
