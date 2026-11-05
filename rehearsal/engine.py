"""Orchestration: Coach pre-pass -> parallel panel -> Judge -> Coach post-pass.

Prompt layout per call (designed for prompt caching):

    system[0]  shared protocol                  (stable across runs)
    system[1]  role persona                     (stable across runs)
    system[2]  workplace profile + debrief log  (stable across a day)  <- cache_control
    user       mode emphasis + material + structure analysis + worry   (volatile)
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel

from .config import Config, Mode, Role
from .llm import LLM, LLMError
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

T = TypeVar("T", bound=BaseModel)
Progress = Callable[[str], None]

LANGUAGE_NAMES = {"en": "English", "zh-TW": "Traditional Chinese", "zh": "Traditional Chinese"}


# --------------------------------------------------------------------------- #
# Prompt pieces
# --------------------------------------------------------------------------- #

PROTOCOL = """\
You are one voice in a pre-meeting rehearsal for a Business Analyst at a large
US consumer bank. The analyst is about to take material (a deck outline, memo,
problem statement, analysis plan, or set of options) into a real meeting. Your
job is to react exactly as the person you are playing would, so the analyst can
prepare.

Rules of the rehearsal:

1. You are reading independently. You have not seen any other reviewer's
   response and you must not guess at it. Give your own view.
2. React to this material. Reference specific slides, sections, claims or
   numbers. A comment that could be pasted onto a different deck is worthless.
3. The material is de-identified. Bracketed placeholders such as [X], [N] or
   [$M] stand for real figures that exist in the actual document. Do not
   complain that numbers are missing. If a figure's provenance or baseline
   matters, ask about that instead.
4. Stay in your lane. Other reviewers cover other angles. Depth in your own
   perspective beats breadth.
5. Be direct and specific. No hedging, no generic advice, no lists of every
   conceivable concern. Name the one or two things you actually care about.
6. Respond in {language}. Keep technical and business terms in English.
7. Your answer must follow the required output schema exactly.
"""

PANEL_PROTOCOL_EXTRA = """\
8. "the_question" is the single question you would actually say aloud in the
   room. Not a list. Not rhetorical. The question you would really ask.
9. "what_would_make_me_say_yes" is concrete: the evidence, change or
   commitment that would move you to support this.
"""


def _language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, code)


def _system_blocks(cfg: Config, role: Role, profile_block: str, *, panel: bool) -> list[dict[str, Any]]:
    protocol = PROTOCOL.format(language=_language_name(cfg.output_language))
    if panel:
        protocol += PANEL_PROTOCOL_EXTRA
    return [
        {"type": "text", "text": protocol},
        {"type": "text", "text": f"# Your role: {role.name}\n\n{role.body}"},
        {"type": "text", "text": profile_block, "cache_control": {"type": "ephemeral"}},
    ]


def _profile_block(cfg: Config) -> str:
    profile = cfg.read_profile() or "(No workplace profile provided.)"
    log = cfg.read_debrief_log() or "(No debrief history yet.)"
    return (
        "# Workplace profile (maintained by the analyst; read it before the material)\n\n"
        f"{profile}\n\n"
        "# Debrief log (what real stakeholders actually asked in past meetings)\n\n"
        f"{log}"
    )


def _material_block(mode: Mode, input_text: str, worry: str | None) -> str:
    worry_text = worry.strip() if worry and worry.strip() else "(not stated)"
    return (
        f"# Mode: {mode.title}\n{mode.emphasis}\n\n"
        f"# Material\n\n{input_text.strip()}\n\n"
        f"# What the analyst is worried about\n{worry_text}\n"
    )


def _structure_block(structure: StructureAnalysis | None) -> str:
    if structure is None:
        return "# Coach's structure analysis\n(unavailable for this run)\n"
    lines = [
        "# Coach's structure analysis (read alongside the material; it is a map, not a verdict)",
        f"Restatement: {structure.one_line_restatement}",
        f"Central question: {structure.central_question}",
        f"Leads with answer: {'yes' if structure.leads_with_answer else 'no'}. {structure.answer_first_note}",
        "Issue tree:",
    ]
    for branch in structure.issue_tree:
        lines.append(f"- {branch.sub_question}")
        for p in branch.sub_points:
            lines.append(f"  - {p}")
    if structure.mece_gaps:
        lines.append("MECE gaps: " + "; ".join(structure.mece_gaps))
    if structure.logic_breaks:
        lines.append("Logic breaks:")
        for lb in structure.logic_breaks:
            lines.append(f"- {lb.claim} ({lb.where_in_material}): {lb.why_it_does_not_follow}")
    return "\n".join(lines) + "\n"


def _dump(model: BaseModel | None) -> str:
    return "(unavailable)" if model is None else json.dumps(model.model_dump(), indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# Engine
# --------------------------------------------------------------------------- #


class Engine:
    def __init__(self, cfg: Config, llm: LLM, progress: Progress | None = None, *, mock: bool = False) -> None:
        self.cfg = cfg
        self.llm = llm
        self.progress = progress or (lambda _msg: None)
        self.mock = mock
        self._sem = asyncio.Semaphore(cfg.max_concurrency)

    # ----- public --------------------------------------------------------- #

    async def run(
        self,
        *,
        mode_id: str,
        input_text: str,
        worry: str | None = None,
        panel_ids: list[str] | None = None,
    ) -> Session:
        mode = self.cfg.modes.get(mode_id)
        if mode is None:
            raise ValueError(f"Unknown mode '{mode_id}'. Available: {', '.join(self.cfg.modes)}")
        panel_ids = list(panel_ids) if panel_ids else list(mode.panel)
        panel_roles = [self.cfg.panelist(rid) for rid in panel_ids]

        now = datetime.now()
        session = Session(
            id=f"{now:%Y%m%d-%H%M%S}-{mode.id}",
            created_at=now.isoformat(timespec="seconds"),
            mode=mode.id,
            mode_title=mode.title,
            input_text=input_text,
            worry=worry,
            panel_ids=panel_ids,
            mock=self.mock,
            output_language=self.cfg.output_language,
        )
        profile_block = _profile_block(self.cfg)
        material = _material_block(mode, input_text, worry)

        # 1. Coach pre-pass
        self.progress("Coach: structure analysis")
        coach = self.cfg.mechanism("coach")
        session.structure = await self._call(
            session,
            coach,
            StructureAnalysis,
            system=_system_blocks(self.cfg, coach, profile_block, panel=False),
            user=material
            + "\n# Task\nThis is the PRE-PASS. Produce the structure analysis described in your role. "
            "Do not evaluate the recommendation; map the argument.",
            kind="coach",
        )
        structure_block = _structure_block(session.structure)
        shared_user = material + "\n" + structure_block

        # 2. Advocate, Challenger, panel in parallel
        self.progress(f"Panel: advocate, challenger and {len(panel_roles)} panelists in parallel")
        advocate = self.cfg.mechanism("advocate")
        challenger = self.cfg.mechanism("challenger")
        tasks: list[asyncio.Task[Any]] = [
            asyncio.create_task(
                self._call(
                    session,
                    advocate,
                    AdvocateOutput,
                    system=_system_blocks(self.cfg, advocate, profile_block, panel=False),
                    user=shared_user + "\n# Task\nBuild the strongest honest case for this material.",
                    kind="panel",
                )
            ),
            asyncio.create_task(
                self._call(
                    session,
                    challenger,
                    ChallengerOutput,
                    system=_system_blocks(self.cfg, challenger, profile_block, panel=False),
                    user=shared_user + "\n# Task\nFind the holes, ranked by damage if raised live.",
                    kind="panel",
                )
            ),
        ]
        for role in panel_roles:
            tasks.append(
                asyncio.create_task(
                    self._call(
                        session,
                        role,
                        PanelistOutput,
                        system=_system_blocks(self.cfg, role, profile_block, panel=True),
                        user=shared_user + f"\n# Task\nRespond as {role.name}, following the output schema.",
                        kind="panel",
                    )
                )
            )
        results = await asyncio.gather(*tasks)
        session.advocate = results[0]
        session.challenger = results[1]
        for role, output in zip(panel_roles, results[2:]):
            session.panel.append(
                PanelistResult(
                    role_id=role.id,
                    role_name=role.name,
                    output=output,
                    error=session.errors.get(role.id),
                )
            )

        # 3. Judge
        self.progress("Judge: synthesizing the brief")
        judge = self.cfg.mechanism("judge")
        session.judge = await self._call(
            session,
            judge,
            JudgeBrief,
            system=_system_blocks(self.cfg, judge, profile_block, panel=False),
            user=self._judge_user(mode, shared_user, session, panel_roles),
            kind="judge",
        )

        # 4. Coach post-pass
        self.progress("Coach: recommended storyline")
        session.storyline = await self._call(
            session,
            coach,
            Storyline,
            system=_system_blocks(self.cfg, coach, profile_block, panel=False),
            user=(
                material
                + "\n"
                + structure_block
                + "\n# Judge's brief\n"
                + _dump(session.judge)
                + "\n\n# Task\nThis is the POST-PASS. Propose the restructured storyline described in your role, "
                "addressing the Judge's must-fix items where structure can address them."
            ),
            kind="coach",
            role_key="coach_post",
        )
        return session

    # ----- internals ------------------------------------------------------ #

    def _judge_user(self, mode: Mode, shared_user: str, session: Session, panel_roles: list[Role]) -> str:
        parts = [shared_user, f"# Judge focus for this mode\n{mode.judge_focus}\n"]
        parts.append("# Advocate\n" + _dump(session.advocate))
        parts.append("# Challenger\n" + _dump(session.challenger))
        parts.append("# Panel (independent responses)")
        for role, result in zip(panel_roles, session.panel):
            parts.append(f"## {role.name} (`{role.id}`)\n" + _dump(result.output))
        if session.errors:
            parts.append("# Roles that failed to respond\n" + "\n".join(f"- {k}: {v}" for k, v in session.errors.items()))
        parts.append("# Task\nProduce the pre-meeting brief described in your role, following the output schema.")
        return "\n\n".join(parts)

    async def _call(
        self,
        session: Session,
        role: Role,
        schema: type[T],
        *,
        system: list[dict[str, Any]],
        user: str,
        kind: str,
        role_key: str | None = None,
    ) -> T | None:
        model = self.cfg.models[kind]
        effort = self.cfg.effort[kind]
        key = role_key or role.id
        start = time.perf_counter()
        async with self._sem:
            try:
                output, usage = await self.llm.complete(
                    system=system,
                    user=user,
                    schema=schema,
                    model=model,
                    effort=effort,
                    max_tokens=self.cfg.max_tokens,
                )
                error = None
            except LLMError as e:
                output, usage, error = None, Usage(), str(e)
            except Exception as e:  # noqa: BLE001 - one role failing must not kill the run
                output, usage, error = None, Usage(), f"{type(e).__name__}: {e}"
        seconds = time.perf_counter() - start
        session.calls.append(CallMeta(role_id=key, model=model, seconds=round(seconds, 2), usage=usage, error=error))
        if error:
            session.errors[key] = error
            self.progress(f"  {role.name}: FAILED ({error})")
        else:
            self.progress(f"  {role.name}: done in {seconds:.1f}s")
        return output


# --------------------------------------------------------------------------- #
# Persistence
# --------------------------------------------------------------------------- #


def save_session(session: Session, sessions_dir: Path) -> Path:
    out = sessions_dir / session.id
    out.mkdir(parents=True, exist_ok=True)
    (out / "session.json").write_text(session.model_dump_json(indent=2), encoding="utf-8")
    (out / "input.md").write_text(session.input_text, encoding="utf-8")
    return out


def load_session(path: Path) -> Session:
    if path.is_dir():
        path = path / "session.json"
    return Session.model_validate_json(path.read_text(encoding="utf-8"))
