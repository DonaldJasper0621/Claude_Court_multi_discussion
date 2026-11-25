---
name: scenario
description: Create a practice scenario for a Business Analyst inside the current project: a business brief, synthetic data with planted causes and red herrings, a data dictionary, and a sealed answer key that only the Rehearsal Room's Judge may read. Use when the user wants to practise diagnosing a trend, build a training case, or types /scenario.
---

# /scenario

You build a realistic analytical exercise that the user then works through as
if it were a real assignment, and that `/rehearse grade` can mark against a
sealed key. The user must be able to do real work on it: write a problem
statement, define metrics, write queries against the data, find the drivers,
and recommend actions.

## 1. Agree the case in one exchange

Ask, or infer from the request, and confirm in one short message:

- **Business and metric**: e.g. co-brand card 30+ DPD rate, card acquisition
  conversion, auto loan early payment defaults, deposit attrition.
- **What leadership sees**: the headline trend and the window (e.g. "up 1.2
  points over six months").
- **Difficulty**: `starter` (2 causes, 1 trap), `standard` (3 causes, 2 traps),
  `hard` (4 causes, 3 traps, one interaction between causes).
- **Scenario name**: short snake_case, e.g. `cobrand_delinquency`.

Then proceed. Do not wait for more confirmation.

## 2. Design the truth before the data

Write, for yourself, the answer key first. It must contain:

- The **planted causes**, each with mechanism, affected population, timing,
  and rough share of the headline movement. Mix types: a vintage or mix shift,
  a policy or program change, an operational failure, a seasonal or macro
  effect.
- The **traps**: at least one metric-definition trap (a denominator or
  definition change in the published KPI), and one or two red herrings that
  look causal and are not.
- The **model answer**: the diagnosis a strong analyst would write, the metric
  definitions they would use, and the query or cut that reveals each cause.
- **Recommended actions** a Director would accept.

Causes must be discoverable from the data with reasonable cuts (vintage,
channel, segment, month, flags). Nothing should require information that is
not in the files.

## 3. Generate the project files

Inside the current project (run `python -m rehearsal.cli init` first if there
is no `.rehearsal/`), create:

```
docs/<scenario>/brief.md            the ask as the Director would send it; what the KPI report shows
data/<scenario>/*.csv               the synthetic tables (accounts, monthly performance, campaigns, KPI report as published, ops notes)
data/<scenario>/data_dictionary.md  every column, its definition, and any definition changes with effective dates
.rehearsal/scenarios/<scenario>/answer_key.md.b64   the answer key, base64 encoded
.rehearsal/scenarios/<scenario>/generator.py.b64    the generator script, base64 encoded
.rehearsal/scenarios/<scenario>/README.md           what is sealed here and that the user should not open it
```

Write the generator as a deterministic Python script (fixed seed, numpy and
pandas) that writes the CSVs, run it, and check the headline trend actually
appears in the published KPI series and that each planted cause is visible
in the right cut (print a few diagnostic aggregates while generating). Keep
the data small enough for git: a few thousand accounts, 12 to 18 months,
under 10 MB total. Then base64 the script and the key into the sealed
directory and delete the plain copies. The data dictionary and the ops notes
may contain the clues a diligent analyst would find in real life (a line in a
changelog, a definition footnote); the answer key must not be inferable from
file names or column names.

Add a short section to the project's `CLAUDE.md` (create it if missing):
the scenario name, where the brief and data are, and the rule that nothing
under `.rehearsal/scenarios/` is to be opened, decoded or summarized by
Claude except through `/rehearse grade`.

## 4. Hand over

Tell the user, in their language: the brief in two sentences, where the files
are, the difficulty, and how the exercise works: do the analysis in
`analysis/<scenario>/`, write the diagnosis and recommendation to
`docs/<scenario>/diagnosis.md`, run `/rehearse review` along the way with the
analysis files as context, and `/rehearse grade docs/<scenario>/diagnosis.md
--answer-key .rehearsal/scenarios/<scenario>/answer_key.md.b64` at the end.

Do not reveal any cause, trap or hint. Do not paste any part of the answer
key into chat, commit messages or file names.
