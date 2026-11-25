"""Project setup, context files, and grade mode."""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path

from rehearsal.config import ASSETS, init_project, install_skills, load_config
from rehearsal.engine import Engine, load_session
from rehearsal.llm import MockLLM, mock_instance
from rehearsal.schemas import GradeReport, PanelistOutput, StructureAnalysis
from rehearsal.staging import advance, init_session


def _project(tmp_path: Path) -> Path:
    proj = tmp_path / "proj"
    proj.mkdir()
    init_project(proj)
    (proj / "analysis").mkdir()
    (proj / "analysis" / "dpd_by_vintage.sql").write_text("select vintage, avg(dpd30) from perf group by 1")
    (proj / "docs").mkdir()
    (proj / "docs" / "metrics.md").write_text("# Metrics\n30+ DPD rate = accounts 30+ dpd / active accounts")
    return proj


def test_init_project_and_discovery(tmp_path, monkeypatch):
    proj = _project(tmp_path)
    assert (proj / ".rehearsal" / "config.yaml").exists()
    assert (proj / ".claude" / "skills" / "rehearse" / "SKILL.md").exists()
    assert "sessions/" in (proj / ".rehearsal" / ".gitignore").read_text()
    # discovery walks up from a subdirectory
    monkeypatch.delenv("REHEARSAL_ROOT", raising=False)
    monkeypatch.chdir(proj / "analysis")
    cfg = load_config()
    assert cfg.base == proj / ".rehearsal" and cfg.project == proj and not cfg.bundled
    assert cfg.sessions_dir == proj / ".rehearsal" / "sessions"
    # idempotent
    assert init_project(proj) == []


def test_install_skills_user_level(tmp_path):
    written = install_skills(home=tmp_path)
    names = sorted(p.parent.name for p in written)
    assert "rehearse" in names
    assert install_skills(home=tmp_path) == []


def test_staged_review_lists_context_files(tmp_path):
    proj = _project(tmp_path)
    cfg = load_config(proj / ".rehearsal")
    sdir = init_session(cfg, mode_id="review", input_text="Finding: vintage 2026-04 drives the rise.",
                        context_paths=["analysis/dpd_by_vintage.sql", "docs"])
    r = advance(cfg, sdir)
    prompt = r.pending[0].prompt_path.read_text()
    assert "# Project files" in prompt
    assert str(proj / "analysis" / "dpd_by_vintage.sql") in prompt
    assert "(directory; list it first)" in prompt
    assert "You may read the project files listed" in prompt
    assert "select vintage" not in prompt  # staged prompts list files, they do not inline them


def test_engine_inlines_context_for_the_api_path(tmp_path):
    proj = _project(tmp_path)
    cfg = load_config(proj / ".rehearsal")
    llm = MockLLM()
    s = asyncio.run(Engine(cfg, llm, mock=True).run(mode_id="review", input_text="x", context_paths=["analysis/dpd_by_vintage.sql"]))
    coach = llm.calls[0]
    assert "select vintage, avg(dpd30)" in coach["user"]
    assert s.context_paths == ["analysis/dpd_by_vintage.sql"]


def test_grade_mode_uses_sealed_key_and_skips_storyline(tmp_path):
    proj = _project(tmp_path)
    cfg = load_config(proj / ".rehearsal")
    key_dir = proj / ".rehearsal" / "scenarios" / "demo"
    key_dir.mkdir(parents=True)
    key_text = "## Planted causes\n1. Autopay migration failure in month 9."
    (key_dir / "answer_key.md.b64").write_bytes(base64.b64encode(key_text.encode()))

    sdir = init_session(cfg, mode_id="grade", input_text="My diagnosis: it was seasonality.",
                        answer_key=".rehearsal/scenarios/demo/answer_key.md.b64")
    r = advance(cfg, sdir)
    r.pending[0].output_path.write_text(mock_instance(StructureAnalysis).model_dump_json())
    r = advance(cfg, sdir)
    assert [p.key for p in r.pending] == ["advocate", "challenger", "methodology_reviewer", "director"]
    for p in r.pending:
        assert "Autopay migration" not in p.prompt_path.read_text()  # panel never sees the key
        schema = {"advocate": "AdvocateOutput", "challenger": "ChallengerOutput"}.get(p.key, "PanelistOutput")
        from rehearsal.schemas import AdvocateOutput, ChallengerOutput
        cls = {"AdvocateOutput": AdvocateOutput, "ChallengerOutput": ChallengerOutput, "PanelistOutput": PanelistOutput}[schema]
        p.output_path.write_text(mock_instance(cls).model_dump_json())
    r = advance(cfg, sdir)
    assert r.stage == "judge" and r.pending[0].schema_name == "GradeReport"
    judge_prompt = r.pending[0].prompt_path.read_text()
    assert "Sealed answer key" in judge_prompt and "Autopay migration failure" in judge_prompt
    r.pending[0].output_path.write_text(mock_instance(GradeReport).model_dump_json())
    r = advance(cfg, sdir)
    assert r.done, r.format()
    s = load_session(sdir)
    assert s.grade is not None and s.judge is None and s.storyline is None
    html = r.report_path.read_text()
    assert "Grade against the answer key" in html and "Model answer" in html
