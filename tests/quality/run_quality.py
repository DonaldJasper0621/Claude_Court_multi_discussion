"""Quality harness for the review panel.

A small set of review drafts with known defects (and one solid draft). Each
round stages a `review` run per case, an orchestrator (a Claude Code session)
plays the roles, an independent scorer compares every role's output with the
defect list, and this script aggregates the scores.

    python tests/quality/run_quality.py prepare <round> [--cases a,b]
    python tests/quality/run_quality.py next <round> <case>      # after a stage's agents finish
    python tests/quality/run_quality.py score <round> <case>     # writes the scorer's prompt
    python tests/quality/run_quality.py summarize <round>        # after scores.json exist
    python tests/quality/run_quality.py compare <round1> <round2>

Layout:
    tests/quality/cases/<case>/draft.md, queries/*.sql     what the panel sees
    tests/quality/defects/<case>.yaml                       hidden from the panel
    tests/quality/results/<round>/<case>/                   session, timing, scoring prompt, scores.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field, ValidationError

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))

from rehearsal.config import ASSETS, load_config  # noqa: E402
from rehearsal.engine import load_session  # noqa: E402
from rehearsal.staging import advance, init_session  # noqa: E402

DATA_DIR = ROOT / "playground" / "cobrand-delinquency" / "data" / "cobrand_delinquency"
DATA_CONTEXT = ["data_dictionary.md", "ops_notes.md", "kpi_report_as_published.csv", "campaigns.csv", "accounts.csv", "monthly_performance.csv"]
ROLE_KEYS = ["coach_pre", "advocate", "challenger", "methodology_reviewer", "senior_manager", "finance", "risk_compliance", "cross_lob_ba"]


# --------------------------------------------------------------------------- #
# Scoring contract (what the independent scorer writes)
# --------------------------------------------------------------------------- #


class Unsupported(BaseModel):
    quote: str = Field(description="The role's own words, verbatim or closely paraphrased.")
    why: str = Field(description="Why it is unsupported, generic, or wrong given the files.")


class RoleScore(BaseModel):
    role_id: str
    caught: list[str] = Field(description="Defect ids the role clearly identified (the specific problem, not just the area).")
    partially: list[str] = Field(description="Defect ids the role gestured at without pinning down.")
    missed: list[str]
    unsupported_or_generic: list[Unsupported]
    claims_total: int = Field(description="Number of distinct concerns, challenges or questions the role raised.")
    claims_citing_file: int = Field(description="Of those, how many name a specific file.")
    claims_citing_file_and_line: int = Field(description="Of those, how many name a file and a line, slide, row or query clause.")
    note: str


class JudgeScore(BaseModel):
    most_severe_defect_id: str = Field(description="From the defect list: the id that would do the most damage if left in. Empty for a solid draft.")
    ranked_first_in_must_fix: bool
    must_fix_order_defect_ids: list[str] = Field(description="Defect ids in the order the Judge's must-fix list addresses them; unknown items as 'other'.")
    verdict: str
    verdict_appropriate: bool = Field(description="Flawed draft: revise or no_go. Solid draft: go, or revise with only minor items.")
    unsupported_or_generic: list[Unsupported]
    note: str


class CaseScore(BaseModel):
    case: str
    roles: list[RoleScore]
    judge: JudgeScore
    overall_note: str


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def case_dir(case: str) -> Path:
    return HERE / "cases" / case


def defects_for(case: str) -> dict:
    return yaml.safe_load((HERE / "defects" / f"{case}.yaml").read_text(encoding="utf-8"))


def results_dir(rnd: str, case: str) -> Path:
    d = HERE / "results" / rnd / case
    d.mkdir(parents=True, exist_ok=True)
    return d


def all_cases() -> list[str]:
    return sorted(p.name for p in (HERE / "cases").iterdir() if p.is_dir())


def cfg_for(rnd: str, case: str):
    # Bundled defaults by default; a round can point at a roles dir via ROLES_ROOT (a config.yaml dir).
    import os
    root = Path(os.environ["ROLES_ROOT"]) if os.environ.get("ROLES_ROOT") else ASSETS
    return load_config(root, project=results_dir(rnd, case))


def session_dir(rnd: str, case: str) -> Path:
    t = json.loads((results_dir(rnd, case) / "timing.json").read_text())
    return Path(t["session_dir"])


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #


def cmd_prepare(args):
    cases = args.cases.split(",") if args.cases else all_cases()
    for case in cases:
        cd = case_dir(case)
        cfg = cfg_for(args.round, case)
        context = [str(cd / "queries")] + [str(DATA_DIR / f) for f in DATA_CONTEXT]
        sdir = init_session(cfg, mode_id="review", input_text=(cd / "draft.md").read_text(encoding="utf-8"),
                            worry=None, context_paths=context)
        rd = results_dir(args.round, case)
        (rd / "timing.json").write_text(json.dumps({"case": case, "round": args.round, "session_dir": str(sdir),
                                                     "started_at": datetime.now().isoformat(timespec="seconds"),
                                                     "started_monotonic": time.time(), "stages": {}}, indent=2))
        print(f"=== {case}")
        print(advance(cfg, sdir, until="judge").format())


def cmd_next(args):
    cfg = cfg_for(args.round, args.case)
    rd = results_dir(args.round, args.case)
    t = json.loads((rd / "timing.json").read_text())
    report = advance(cfg, session_dir(args.round, args.case), until="judge", skip=(args.skip or "").split(",") if args.skip else None)
    now = time.time()
    if report.done:
        t["finished_at"] = datetime.now().isoformat(timespec="seconds")
        t["seconds_total"] = round(now - t["started_monotonic"], 1)
    else:
        t["stages"][report.stage] = {"reached_at": round(now - t["started_monotonic"], 1)}
    (rd / "timing.json").write_text(json.dumps(t, indent=2))
    print(report.format())


def cmd_score(args):
    rd = results_dir(args.round, args.case)
    sdir = session_dir(args.round, args.case)
    s = load_session(sdir)
    defects = defects_for(args.case)
    outputs = {}
    if s.structure: outputs["coach_pre"] = s.structure.model_dump()
    if s.advocate: outputs["advocate"] = s.advocate.model_dump()
    if s.challenger: outputs["challenger"] = s.challenger.model_dump()
    for r in s.panel:
        outputs[r.role_id] = r.output.model_dump() if r.output else {"error": r.error}
    judge = s.judge.model_dump() if s.judge else {"error": s.errors.get("judge")}
    out_path = rd / "scores.json"
    prompt = f"""# Scoring task

You are an independent scorer for a review panel. You did NOT take part in the
review. Compare each role's output against the defect list and write one JSON
object to:

    {out_path}

It must validate against the SCHEMA at the end. Raw JSON only, no fences.

Rules:
- A defect counts as "caught" only if the role identifies the specific problem
  (not just the area). "partially" means the role pointed at the right place or
  symptom without naming the actual defect. Anything else is "missed".
- "unsupported_or_generic": concerns, challenges or questions that (a) could be
  pasted onto any other draft, (b) assert something the listed files contradict,
  or (c) ask for something the draft already provides. Quote them.
- Citations: count the role's distinct claims; how many name a specific file;
  how many name a file AND a line, slide, row, or query clause.
- Judge: identify the single most severe defect from the list (severity, then
  tier). Say whether the Judge's must-fix list puts it first, and map the
  must-fix items to defect ids in order.
- A solid draft has an empty defect list: then only unsupported items, citation
  quality and verdict appropriateness matter.
- You may open the case files under {case_dir(args.case)} and the data files
  under {DATA_DIR} to check a role's claim. Do not open anything else.

# Defect list (hidden from the panel)

```yaml
{yaml.safe_dump(defects, sort_keys=False, allow_unicode=True)}
```

# The draft the panel reviewed

{(case_dir(args.case) / "draft.md").read_text(encoding="utf-8")}

# Role outputs

"""
    for key, val in outputs.items():
        prompt += f"## {key}\n```json\n{json.dumps(val, indent=1, ensure_ascii=False)}\n```\n\n"
    prompt += f"## judge\n```json\n{json.dumps(judge, indent=1, ensure_ascii=False)}\n```\n\n"
    prompt += "# SCHEMA\n\n```json\n" + json.dumps(CaseScore.model_json_schema(), indent=1) + "\n```\n"
    (rd / "scoring.prompt.md").write_text(prompt, encoding="utf-8")
    print(rd / "scoring.prompt.md")
    print("expected output:", out_path)


def _load_scores(rnd: str) -> dict[str, CaseScore]:
    scores = {}
    for case in all_cases():
        p = HERE / "results" / rnd / case / "scores.json"
        if p.exists():
            try:
                scores[case] = CaseScore.model_validate_json(p.read_text(encoding="utf-8"))
            except ValidationError as e:
                print(f"INVALID {p}: {str(e)[:300]}", file=sys.stderr)
    return scores


def summarize_round(rnd: str) -> dict:
    scores = _load_scores(rnd)
    per_role: dict[str, dict] = {}
    cases_out = {}
    for case, cs in scores.items():
        defects = defects_for(case)
        ids = [d["id"] for d in defects.get("defects", [])]
        flawed = bool(ids)
        t = json.loads((HERE / "results" / rnd / case / "timing.json").read_text())
        cases_out[case] = {
            "flawed": flawed, "n_defects": len(ids), "seconds_total": t.get("seconds_total"),
            "judge": cs.judge.model_dump(),
        }
        for r in cs.roles:
            agg = per_role.setdefault(r.role_id, {"caught": 0, "partial": 0, "defects": 0, "unsupported": 0, "unsupported_good": 0,
                                                   "claims": 0, "cite_file": 0, "cite_line": 0, "caught_by_tier": {}, "missed_by_tier": {}})
            if flawed:
                agg["defects"] += len(ids)
                agg["caught"] += len(r.caught)
                agg["partial"] += len(r.partially)
                agg["unsupported"] += len(r.unsupported_or_generic)
                tier = {d["id"]: d["tier"] for d in defects["defects"]}
                for i in r.caught:
                    agg["caught_by_tier"][tier.get(i, "?")] = agg["caught_by_tier"].get(tier.get(i, "?"), 0) + 1
                for i in r.missed:
                    agg["missed_by_tier"][tier.get(i, "?")] = agg["missed_by_tier"].get(tier.get(i, "?"), 0) + 1
            else:
                agg["unsupported_good"] += len(r.unsupported_or_generic)
            agg["claims"] += r.claims_total
            agg["cite_file"] += r.claims_citing_file
            agg["cite_line"] += r.claims_citing_file_and_line
    for role, agg in per_role.items():
        agg["catch_rate"] = round((agg["caught"] + 0.5 * agg["partial"]) / agg["defects"], 2) if agg["defects"] else None
        agg["cite_line_rate"] = round(agg["cite_line"] / agg["claims"], 2) if agg["claims"] else None
    return {"round": rnd, "cases": cases_out, "roles": per_role}


def _table(summary: dict) -> str:
    lines = ["| role | catch rate | caught/partial/defects | unsupported (flawed) | unsupported (solid) | claims citing file+line |", "|---|---|---|---|---|---|"]
    for role in ROLE_KEYS:
        a = summary["roles"].get(role)
        if not a:
            continue
        lines.append(f"| {role} | {a['catch_rate']} | {a['caught']}/{a['partial']}/{a['defects']} | {a['unsupported']} | {a['unsupported_good']} | {a['cite_line']}/{a['claims']} ({a['cite_line_rate']}) |")
    lines.append("")
    lines.append("| case | defects | judge verdict | appropriate | most severe first | must-fix order | seconds |")
    lines.append("|---|---|---|---|---|---|---|")
    for case, c in summary["cases"].items():
        j = c["judge"]
        lines.append(f"| {case} | {c['n_defects']} | {j['verdict']} | {j['verdict_appropriate']} | {j['ranked_first_in_must_fix']} | {', '.join(j['must_fix_order_defect_ids'])} | {c['seconds_total']} |")
    return "\n".join(lines)


def cmd_summarize(args):
    summary = summarize_round(args.round)
    out = HERE / "results" / args.round
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    md = f"# Round {args.round}\n\n" + _table(summary) + "\n"
    (out / "summary.md").write_text(md)
    print(md)


def cmd_compare(args):
    a, b = summarize_round(args.round1), summarize_round(args.round2)
    lines = [f"| role | catch {args.round1} | catch {args.round2} | unsupported {args.round1} | unsupported {args.round2} | solid-draft unsupported {args.round1} → {args.round2} | cite file+line {args.round1} → {args.round2} |",
             "|---|---|---|---|---|---|---|"]
    for role in ROLE_KEYS:
        x, y = a["roles"].get(role, {}), b["roles"].get(role, {})
        if not x and not y:
            continue
        lines.append(f"| {role} | {x.get('catch_rate')} | {y.get('catch_rate')} | {x.get('unsupported')} | {y.get('unsupported')} | {x.get('unsupported_good')} → {y.get('unsupported_good')} | {x.get('cite_line_rate')} → {y.get('cite_line_rate')} |")
    lines.append("")
    lines.append(f"| case | verdict {args.round1} → {args.round2} | appropriate | most severe first | seconds |")
    lines.append("|---|---|---|---|---|")
    for case in sorted(set(a["cases"]) | set(b["cases"])):
        ca, cb = a["cases"].get(case, {}).get("judge", {}), b["cases"].get(case, {}).get("judge", {})
        lines.append(f"| {case} | {ca.get('verdict')} → {cb.get('verdict')} | {ca.get('verdict_appropriate')} → {cb.get('verdict_appropriate')} | {ca.get('ranked_first_in_must_fix')} → {cb.get('ranked_first_in_must_fix')} | {a['cases'].get(case, {}).get('seconds_total')} → {b['cases'].get(case, {}).get('seconds_total')} |")
    md = "\n".join(lines)
    (HERE / "results" / f"compare_{args.round1}_{args.round2}.md").write_text(md + "\n")
    print(md)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("prepare"); a.add_argument("round"); a.add_argument("--cases"); a.set_defaults(func=cmd_prepare)
    a = sub.add_parser("next"); a.add_argument("round"); a.add_argument("case"); a.add_argument("--skip"); a.set_defaults(func=cmd_next)
    a = sub.add_parser("score"); a.add_argument("round"); a.add_argument("case"); a.set_defaults(func=cmd_score)
    a = sub.add_parser("summarize"); a.add_argument("round"); a.set_defaults(func=cmd_summarize)
    a = sub.add_parser("compare"); a.add_argument("round1"); a.add_argument("round2"); a.set_defaults(func=cmd_compare)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
