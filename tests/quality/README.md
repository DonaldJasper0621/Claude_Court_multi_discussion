# Quality test set for the review panel

Measures whether the panel catches known defects, how much of what it says is
unsupported, and whether the Judge ranks the worst problem first.

## Cases

| case | kind | what it tests |
|---|---|---|
| `flawed_definitions` | flawed draft | definition and denominator errors, a SQL bug, a seasoning/vintage misread |
| `flawed_causality` | flawed draft | correlation read as cause, a join/aggregation error, a card-business misjudgment |
| `solid_draft` | sound draft | whether the panel invents problems when there are none |

Each case has `draft.md` and `queries/*.sql` under `cases/<case>/` (what the
panel sees) and a defect list under `defects/<case>.yaml` (what the panel must
never see). Defects carry a tier:

- `obvious`: visible from the draft alone.
- `needs_files`: visible only by opening the SQL or the data.
- `needs_domain`: visible only with card-business knowledge.

Drafts were written by subagents that could not read the role definitions.
During a run the roles may read only the case files and the practice data.

## Running a round

```bash
python tests/quality/run_quality.py prepare r1          # stages all cases, prints pending roles
# orchestrator plays each pending role in a subagent, then per case:
python tests/quality/run_quality.py next r1 <case>      # repeat per stage until DONE (stops after the Judge)
python tests/quality/run_quality.py score r1 <case>     # writes scoring.prompt.md; an independent scorer writes scores.json
python tests/quality/run_quality.py summarize r1
python tests/quality/run_quality.py compare r1 r2
```

`ROLES_ROOT=<dir with config.yaml>` points a round at a different set of
role files; by default the bundled defaults in `rehearsal/assets` are used.

Results live under `results/<round>/` and are committed, so rounds can be
compared later.
