"""Bundle roles, modes, profile and schemas from the repo into app/index.html.

The repo stays the source of truth: edit roles/*.md, modes.yaml or
profile/workplace.md, run this script, republish app/index.html.

    python scripts/build_app.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rehearsal.config import load_config  # noqa: E402
from rehearsal.engine import PANEL_PROTOCOL_EXTRA, PROTOCOL  # noqa: E402
from rehearsal.schemas import (  # noqa: E402
    AdvocateOutput,
    ChallengerOutput,
    JudgeBrief,
    PanelistOutput,
    Storyline,
    StructureAnalysis,
)

PLACEHOLDER = "__REHEARSAL_DATA__"


def build_data() -> dict:
    cfg = load_config(ROOT)
    roles = {
        r.id: {"id": r.id, "name": r.name, "layer": r.layer, "body": r.body}
        for r in cfg.roles.values()
    }
    modes = {
        m.id: {
            "id": m.id,
            "title": m.title,
            "description": m.description,
            "input_hint": m.input_hint,
            "panel": m.panel,
            "emphasis": m.emphasis,
            "judge_focus": m.judge_focus,
        }
        for m in cfg.modes.values()
    }
    schemas = {
        "StructureAnalysis": StructureAnalysis.model_json_schema(),
        "AdvocateOutput": AdvocateOutput.model_json_schema(),
        "ChallengerOutput": ChallengerOutput.model_json_schema(),
        "PanelistOutput": PanelistOutput.model_json_schema(),
        "JudgeBrief": JudgeBrief.model_json_schema(),
        "Storyline": Storyline.model_json_schema(),
    }
    return {
        "protocol": PROTOCOL,
        "panelProtocolExtra": PANEL_PROTOCOL_EXTRA,
        "roles": roles,
        "modes": modes,
        "modeOrder": list(cfg.modes.keys()),
        "schemas": schemas,
        "profileDefault": cfg.read_profile(),
        "debriefLogDefault": cfg.read_debrief_log(),
    }


def build(template: Path, out: Path) -> Path:
    data = build_data()
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    html = template.read_text(encoding="utf-8")
    if PLACEHOLDER not in html:
        raise SystemExit(f"{template} has no {PLACEHOLDER} placeholder")
    out.write_text(html.replace(PLACEHOLDER, payload), encoding="utf-8")
    return out


if __name__ == "__main__":
    result = build(ROOT / "app" / "template.html", ROOT / "app" / "index.html")
    print(result, f"{result.stat().st_size / 1024:.0f} KB")
