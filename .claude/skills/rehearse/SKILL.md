---
name: rehearse
description: Run the pre-meeting rehearsal panel on a deck outline, memo, problem statement, analysis plan or set of options. Use when the user asks to rehearse, stress-test, pre-read, review or "put on trial" something they are about to take into a meeting, or types /rehearse. Also handles the post-meeting debrief.
---

# /rehearse

You are the orchestrator of the Rehearsal Room in this repository. You do not
play the roles yourself. The Python package writes one prompt file per role;
you run each prompt in its own subagent so the roles stay independent; the
package validates the JSON each subagent writes, advances the stage, and
renders the report. No API key is involved: the subagents are the model.

Read `DESIGN.md` only if you need background. The procedure below is complete.

## 1. Collect the inputs

- **Mode**: one of `framing`, `method`, `preread`, `stakeholder`, `decide`.
  If the user did not name one, infer it: a deck or memo about to go out is
  `preread`; a problem statement at project start is `framing`; an analysis
  plan is `method`; a meeting with one function is `stakeholder`; a choice
  between options is `decide`. Say which mode you picked and why in one line.
- **Material**: a file path the user gave, or text pasted in chat. If pasted,
  write it to `sessions/inbox/<YYYYMMDD-HHMMSS>.md` first. Do not edit it.
- **Worry** (optional): what the user is most nervous about, one sentence.
- **Panel override** (optional): `--panel a,b,c` replaces the default panel,
  `--add x,y` adds to it. Role ids: `python -m rehearsal.cli roles`.
- **Language**: the report defaults to English (meetings are in English).
  Pass `--language zh-TW` only if the user asks for Chinese output.

If the material contains what looks like real customer data, real dollar
figures tied to a named program, or verbatim internal documents, stop and ask
the user to replace them with placeholders before you run. This is a hard rule.

## 2. Make sure the package is importable

```bash
python -c "import rehearsal" 2>/dev/null || pip install -q -e .
```

## 3. Start the session

```bash
python -m rehearsal.cli stage init -m <mode> -i <path> [-w "<worry>"] [--panel ...] [--add ...]
```

The output lists `SESSION <dir>` and `STAGE <name>: N pending`, with one line
per pending role: `key | role name | prompt=<file> | output=<file>`.

## 4. Run every pending role in parallel subagents

For every pending line, spawn one `general-purpose` Agent in the same
message so they run concurrently. Use this prompt, substituting the paths:

```
Read the file <prompt path> in full. It contains your role, the material to
review, and a JSON schema. Follow its instructions exactly: write a single raw
JSON object that validates against the schema to <output path>. Do not read
any other file. Do not reply with the content in chat; the file is the output.
When the file is written, reply only with the word DONE.
```

Do not summarize, paraphrase or pre-digest the prompt file for the agent, and
never show one agent another agent's output. Independence is the point.

Wait for all agents of the stage to finish before continuing. If an agent
reports failure, spawn it again once with the same prompt.

## 5. Advance

```bash
python -m rehearsal.cli stage next <session dir>
```

- If a line ends with `INVALID: <reason>`, the JSON did not validate. Spawn
  that role again with the same prompt plus: "A previous attempt was rejected:
  <reason>. Fix it and overwrite the file." At most two retries; then advance
  with `--skip <key>` and tell the user that role is missing from the report.
- If a new `STAGE` is listed, go back to step 4.
- When the output says `DONE` and `REPORT <path>`, go to step 6.

The stages run in this order: `coach_pre` (1 role), `panel` (advocate,
challenger and the panelists, typically 7 to 10 roles), `judge` (1),
`coach_post` (1). A full run is four rounds.

## 6. Deliver

1. Send `<session dir>/report.html` to the user with SendUserFile,
   `display: "render"`. It is self-contained.
2. In chat, in the user's language, give: the verdict and headline; the
   must-fix list; the likely questions as a short list of question and
   one-line suggested answer; and the one dissent or blind spot that matters
   most. Keep questions and answers in English so they are ready to use.
3. Tell the user the session id so they can debrief later.

Do not pad the chat summary with everything in the report. The report is the
full deliverable; the chat is the two-minute version.

## 7. Follow-ups in the same conversation

- **Ask one role a follow-up** ("what would Finance say if I changed the
  baseline?"): spawn one agent with that role's prompt file from the `panel`
  stage, plus the user's follow-up appended under a `# Follow-up` heading, and
  ask it to answer in chat (not JSON). Relay the answer.
- **Re-run on a revised version**: start a new session (step 3) and, when it
  is done, compare the two Judge briefs for the user: verdict change, which
  must-fix items cleared, which questions disappeared or appeared.

## 8. Debrief after the real meeting

When the user comes back after the meeting (or types `/rehearse debrief`):

1. Find the session: `python -m rehearsal.cli sessions`.
2. Show the Judge's likely questions numbered from 0 and ask which were
   actually asked, what was asked that was not predicted (and by whom), the
   outcome in the room, and anything worth remembering.
3. Write the answers to a JSON file in the scratchpad:
   `{"outcome_in_room": "...", "asked": [0, 2], "unpredicted": ["..."], "notes": "..."}`
4. Run `python -m rehearsal.cli debrief <session id> --from <json path>`.
   This appends to `profile/debrief_log.md`, which every role reads next time.
5. If the user volunteers something durable about their manager, Director or
   a stakeholder, offer to add it to `profile/workplace.md` under the matching
   section, and do so if they agree. Then commit both profile files.

## Notes

- `sessions/` is git-ignored because it holds work material. Never commit it.
- Roles live in `roles/` as Markdown. If the user says a role sounds wrong
  ("the Director would never ask that"), edit that role file, not the code.
- `python -m rehearsal.cli run` is the direct-API path and needs
  `ANTHROPIC_API_KEY`. Do not use it from this skill.
