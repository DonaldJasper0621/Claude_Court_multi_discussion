# Rehearsal Room — Design

A personal pre-meeting rehearsal tool for a Business Analyst. Before a deck, memo,
or recommendation goes to leadership, a panel of simulated stakeholders reads it
independently, an Advocate and a Challenger argue over it, a Coach restructures
it, and a Judge turns everything into a pre-meeting brief: what to fix, what you
will be asked, and how to answer.

It is an adaptation of the "Claude Court" idea (prosecution, defense, 12 jurors,
judge) to real workplace decisions. The courtroom mechanics are kept where they
help (independent reviewers, forced disagreement, a synthesizer) and dropped where
they do not (binary guilty / not-guilty verdicts, entertainment framing).

## 1. The problem this solves

A BA's output is "analysis + recommendation + persuading a decision maker". The
quality of that output is usually decided in one room: the meeting where the deck
goes to a Director or VP. The common ways that meeting goes badly are not analysis
errors. They are:

| Failure | What it looks like |
|---|---|
| Wrong problem framed | Two weeks of work answering a question nobody was asking |
| No answer first | Lots of data, no "so what", gets interrupted on slide 3 |
| Methodology punctured live | Wrong denominator, seasonality not controlled, selection bias in a test, sizing baseline questioned |
| A stakeholder missed | Risk, Compliance, Tech or Ops says "this can't ship" at the last minute |
| Questions not anticipated | "I'll get back to you" on something that was predictable |

All five are predictable before the meeting. The tool's job is to predict them.

## 2. What it is not

- Not a verdict machine. Workplace questions are rarely binary. The Judge outputs
  `go / revise / no_go` plus a brief, not guilty / not guilty.
- Not a replacement for the real stakeholders. It is a rehearsal, calibrated over
  time against what real people actually asked.
- Not a place for confidential data. Inputs are de-identified structure, logic
  and assumptions. Real customer data, actual figures and verbatim internal
  documents stay out. The tool tests reasoning and persuasion, not the numbers.

## 3. Role architecture

Two layers. The mechanism layer is fixed and always present. The panel layer is
configurable per run.

### 3.1 Mechanism layer (always present)

| Role | Job | When it runs |
|---|---|---|
| **Coach** (Structure & Communication) | Decompose the input into an issue tree, check MECE, find logic breaks, check answer-first. After the Judge: propose a restructured storyline. | Pre-pass before the panel; post-pass after the Judge |
| **Advocate** | Build the strongest honest case for the material. Surface strengths the author under-sold. | Parallel with panel |
| **Challenger** | Find the holes: assumptions, data, logic, timeline, politics. | Parallel with panel |
| **Judge** (Chief of Staff) | Read everything. Produce the pre-meeting brief. | After all of the above |

The Coach runs before the panel so that panelists react to a structurally clear
version of the argument, not to the author's phrasing. The Coach's structure
analysis is appended to the material every panelist sees.

### 3.2 Panel layer (configurable)

Roles are defined by what the person cares about, not by title. Each has a
persona file in `roles/panel/` with: identity, what they care about, how they
behave in meetings, what they never let slide, and anti-patterns to avoid
(generic advice, framework-dropping, hedging).

| Role id | Cares about | The kind of question they ask |
|---|---|---|
| `senior_manager` | Scope alignment, timeline, whether this will embarrass them upward | "Is this the scope we aligned on last week?" |
| `director` | Answer first, size of prize, risk, what decision is being asked of them | "If this were one page, what should I remember?" |
| `methodology_reviewer` | Denominators, samples, confounders, metric definitions, test design | "Did the lift control for seasonality? How was control selected?" |
| `risk_compliance` | Fair lending / UDAAP, model risk, controls, well-managed, documentation | "Does this segmentation have disparate-impact exposure?" |
| `tech_product` | Feasibility, data availability, dependencies, build time | "That field doesn't exist today. Did you know?" |
| `finance` | Incrementality, NPV, cost, sizing assumptions | "Which year is the baseline for this sizing?" |
| `customer` | Whether this actually helps, or adds friction | "So what will I notice?" |
| `strategy_partner` | Market sizing, entry, growth levers, competitive response | "Which growth lever did you leave out, and why?" |
| `ops` (optional) | Implementation reality, process change, frontline impact | "Who handles the exception queue this creates?" |
| `cross_lob_ba` (optional) | Institutional memory, "we tried this in 2023" | "How does this relate to what Auto did last quarter?" |

The `cross_lob_ba` role is only useful once the workplace profile has history in
it. It is off by default.

### 3.3 Why the Consultant is split in two

A "consultant" role covers two different jobs with different usage frequency:

- **Structure & communication** (issue tree, MECE, Pyramid Principle / SCQA,
  hypothesis-driven, answer-first, driver tree, 80/20, ghost deck, so-what
  ladder). Used on almost every deliverable. This is the **Coach**, in the
  mechanism layer.
- **Strategy & market** (market sizing with top-down / bottom-up triangulation,
  market entry, growth strategy, Porter, Ansoff, 7S, 4P/4C, unit economics).
  Situational. This is `strategy_partner`, in the panel layer.

Both carry a hard rule against framework theater: a framework is used only when
it changes the answer, at most one or two per response, with the reason stated.

## 4. Output contracts

Panelists do not vote. Each returns a fixed structure that doubles as a prep
checklist:

```
one_line_reaction
stance: supportive | neutral | skeptical | blocking
top_concerns[1..2]: { concern, where_in_material, severity }
the_question            # the one thing they would say aloud in the meeting
what_would_make_me_say_yes
```

The Judge's brief:

```
verdict: go | revise | no_go
headline                 # one sentence, answer first
must_fix_before_sending[]
likely_questions[]: { question, asked_by, why_they_ask, suggested_answer }
consensus[]
dissent[]: { topic, positions, root_cause }
blind_spots[]            # things nobody on the panel raised but should have
next_steps[]
```

The Coach's post-pass:

```
one_line_restatement     # the whole argument in one sentence
opening_scqa             # situation, complication, question, answer
recommended_storyline[]: { title, key_message, why_here }
changes_from_original[]
so_what_ladder[]         # finding -> so what -> so what -> implication
```

All outputs are produced via structured outputs (`messages.parse` with Pydantic
models), so the report renderer never parses free text.

## 5. Modes

One panel, five entry points matching the stages of a BA project.

| Mode | When | Default panel | Emphasis |
|---|---|---|---|
| `framing` | Project start, before analysis | director, senior_manager, strategy_partner, methodology_reviewer, customer | Is this the right problem? What would each person say the real problem is? |
| `method` | Analysis design | methodology_reviewer, finance, risk_compliance, tech_product, senior_manager | Will the approach survive scrutiny? |
| `preread` | Before a deck or memo goes out | director, senior_manager, methodology_reviewer, risk_compliance, finance, tech_product, customer | Full rehearsal. Highest-value mode. |
| `stakeholder` | Before a meeting with one function | risk_compliance, tech_product, finance, ops (override with `--panel`) | Predict objections and how to handle them |
| `decide` | Choosing between options | director, senior_manager, finance, strategy_partner, methodology_reviewer, tech_product | Judge must pick and state trade-offs |

Modes live in `modes.yaml`. Each mode carries an `emphasis` paragraph injected
into every role's prompt and a `judge_focus` paragraph for the Judge.

## 6. Run flow

```
input (markdown) + mode + optional worry + optional panel override
        │
        ▼
 1. Coach pre-pass ──────────► structure_analysis
        │
        ▼
 2. In parallel (independent, no shared outputs):
        Advocate  Challenger  Panelist₁ … Panelistₙ
        │
        ▼
 3. Judge ◄── all of the above ───► brief
        │
        ▼
 4. Coach post-pass ◄── input + brief ───► storyline
        │
        ▼
 5. Persist session (JSON) + render HTML report + open browser
```

Independence in step 2 is the point. Panelists never see each other's output,
which prevents the panel from collapsing into one opinion.

## 7. Workplace profile and calibration loop

Two things make this a work tool rather than a toy.

**Workplace profile** (`profile/workplace.md`). A file the user maintains: line
of business, manager's style, recurring stakeholders and their historical
positions, company norms (answer first, one-pagers, well-managed), past feedback
received. Every role reads it. The Director is not a generic Director; it asks
what this user's boss actually asks.

**Debrief log** (`profile/debrief_log.md`). After the real meeting, the user
marks which predicted questions were actually asked and records questions that
were not predicted. Both are appended to the log, which every role also reads.
Three months of this makes the panel sharper than any generic prompt.

`rehearse debrief <session>` drives this interactively in v1.

## 8. Interface plan

**v1 (this build).** Python CLI. Output is a self-contained HTML report opened in
the browser. The HTML gives most of the reading experience (cards, collapsible
sections, Judge brief up front). Purpose: test role quality against real,
de-identified cases and iterate on prompts.

**v2.** Local web app (FastAPI + plain HTML/JS or Streamlit). Adds: follow-up
question to a single role, v1 vs v2 comparison of a revised input, interactive
debrief, profile editor. Not built until the roles produce questions that sound
like the user's actual stakeholders.

The frontend is deliberately second. The asset is the role prompts.

## 9. Technical choices

- Python 3.11+, `anthropic` SDK, `pydantic`, `pyyaml`, `jinja2`.
- `AsyncAnthropic` with `asyncio.gather` and a concurrency semaphore for the
  panel. Structured outputs via `messages.parse`.
- Default model `claude-opus-5-5` for every role; Judge and Coach at
  `effort: high`, panel at `effort: medium`. Overridable in `config.yaml`.
- Stable content (role persona, protocol, profile) goes in the `system` block
  with `cache_control`, so repeated runs on a revised deck reuse the cached
  prefix. Volatile content (the material, the worry) goes in the user turn.
- `stop_reason == "refusal"` is handled explicitly per call rather than via
  server-side fallbacks, so the helper-based `parse` path stays simple.
- A mock backend (`--mock`) produces schema-valid placeholder output so the
  pipeline and report can be exercised without an API key.
- Everything persists as local files. Sessions in `sessions/` (git-ignored),
  profile and roles in git.

## 10. Repository layout

```
DESIGN.md
README.md
config.yaml                 models, effort, concurrency, output language
modes.yaml                  the five modes
roles/
  mechanism/                advocate, challenger, coach, judge
  panel/                    one file per panelist
profile/
  workplace.md              user-maintained context (template provided)
  debrief_log.md            appended by `rehearse debrief`
rehearsal/                  the package
  cli.py  config.py  engine.py  llm.py  schemas.py  report.py  debrief.py
  templates/report.html.j2
examples/                   de-identified sample inputs
sessions/                   run outputs (git-ignored)
tests/
```

## 11. Open questions for v2

- Whether to extract text from `.pptx` directly, and how to strip numbers
  automatically when doing so.
- Whether follow-up questions to a single role should carry the full panel
  context or only that role's own prior output.
- Whether to weight panel roles per mode (e.g. methodology_reviewer counts more
  in `method`) in the Judge's synthesis, or leave weighting to the Judge's
  judgment.
