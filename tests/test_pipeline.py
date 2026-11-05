"""End-to-end checks using the mock backend. No network, no credentials."""

from __future__ import annotations

import asyncio
from html import escape as html_escape
from pathlib import Path

import pytest

from rehearsal.config import ConfigError, load_config, split_frontmatter
from rehearsal.debrief import append_to_log, format_log_entry, run_debrief
from rehearsal.engine import Engine, load_session, save_session
from rehearsal.llm import MockLLM, mock_instance
from rehearsal.report import render_report
from rehearsal.schemas import JudgeBrief, PanelistOutput, Session, StructureAnalysis

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def cfg():
    return load_config(ROOT)


def test_config_loads_all_modes_and_roles(cfg):
    assert set(cfg.modes) == {"framing", "method", "preread", "stakeholder", "decide"}
    for required in ("coach", "advocate", "challenger", "judge"):
        assert cfg.mechanism(required).layer == "mechanism"
    panel_ids = {r.id for r in cfg.panel_roles()}
    assert {"director", "senior_manager", "methodology_reviewer", "risk_compliance",
            "tech_product", "finance", "customer", "strategy_partner", "ops", "cross_lob_ba"} <= panel_ids
    for mode in cfg.modes.values():
        for rid in mode.panel:
            assert rid in panel_ids, f"{mode.id} references unknown panelist {rid}"


def test_unknown_panelist_raises(cfg):
    with pytest.raises(ConfigError):
        cfg.panelist("ceo")


def test_frontmatter_split():
    meta, body = split_frontmatter("---\nid: x\nname: X\n---\nbody here")
    assert meta == {"id": "x", "name": "X"}
    assert body.strip() == "body here"
    meta2, body2 = split_frontmatter("no frontmatter")
    assert meta2 == {} and body2 == "no frontmatter"


def test_mock_instance_validates_every_schema():
    for schema in (StructureAnalysis, PanelistOutput, JudgeBrief):
        inst = mock_instance(schema)
        assert schema.model_validate(inst.model_dump())
    assert mock_instance(JudgeBrief).verdict == "go"


def _run(cfg, mode="preread", panel=None, worry="baseline"):
    llm = MockLLM()
    engine = Engine(cfg, llm, mock=True)
    sample = (ROOT / "examples" / "sample_preread.md").read_text(encoding="utf-8")
    session = asyncio.run(engine.run(mode_id=mode, input_text=sample, worry=worry, panel_ids=panel))
    return session, llm


def test_full_run_produces_every_section(cfg):
    session, llm = _run(cfg)
    assert session.structure and session.advocate and session.challenger
    assert session.judge and session.storyline
    assert [r.role_id for r in session.panel] == cfg.modes["preread"].panel
    assert all(r.output is not None for r in session.panel)
    assert not session.errors
    # coach pre, advocate, challenger, 7 panelists, judge, coach post
    assert len(llm.calls) == 3 + len(session.panel) + 2
    assert len(session.calls) == len(llm.calls)


def test_prompts_carry_profile_mode_and_structure(cfg):
    session, llm = _run(cfg, worry="the baseline")
    panel_calls = [c for c in llm.calls if c["schema"] == "PanelistOutput"]
    assert panel_calls
    for call in panel_calls:
        system_text = "\n".join(b["text"] for b in call["system"])
        assert "Workplace profile" in system_text
        assert "Your role:" in system_text
        assert call["system"][-1].get("cache_control") == {"type": "ephemeral"}
        assert "Mode: Pre-read Review" in call["user"]
        assert "Coach's structure analysis" in call["user"]
        assert "the baseline" in call["user"]
    judge_call = next(c for c in llm.calls if c["schema"] == "JudgeBrief")
    assert "Judge focus" in judge_call["user"]
    assert "# Panel (independent responses)" in judge_call["user"]
    post = [c for c in llm.calls if c["schema"] == "Storyline"]
    assert len(post) == 1 and "Judge's brief" in post[0]["user"]


def test_panel_override_and_add(cfg):
    session, _ = _run(cfg, mode="stakeholder", panel=["risk_compliance", "ops"])
    assert [r.role_id for r in session.panel] == ["risk_compliance", "ops"]


def test_unknown_mode_raises(cfg):
    engine = Engine(cfg, MockLLM(), mock=True)
    with pytest.raises(ValueError):
        asyncio.run(engine.run(mode_id="nope", input_text="x"))


def test_save_render_and_reload(cfg, tmp_path):
    session, _ = _run(cfg)
    out = save_session(session, tmp_path)
    assert (out / "session.json").exists() and (out / "input.md").exists()
    html = render_report(session)
    assert "<!doctype html>" in html
    assert "Pre-meeting brief" in html
    assert "Mock run" in html
    assert session.judge.headline in html
    for r in session.panel:
        assert html_escape(r.role_name) in html
    reloaded = load_session(out)
    assert reloaded.id == session.id and reloaded.judge == session.judge


def test_one_failing_role_does_not_kill_the_run(cfg):
    class FlakyLLM(MockLLM):
        async def complete(self, **kw):
            if kw["schema"].__name__ == "PanelistOutput" and "Finance" in kw["user"]:
                raise RuntimeError("boom")
            return await super().complete(**kw)

    engine = Engine(cfg, FlakyLLM(), mock=True)
    session = asyncio.run(engine.run(mode_id="preread", input_text="# Deck\nslide 1"))
    assert "finance" in session.errors
    failed = next(r for r in session.panel if r.role_id == "finance")
    assert failed.output is None and "boom" in failed.error
    assert session.judge is not None  # the judge still ran
    html = render_report(session)
    assert "boom" in html


def test_debrief_records_and_logs(cfg, tmp_path):
    session, _ = _run(cfg)
    n = len(session.judge.likely_questions)
    answers = iter((["y", "n"] * n)[:n] + ["VP asked about Auto overlap", "", "approved with caveats", "went fine"])
    debrief = run_debrief(session, ask=lambda _p: next(answers), say=lambda _m: None)
    assert len(debrief.predicted) == n
    assert debrief.predicted[0].asked is True
    assert debrief.unpredicted == ["VP asked about Auto overlap"]
    assert debrief.outcome_in_room == "approved with caveats"

    log = tmp_path / "log.md"
    append_to_log(log, format_log_entry(session, debrief))
    append_to_log(log, format_log_entry(session, debrief))
    text = log.read_text()
    assert text.count("## ") == 2
    assert "Not predicted, but asked:\n- VP asked about Auto overlap" in text

    session.debrief = debrief
    assert "Debrief (" in render_report(session)
    Session.model_validate_json(session.model_dump_json())
