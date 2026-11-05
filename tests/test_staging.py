"""Staged runner: prompts out, JSON in, report at the end. No network."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rehearsal.cli import main
from rehearsal.config import load_config
from rehearsal.debrief import debrief_from_file
from rehearsal.engine import load_session
from rehearsal.llm import mock_instance
from rehearsal.schemas import (
    AdvocateOutput,
    ChallengerOutput,
    JudgeBrief,
    PanelistOutput,
    Storyline,
    StructureAnalysis,
)
from rehearsal.staging import advance, init_session

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = {
    "StructureAnalysis": StructureAnalysis,
    "AdvocateOutput": AdvocateOutput,
    "ChallengerOutput": ChallengerOutput,
    "PanelistOutput": PanelistOutput,
    "JudgeBrief": JudgeBrief,
    "Storyline": Storyline,
}


@pytest.fixture
def cfg(tmp_path):
    c = load_config(ROOT)
    c.paths["sessions"] = str(tmp_path / "sessions")
    return c


def _answer_all(report):
    """Pretend to be the orchestrator: write a schema-valid JSON for every pending prompt."""
    for p in report.pending:
        assert p.prompt_path.exists()
        text = p.prompt_path.read_text()
        assert "# SYSTEM" in text and "# USER" in text and "# SCHEMA" in text
        assert str(p.output_path) in text
        p.output_path.write_text(mock_instance(SCHEMAS[p.schema_name]).model_dump_json())


def test_staged_run_walks_all_four_stages(cfg):
    sample = (ROOT / "examples" / "sample_preread.md").read_text()
    sdir = init_session(cfg, mode_id="preread", input_text=sample, worry="baseline")
    assert (sdir / "session.json").exists()

    r = advance(cfg, sdir)
    assert r.stage == "coach_pre" and [p.key for p in r.pending] == ["coach_pre"]
    _answer_all(r)

    r = advance(cfg, sdir)
    assert r.stage == "panel"
    keys = [p.key for p in r.pending]
    assert keys[:2] == ["advocate", "challenger"]
    assert keys[2:] == cfg.modes["preread"].panel
    # the panel prompts must carry the coach's structure analysis
    assert "Coach's structure analysis" in r.pending[2].prompt_path.read_text()
    _answer_all(r)

    r = advance(cfg, sdir)
    assert r.stage == "judge"
    judge_prompt = r.pending[0].prompt_path.read_text()
    assert "# Panel (independent responses)" in judge_prompt and "Judge focus" in judge_prompt
    _answer_all(r)

    r = advance(cfg, sdir)
    assert r.stage == "coach_post"
    assert "Judge's brief" in r.pending[0].prompt_path.read_text()
    _answer_all(r)

    r = advance(cfg, sdir)
    assert r.done and r.report_path.exists()
    s = load_session(sdir)
    assert s.structure and s.advocate and s.challenger and s.judge and s.storyline
    assert [p.role_id for p in s.panel] == cfg.modes["preread"].panel
    assert not s.errors
    assert "Pre-meeting brief" in r.report_path.read_text()


def test_invalid_output_is_reported_and_retried(cfg):
    sdir = init_session(cfg, mode_id="method", input_text="# Approach\nstuff")
    r = advance(cfg, sdir)
    r.pending[0].output_path.parent.mkdir(parents=True, exist_ok=True)
    r.pending[0].output_path.write_text('{"not": "valid"}')
    r2 = advance(cfg, sdir)
    assert r2.stage == "coach_pre" and r2.pending[0].error and "validation" in r2.pending[0].error.lower()
    # fix it
    r2.pending[0].output_path.write_text(mock_instance(StructureAnalysis).model_dump_json())
    r3 = advance(cfg, sdir)
    assert r3.stage == "panel"


def test_fenced_json_is_tolerated(cfg):
    sdir = init_session(cfg, mode_id="method", input_text="# Approach\nstuff")
    r = advance(cfg, sdir)
    r.pending[0].output_path.parent.mkdir(parents=True, exist_ok=True)
    body = mock_instance(StructureAnalysis).model_dump_json()
    r.pending[0].output_path.write_text(f"```json\n{body}\n```")
    assert advance(cfg, sdir).stage == "panel"


def test_skip_marks_role_failed_and_moves_on(cfg):
    sdir = init_session(cfg, mode_id="stakeholder", input_text="ask", panel_ids=["ops", "finance"])
    _answer_all(advance(cfg, sdir))
    r = advance(cfg, sdir)
    assert r.stage == "panel"
    # answer everything except finance, then skip it
    for p in r.pending:
        if p.key != "finance":
            p.output_path.write_text(mock_instance(SCHEMAS[p.schema_name]).model_dump_json())
    r = advance(cfg, sdir, skip=["finance"])
    assert r.stage == "judge"
    s = load_session(sdir)
    assert "finance" in s.errors
    fin = next(p for p in s.panel if p.role_id == "finance")
    assert fin.output is None and fin.error
    assert "failed to respond" in r.pending[0].prompt_path.read_text()


def test_cli_stage_and_debrief_from_file(cfg, tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("REHEARSAL_ROOT", str(ROOT))
    # route sessions into tmp by patching config.yaml paths is heavier; use the API for init and the CLI for next
    sdir = init_session(cfg, mode_id="decide", input_text="A or B", panel_ids=["director"])
    for _ in range(4):
        r = advance(cfg, sdir)
        _answer_all(r)
    rc = main(["--root", str(ROOT), "stage", "next", str(sdir)])
    out = capsys.readouterr().out
    assert rc == 0 and "DONE" in out and "REPORT" in out

    s = load_session(sdir)
    n = len(s.judge.likely_questions)
    f = tmp_path / "d.json"
    f.write_text(json.dumps({"outcome_in_room": "approved", "asked": [0], "unpredicted": ["x?"], "notes": "ok"}))
    d = debrief_from_file(s, f)
    assert len(d.predicted) == n and d.predicted[0].asked and d.unpredicted == ["x?"]
    f.write_text(json.dumps({"asked": [99]}))
    with pytest.raises(ValueError):
        debrief_from_file(s, f)
