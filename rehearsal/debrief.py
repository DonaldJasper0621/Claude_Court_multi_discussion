"""Post-meeting debrief: record what was actually asked, feed the profile."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from .schemas import Debrief, DebriefAnswer, Session

Ask = Callable[[str], str]


def run_debrief(session: Session, ask: Ask = input, say: Callable[[str], None] = print) -> Debrief:
    """Interactive debrief. `ask` and `say` are injectable for tests."""
    if session.judge is None:
        raise ValueError("This session has no Judge brief to debrief against.")

    say(f"\nDebrief for {session.id} ({session.mode_title})")
    say("For each predicted question, answer y if it was actually asked, n if not.\n")

    predicted: list[DebriefAnswer] = []
    for q in session.judge.likely_questions:
        say(f"  [{q.asked_by}] {q.question}")
        answer = ask("  asked? [y/n] ").strip().lower()
        predicted.append(DebriefAnswer(question=q.question, predicted_for=q.asked_by, asked=answer.startswith("y")))

    say("\nQuestions that were asked but not predicted. Include who asked. Blank line to finish.")
    unpredicted: list[str] = []
    while True:
        line = ask("  > ").strip()
        if not line:
            break
        unpredicted.append(line)

    outcome = ask("\nOutcome in the room (e.g. approved / sent back / deferred, and why): ").strip()
    notes = ask("Anything else worth remembering about how it went: ").strip()

    return Debrief(
        recorded_at=datetime.now().isoformat(timespec="minutes"),
        outcome_in_room=outcome,
        predicted=predicted,
        unpredicted=unpredicted,
        notes=notes,
    )


def debrief_from_file(session: Session, path: Path) -> Debrief:
    """Non-interactive debrief from a JSON file:

    {"outcome_in_room": "...", "asked": [0, 2], "unpredicted": ["..."], "notes": "..."}

    `asked` lists zero-based indices into the Judge's likely_questions.
    """
    import json

    if session.judge is None:
        raise ValueError("This session has no Judge brief to debrief against.")
    data = json.loads(path.read_text(encoding="utf-8"))
    questions = session.judge.likely_questions
    asked_raw = data.get("asked", [])
    if not isinstance(asked_raw, list):
        raise ValueError("'asked' must be a list of indices")
    asked: set[int] = set()
    for i in asked_raw:
        if not isinstance(i, int) or not 0 <= i < len(questions):
            raise ValueError(f"'asked' index {i!r} is out of range 0..{len(questions) - 1}")
        asked.add(i)
    return Debrief(
        recorded_at=datetime.now().isoformat(timespec="minutes"),
        outcome_in_room=str(data.get("outcome_in_room", "")).strip(),
        predicted=[
            DebriefAnswer(question=q.question, predicted_for=q.asked_by, asked=(i in asked))
            for i, q in enumerate(questions)
        ],
        unpredicted=[str(x) for x in data.get("unpredicted", [])],
        notes=str(data.get("notes", "")).strip(),
    )


def format_log_entry(session: Session, debrief: Debrief) -> str:
    asked = [a for a in debrief.predicted if a.asked]
    missed = [a for a in debrief.predicted if not a.asked]
    lines = [f"## {debrief.recorded_at[:10]} · {session.mode} · {session.id}"]
    lines.append(f"Outcome: {debrief.outcome_in_room or '(not recorded)'}")
    lines.append("Predicted and asked:")
    lines += [f"- {a.question} (predicted for {a.predicted_for})" for a in asked] or ["- (none)"]
    lines.append("Predicted, not asked:")
    lines += [f"- {a.question} (predicted for {a.predicted_for})" for a in missed] or ["- (none)"]
    lines.append("Not predicted, but asked:")
    lines += [f"- {q}" for q in debrief.unpredicted] or ["- (none)"]
    if debrief.notes:
        lines.append("Notes:")
        lines.append(f"- {debrief.notes}")
    return "\n".join(lines) + "\n"


def append_to_log(log_path: Path, entry: str) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    sep = "" if not existing or existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
    log_path.write_text(existing + sep + entry, encoding="utf-8")


def hit_rate(debrief: Debrief) -> tuple[int, int]:
    asked = sum(1 for a in debrief.predicted if a.asked)
    return asked, len(debrief.predicted)
