"""Staged runner: the same pipeline, driven by an external orchestrator.

Instead of calling the model itself, this writes one prompt file per role and
waits for someone (a Claude Code session with subagents, a human, a script) to
write the matching JSON output. `advance()` ingests whatever outputs exist,
validates them against the role's schema, and writes the prompts for the next
stage. When every stage is complete it renders the report.

Stages: coach_pre -> panel (advocate, challenger, panelists) -> judge -> coach_post
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from .config import Config, Role
from .engine import Prompts, load_session, new_session, save_session
from .report import write_report
from .schemas import (
    AdvocateOutput,
    CallMeta,
    ChallengerOutput,
    JudgeBrief,
    PanelistOutput,
    PanelistResult,
    Session,
    Storyline,
    StructureAnalysis,
    Usage,
)

STAGE_ORDER = ["coach_pre", "panel", "judge", "coach_post"]
ORCHESTRATED_MODEL = "orchestrated"  # model is whoever runs the prompt files


@dataclass
class Pending:
    key: str
    role_name: str
    schema_name: str
    prompt_path: Path
    output_path: Path
    error: str | None = None


@dataclass
class StageReport:
    session_dir: Path
    stage: str | None
    pending: list[Pending] = field(default_factory=list)
    done: bool = False
    report_path: Path | None = None

    def format(self) -> str:
        lines = [f"SESSION {self.session_dir}"]
        if self.done:
            lines.append("DONE")
            lines.append(f"REPORT {self.report_path}")
            return "\n".join(lines)
        lines.append(f"STAGE {self.stage}: {len(self.pending)} pending")
        for p in self.pending:
            line = f"  {p.key} | {p.role_name} | prompt={p.prompt_path} | output={p.output_path}"
            if p.error:
                line += f" | INVALID: {p.error}"
            lines.append(line)
        return "\n".join(lines)


@dataclass
class _Expected:
    key: str
    role: Role
    schema: type[BaseModel]
    system: list[dict[str, Any]]
    user: str


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #


def init_session(
    cfg: Config,
    *,
    mode_id: str,
    input_text: str,
    worry: str | None = None,
    panel_ids: list[str] | None = None,
) -> Path:
    mode = cfg.modes.get(mode_id)
    if mode is None:
        raise ValueError(f"Unknown mode '{mode_id}'. Available: {', '.join(cfg.modes)}")
    session, _ = new_session(cfg, mode, input_text, worry, panel_ids)
    return save_session(session, cfg.sessions_dir)


def advance(cfg: Config, session_dir: Path, *, skip: list[str] | None = None) -> StageReport:
    session = load_session(session_dir)
    mode = cfg.modes[session.mode]
    panel_roles = [cfg.panelist(rid) for rid in session.panel_ids]
    prompts = Prompts(cfg, mode, session.input_text, session.worry)
    skip = set(skip or [])

    for stage in STAGE_ORDER:
        expected = _expected_for(stage, cfg, prompts, session, panel_roles)
        pending: list[Pending] = []
        stage_dir = session_dir / "stages" / stage
        for exp in expected:
            if _is_ingested(session, exp.key):
                continue
            out_path = stage_dir / f"{exp.key}.output.json"
            prompt_path = stage_dir / f"{exp.key}.prompt.md"
            if exp.key in skip:
                _record(session, exp, None, error="skipped by orchestrator")
                continue
            error = None
            if out_path.exists():
                try:
                    parsed = _parse_output(out_path, exp.schema)
                    _record(session, exp, parsed)
                    continue
                except (ValidationError, ValueError, json.JSONDecodeError) as e:
                    error = _short(str(e))
            stage_dir.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(_render_prompt(exp, out_path), encoding="utf-8")
            pending.append(Pending(exp.key, exp.role.name, exp.schema.__name__, prompt_path, out_path, error))
        if stage == "panel":
            _finalize_panel(session, panel_roles)
        if pending:
            save_session(session, cfg.sessions_dir)
            return StageReport(session_dir=session_dir, stage=stage, pending=pending)

    save_session(session, cfg.sessions_dir)
    report = write_report(session, session_dir)
    return StageReport(session_dir=session_dir, stage=None, done=True, report_path=report)


# --------------------------------------------------------------------------- #
# Internals
# --------------------------------------------------------------------------- #


def _expected_for(stage: str, cfg: Config, prompts: Prompts, session: Session, panel_roles: list[Role]) -> list[_Expected]:
    if stage == "coach_pre":
        sys_, user = prompts.coach_pre()
        return [_Expected("coach_pre", cfg.mechanism("coach"), StructureAnalysis, sys_, user)]
    if stage == "panel":
        out: list[_Expected] = []
        sys_, user = prompts.advocate(session.structure)
        out.append(_Expected("advocate", cfg.mechanism("advocate"), AdvocateOutput, sys_, user))
        sys_, user = prompts.challenger(session.structure)
        out.append(_Expected("challenger", cfg.mechanism("challenger"), ChallengerOutput, sys_, user))
        for role in panel_roles:
            sys_, user = prompts.panelist(role, session.structure)
            out.append(_Expected(role.id, role, PanelistOutput, sys_, user))
        return out
    if stage == "judge":
        sys_, user = prompts.judge(session, panel_roles)
        return [_Expected("judge", cfg.mechanism("judge"), JudgeBrief, sys_, user)]
    if stage == "coach_post":
        sys_, user = prompts.coach_post(session)
        return [_Expected("coach_post", cfg.mechanism("coach"), Storyline, sys_, user)]
    raise ValueError(stage)


def _is_ingested(session: Session, key: str) -> bool:
    if key in session.errors:
        return True
    if key == "coach_pre":
        return session.structure is not None
    if key == "advocate":
        return session.advocate is not None
    if key == "challenger":
        return session.challenger is not None
    if key == "judge":
        return session.judge is not None
    if key == "coach_post":
        return session.storyline is not None
    return any(r.role_id == key and r.output is not None for r in session.panel)


def _record(session: Session, exp: _Expected, parsed: BaseModel | None, *, error: str | None = None) -> None:
    key = exp.key
    session.calls.append(CallMeta(role_id=key, model=ORCHESTRATED_MODEL, seconds=0.0, usage=Usage(), error=error))
    if error:
        session.errors[key] = error
    if key == "coach_pre":
        session.structure = parsed  # type: ignore[assignment]
    elif key == "advocate":
        session.advocate = parsed  # type: ignore[assignment]
    elif key == "challenger":
        session.challenger = parsed  # type: ignore[assignment]
    elif key == "judge":
        session.judge = parsed  # type: ignore[assignment]
    elif key == "coach_post":
        session.storyline = parsed  # type: ignore[assignment]
    else:
        session.panel = [r for r in session.panel if r.role_id != key]
        session.panel.append(PanelistResult(role_id=key, role_name=exp.role.name, output=parsed, error=error))  # type: ignore[arg-type]


def _finalize_panel(session: Session, panel_roles: list[Role]) -> None:
    order = {r.id: i for i, r in enumerate(panel_roles)}
    session.panel.sort(key=lambda r: order.get(r.role_id, 99))


def _parse_output(path: Path, schema: type[BaseModel]) -> BaseModel:
    text = path.read_text(encoding="utf-8").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
    return schema.model_validate_json(text)


def _short(msg: str, limit: int = 600) -> str:
    msg = " ".join(msg.split())
    return msg if len(msg) <= limit else msg[: limit - 3] + "..."


def _render_prompt(exp: _Expected, out_path: Path) -> str:
    system_text = "\n\n".join(str(b.get("text", "")) for b in exp.system)
    schema_json = json.dumps(exp.schema.model_json_schema(), indent=2, ensure_ascii=False)
    return (
        f"# How to respond\n\n"
        f"You are performing one role in a rehearsal. Read the SYSTEM and USER sections below and "
        f"respond by writing a single JSON object to this file:\n\n"
        f"    {out_path}\n\n"
        f"The JSON must validate against the SCHEMA section (schema name: {exp.schema.__name__}). "
        f"Write raw JSON only: no Markdown fences, no commentary, no fields outside the schema. "
        f"Do not read other roles' outputs or any other file in the session directory. "
        f"Do not reply in chat; the file is the only output.\n\n"
        f"# SYSTEM\n\n{system_text}\n\n"
        f"# USER\n\n{exp.user}\n\n"
        f"# SCHEMA\n\n```json\n{schema_json}\n```\n"
    )
