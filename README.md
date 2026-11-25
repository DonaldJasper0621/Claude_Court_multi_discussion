# Rehearsal Room

A pre-meeting rehearsal panel for a Business Analyst, built to live inside the
projects you work on. A Coach maps your argument, an Advocate and a Challenger
argue it, simulated stakeholders read it independently and can open your
project's files to check the work, and a Judge turns everything into a brief:
what to fix, what you will be asked, how to answer. For practice cases, the
Judge also grades your diagnosis against a sealed answer key.

Why it is built this way: [docs/DESIGN.md](docs/DESIGN.md).

## Install on any machine

```bash
pip install "git+https://github.com/DonaldJasper0621/Claude_Court_multi_discussion"
rehearse install-skills        # /rehearse and /scenario in every Claude Code project on this machine
```

Then, inside any project you want the panel to know about:

```bash
cd my-project
rehearse init                  # creates .rehearsal/ (config, roles, profile) and .claude/skills/
claude                         # open Claude Code here; type /rehearse
```

Commit `.rehearsal/` (except `sessions/`, already git-ignored) and
`.claude/skills/` so the tuned panel travels with the project to any machine.
No API key is needed for the Claude Code path; the roles run as subagents on
your Claude subscription.

## Using it inside a project

| You want to | Type in Claude Code |
|---|---|
| Check you are solving the right problem | `/rehearse framing docs/problem_statement.md` |
| Check the analytical approach | `/rehearse method docs/approach.md -c data/data_dictionary.md` |
| Review an analysis in progress, with the panel reading your queries | `/rehearse review docs/findings.md -c analysis/ -c data/data_dictionary.md` |
| Rehearse a deck before it goes out | `/rehearse preread docs/one_pager.md -c docs/` |
| Prepare for a meeting with one function | `/rehearse stakeholder docs/ask.md --panel risk_compliance,ops` |
| Choose between options | `/rehearse decide docs/options.md` |
| Grade a practice diagnosis against the sealed key | `/rehearse grade docs/diagnosis.md --answer-key .rehearsal/scenarios/<name>/answer_key.md.b64` |
| Build a new practice case | `/scenario` |
| Record what was really asked after a meeting | `/rehearse debrief` |

`-c` points the roles at files or directories they may open. That is the
point of running in-project: the Methodology Reviewer reads your SQL, Finance
reads your sizing, nobody works from a paste.

## Practice before day one

`playground/cobrand-delinquency/` is a complete practice case: a Director's
brief, 18 months of synthetic co-brand card data with planted drivers and
traps, a data dictionary, ops notes, and a sealed answer key. Open that folder
in Claude Code and start with its `README.md`. Build more cases with
`/scenario`.

## Where everything lives

| What | Where |
|---|---|
| The package (engine, CLI, bundled defaults, skills) | `rehearsal/` |
| Default role personas | `rehearsal/assets/roles/mechanism/`, `rehearsal/assets/roles/panel/` |
| Default modes, config, profile | `rehearsal/assets/modes.yaml`, `config.yaml`, `profile/` |
| The two skills | `rehearsal/assets/skills/rehearse/`, `rehearsal/assets/skills/scenario/` |
| A project's own copy (after `rehearse init`) | `<project>/.rehearsal/`, `<project>/.claude/skills/` |
| Practice case | `playground/cobrand-delinquency/` |
| Web app (paste-in, no file access) | https://claude.ai/artifact/4gwYTmavK8DDqwSZTnFvAp, source in `app/` |
| Design notes | `docs/DESIGN.md` |
| Tests | `tests/` (`pytest`, no network) |

Run outputs go to `<project>/.rehearsal/sessions/` and are never committed.

## Other ways to run the same pipeline

- **Web app** (https://claude.ai/artifact/4gwYTmavK8DDqwSZTnFvAp): a chat-style
  page for the paste-in case, when there is no project to point at. Runs on
  your claude.ai account. Rebuild from the repo with `python scripts/build_app.py`.
- **Python CLI with an API key**: `rehearse run -m preread -i deck.md -c analysis/`
  calls the API directly (`ANTHROPIC_API_KEY` or `ant auth login`), inlining
  the context files into the prompts. `rehearse run ... --mock` exercises the
  pipeline without a model.

## Input rules

Markdown or text. Use placeholders such as `[X]` or `[$M]` for real figures;
roles ask about provenance, not about the blank. At work: no customer data,
real figures, or verbatim internal documents, and check your employer's policy
on external AI tools. Practice cases are synthetic and exempt.

## Tests

```bash
pip install -e ".[dev]" && pytest
```
