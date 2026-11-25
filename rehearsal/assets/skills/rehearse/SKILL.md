---
name: rehearse
description: Run the Rehearsal Room panel on a deck outline, memo, problem statement, analysis plan, work-in-progress analysis or set of options, with the roles able to read the project's files. Use when the user asks to rehearse, stress-test, review, pre-read, grade or "put on trial" something they are working on, or types /rehearse. Also handles the post-meeting debrief.
---

# /rehearse

You are the orchestrator of the Rehearsal Room. You do not play the roles. The
`rehearsal` package writes one prompt file per role; you run each prompt in
its own subagent so the roles stay independent; the package validates the JSON
each subagent writes, advances the stage, and renders the report. No API key:
the subagents are the model.

## 0. Make sure the tool is available

```bash
python -c "import rehearsal" 2>/dev/null || pip install -q "git+https://github.com/DonaldJasper0621/Claude_Court_multi_discussion"
python -m rehearsal.cli where
```

`where` shows which config is in use. If it says "bundled defaults" and this
project should have its own tuned panel and profile, run
`python -m rehearsal.cli init` once (creates `.rehearsal/` and this skill in
`.claude/skills/`; commit both).

## 1. Collect the inputs

- **Mode**: `framing`, `method`, `preread`, `stakeholder`, `decide`,
  `review` (analysis in progress), or `grade` (practice scenario with a
  sealed answer key). If the user did not name one, infer it and say which in
  one line: a deck or memo about to go out is `preread`; a problem statement is
  `framing`; an analysis plan is `method`; findings and queries still being
  worked on are `review`; a choice between options is `decide`; a diagnosis
  of a practice scenario is `grade`.
- **Material**: a file path, or text pasted in chat. If pasted, write it to
  `.rehearsal/inbox/<YYYYMMDD-HHMMSS>.md` first. Do not edit it.
- **Context** (the point of running inside a project): the files and
  directories the roles may open to check the work. Default to the project's
  analysis, docs and data-dictionary files relevant to the material; ask only
  if the project has no obvious candidates. Pass each as `-c path`. Roles read
  these with their own tools; you never paste file contents into prompts.
- **Worry** (optional): what the user is most nervous about.
- **Panel override** (optional): `--panel a,b,c` replaces, `--add x,y` adds.
  Role ids: `python -m rehearsal.cli roles`.
- **Answer key** (`grade` mode only): the sealed `.b64` file under
  `.rehearsal/scenarios/<name>/`. Pass `--answer-key <path>`. Never open,
  decode or quote it yourself; only the Judge's prompt carries it.
- **Language**: English by default. `--language zh-TW` only if asked.

If the material or context looks like real customer data, real figures tied to
a named program, or verbatim internal documents, stop and ask the user to
de-identify first. Synthetic practice data is fine.

## 2. Start the session

```bash
python -m rehearsal.cli stage init -m <mode> -i <material> [-c <path>]... [-w "<worry>"] [--answer-key <path>]
```

Output: `SESSION <dir>`, then `STAGE <name>: N pending` with one line per role:
`key | role name | prompt=<file> | output=<file>`.

## 3. Run every pending role in parallel subagents

Spawn one `general-purpose` Agent per pending line, all in the same message:

```
Read the file <prompt path> in full. It contains your role, the material to
review, a list of project files you may open, and a JSON schema. Follow its
instructions exactly: read the project files your perspective needs, then
write a single raw JSON object that validates against the schema to
<output path>. Do not read anything outside the listed project files. Do not
reply with the content in chat; the file is the output. When the file is
written, reply only with the word DONE.
```

Never summarize the prompt file for the agent and never show one agent
another agent's output. Wait for all agents of a stage before continuing.

## 4. Advance

```bash
python -m rehearsal.cli stage next <session dir>
```

- `INVALID: <reason>` on a line: spawn that role again with the same prompt
  plus "A previous attempt was rejected: <reason>. Fix it and overwrite the
  file." Two retries at most, then `--skip <key>` and tell the user.
- A new `STAGE`: back to step 3.
- `DONE` and `REPORT <path>`: step 5.

Stages: `coach_pre` (1) → `panel` (advocate, challenger, panelists) →
`judge` (1) → `coach_post` (1; skipped in `grade` mode).

## 5. Deliver

1. Send `<session dir>/report.html` with SendUserFile, `display: "render"`.
2. In chat, in the user's language, the two-minute version: verdict and
   headline (or score and headline in `grade` mode); must-fix list; the likely
   questions with one-line suggested answers; the one dissent or blind spot
   that matters most. Keep questions and answers in English.
3. In `review` mode, also list what the panel checked in the project files and
   what they found there; that is the value of running in-project.
4. Mention the session id for a later debrief.

## 6. Follow-ups in the same conversation

- **Ask one role**: spawn one agent with that role's prompt file from the
  `panel` stage plus the question under a `# Follow-up` heading; ask it to
  answer in chat (not JSON), still allowed to read the listed files.
- **Re-run on revised work**: new session (step 2); then compare the two
  Judge outputs: verdict change, must-fix items cleared, questions that
  disappeared or appeared.

## 7. Debrief after the real meeting (not for practice scenarios)

1. `python -m rehearsal.cli sessions` to find the session.
2. Show the likely questions numbered from 0; ask which were asked, what was
   asked that was not predicted (and by whom), the outcome, anything to keep.
3. Write `{"outcome_in_room": "...", "asked": [0, 2], "unpredicted": ["..."], "notes": "..."}`
   to a scratch file and run `python -m rehearsal.cli debrief <session> --from <file>`.
4. Offer to fold durable facts about the manager, Director or a stakeholder
   into `.rehearsal/profile/workplace.md`; commit the profile files.

## Notes

- `.rehearsal/sessions/` is git-ignored; never commit it. Everything else under
  `.rehearsal/` (config, roles, profile, sealed scenario keys) is meant to be
  committed so the panel travels with the project.
- A role that sounds wrong is fixed in `.rehearsal/roles/<layer>/<id>.md`.
- Practice scenarios are created with `/scenario`; they put the sealed key in
  `.rehearsal/scenarios/<name>/answer_key.md.b64`.
