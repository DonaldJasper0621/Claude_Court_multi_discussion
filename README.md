# Rehearsal Room

A pre-meeting rehearsal tool for a Business Analyst. Before a deck, memo or
recommendation goes to leadership, a panel of simulated stakeholders reads it
independently, an Advocate and a Challenger argue over it, a Coach restructures
it, and a Judge turns everything into a pre-meeting brief: what to fix, what
you will be asked, and how to answer.

Design rationale, role architecture and the v2 plan are in [DESIGN.md](DESIGN.md).

## Install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

Credentials: set `ANTHROPIC_API_KEY`, or run `ant auth login` if you have the
Anthropic CLI. The client reads either automatically.

## First run

```bash
# Check the pipeline and the report layout without calling the model
rehearse run -m preread -i examples/sample_preread.md --mock

# Real run on the sample
rehearse run -m preread -i examples/sample_preread.md \
  -w "Finance will question the sizing baseline"
```

The report opens in your browser. The session is saved under `sessions/`.

## Everyday use

```bash
rehearse modes                      # the five modes and their default panels
rehearse roles                      # every role you can put on the panel

rehearse run -m framing   -i problem.md
rehearse run -m method    -i approach.md
rehearse run -m preread   -i deck_outline.md -w "slide 6 sizing"
rehearse run -m stakeholder -i ask.md -p risk_compliance,ops
rehearse run -m decide    -i options.md --add strategy_partner

rehearse sessions                   # list past runs
rehearse debrief 20261105-191849-preread   # after the real meeting
rehearse profile                    # path of the workplace profile to edit
```

`-p/--panel` replaces the mode's default panel. `-a/--add` adds to it.
`--language zh-TW` switches the output language for one run.

## What makes it yours

Two files, both read by every role on every run:

- `profile/workplace.md`: your line of business, your manager's style, the
  Director's habits, recurring stakeholders, past feedback. Fill it in. The
  more specific it is, the less generic the panel sounds.
- `profile/debrief_log.md`: appended by `rehearse debrief` after real
  meetings. Which predicted questions were asked, which were missed. This is
  the calibration loop.

Roles live in `roles/` as Markdown with a small YAML header. Edit them freely;
no code changes needed. Modes live in `modes.yaml`.

## Input format

Plain Markdown or text. For a deck, paste slide titles and key messages. Use
placeholders such as `[X]`, `[N]`, `[$M]` for real figures; the roles are told
to treat them as present and to ask about provenance, not about the blank.

**Keep it de-identified.** No customer data, no actual figures, no verbatim
internal documents. The tool tests reasoning and persuasion, not the numbers.
Check your employer's policy on external AI tools before using work material.

## Configuration

`config.yaml` sets models, effort levels, concurrency and output language.
Defaults: `claude-opus-5-5` for every role, `effort: high` for Judge and
Coach, `medium` for the panel. A full `preread` run is about a dozen calls.

## Layout

```
DESIGN.md            why it is built this way
config.yaml          models, effort, paths
modes.yaml           the five modes
roles/mechanism/     coach, advocate, challenger, judge
roles/panel/         senior_manager, director, methodology_reviewer, risk_compliance,
                     tech_product, finance, customer, strategy_partner, ops, cross_lob_ba
profile/             workplace.md (yours), debrief_log.md (appended)
rehearsal/           the package: cli, config, engine, llm, schemas, report, debrief
examples/            de-identified sample input
sessions/            run outputs (git-ignored)
tests/               pytest, mock backend, no network
```

## Tests

```bash
pytest
```
