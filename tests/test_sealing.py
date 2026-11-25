"""Leak prevention and the --until stop."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from rehearsal.config import SEALED_DENY_RULES, init_project, load_config, write_project_settings
from rehearsal.engine import load_session
from rehearsal.llm import mock_instance
from rehearsal.schemas import AdvocateOutput, ChallengerOutput, GradeReport, JudgeBrief, PanelistOutput, StructureAnalysis
from rehearsal.staging import ANSWER_KEY_HEADER, advance, init_session

SCHEMAS = {"StructureAnalysis": StructureAnalysis, "AdvocateOutput": AdvocateOutput, "ChallengerOutput": ChallengerOutput,
           "PanelistOutput": PanelistOutput, "GradeReport": GradeReport, "JudgeBrief": JudgeBrief}


def _answer_all(report):
    for p in report.pending:
        p.output_path.write_text(mock_instance(SCHEMAS[p.schema_name]).model_dump_json())


def test_init_writes_deny_rules_and_merges(tmp_path):
    proj = tmp_path / "p"; proj.mkdir()
    (proj / ".claude").mkdir()
    (proj / ".claude" / "settings.json").write_text(json.dumps({"permissions": {"allow": ["Bash(pytest:*)"], "deny": ["Read(./.env)"]}}))
    init_project(proj)
    data = json.loads((proj / ".claude" / "settings.json").read_text())
    assert data["permissions"]["allow"] == ["Bash(pytest:*)"]
    assert "Read(./.env)" in data["permissions"]["deny"]
    for rule in SEALED_DENY_RULES:
        assert rule in data["permissions"]["deny"]
    assert write_project_settings(proj) is False  # idempotent
    # the grade command itself is not caught by the Bash prefix rules
    cmd = "python -m rehearsal.cli stage init -m grade -i docs/diagnosis.md --answer-key .rehearsal/scenarios/x/answer_key.md.b64"
    assert not any(cmd.startswith(r[len("Bash("):].split(":*")[0]) for r in SEALED_DENY_RULES if r.startswith("Bash("))


def test_grade_redacts_key_from_judge_prompt_when_done(tmp_path):
    proj = tmp_path / "p"; proj.mkdir(); init_project(proj)
    cfg = load_config(proj / ".rehearsal")
    kd = proj / ".rehearsal" / "scenarios" / "demo"; kd.mkdir(parents=True)
    secret = "SECRET-CAUSE-42: the autopay migration"
    (kd / "answer_key.md.b64").write_bytes(base64.b64encode(secret.encode()))
    sdir = init_session(cfg, mode_id="grade", input_text="diagnosis", answer_key=".rehearsal/scenarios/demo/answer_key.md.b64")
    r = advance(cfg, sdir); _answer_all(r)
    r = advance(cfg, sdir); _answer_all(r)
    r = advance(cfg, sdir)
    assert r.stage == "judge"
    judge_prompt = r.pending[0].prompt_path
    assert secret in judge_prompt.read_text()
    _answer_all(r)
    r = advance(cfg, sdir)
    assert r.done
    text = judge_prompt.read_text()
    assert secret not in text and "[redacted after grading" in text and ANSWER_KEY_HEADER not in text
    # nothing else in the session dir holds the secret
    for f in sdir.rglob("*"):
        if f.is_file():
            assert secret not in f.read_text(errors="ignore"), f


def test_until_judge_skips_storyline(tmp_path):
    proj = tmp_path / "p"; proj.mkdir(); init_project(proj)
    cfg = load_config(proj / ".rehearsal")
    sdir = init_session(cfg, mode_id="review", input_text="findings", panel_ids=["finance"])
    for _ in range(3):
        r = advance(cfg, sdir, until="judge")
        assert not r.done
        _answer_all(r)
    r = advance(cfg, sdir, until="judge")
    assert r.done and r.report_path.exists()
    s = load_session(sdir)
    assert s.judge is not None and s.storyline is None
    assert not (sdir / "stages" / "coach_post").exists()
