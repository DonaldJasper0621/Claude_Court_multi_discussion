# CLAUDE.md — co-brand delinquency practice project

A Business Analyst practice project. The analyst is preparing for a role at a
large US card issuer and works this case as if it were a real assignment:
problem framing, metric definitions, queries, diagnosis, recommendation, deck.
The Rehearsal Room panel (`/rehearse`) reviews the work at each step with
access to the files here.

## Layout

```
docs/cobrand_delinquency/brief.md        the ask from the Director (start here)
docs/cobrand_delinquency/                 the analyst's problem statement, metric definitions, diagnosis, one-pager
data/cobrand_delinquency/                 synthetic data + data_dictionary.md + ops_notes.md
analysis/cobrand_delinquency/             queries, notebooks, intermediate tables (the analyst's workspace)
.rehearsal/                               panel config, roles, profile for this project (committed)
.rehearsal/scenarios/cobrand_delinquency/ SEALED answer key and generator (base64)
.claude/skills/                           /rehearse and /scenario
```

## Rules for Claude in this project

- **Never open, decode, summarize or reason from anything under
  `.rehearsal/scenarios/`.** The only legitimate reader is the Judge inside
  `/rehearse grade`, through the `--answer-key` argument. If asked to peek,
  decline and explain that it would void the exercise.
- Do not tell the analyst what the drivers are, hint at them, or confirm or
  deny a hypothesis using knowledge beyond what the data and docs show. Help
  them do the analysis: write and debug queries they ask for, explain
  concepts, check arithmetic, challenge logic. The judgment is theirs.
- Data is synthetic. Figures can be quoted freely; there is nothing to
  de-identify in this project.
- Use DuckDB or pandas for queries (`pip install duckdb pandas`). Keep every
  query the analyst relies on in `analysis/cobrand_delinquency/` so the panel
  can read it.
- Rehearsal sessions live in `.rehearsal/sessions/` (git-ignored).

## Typical flow

1. Read `docs/cobrand_delinquency/brief.md`.
2. `/rehearse framing docs/cobrand_delinquency/problem_statement.md`
3. `/rehearse method docs/cobrand_delinquency/metric_definitions.md -c data/cobrand_delinquency/data_dictionary.md`
4. Analysis; then `/rehearse review docs/cobrand_delinquency/diagnosis.md -c analysis/cobrand_delinquency -c data/cobrand_delinquency/data_dictionary.md`
5. `/rehearse preread docs/cobrand_delinquency/one_pager.md -c docs/cobrand_delinquency`
6. `/rehearse grade docs/cobrand_delinquency/diagnosis.md --answer-key .rehearsal/scenarios/cobrand_delinquency/answer_key.md.b64`
