# CLAUDE.md

Rehearsal Room: a pre-meeting rehearsal panel for a Business Analyst. One
pipeline (Coach → Advocate, Challenger, panel → Judge → Coach), three runtimes
(claude.ai web app, Claude Code skill, Python CLI). Read `README.md` for the
map and `docs/DESIGN.md` for the reasoning.

## Layout

```
app/template.html         web app source (edit)        app/dist/index.html  built, published
roles/mechanism|panel/    role personas (Markdown + YAML header)
config/config.yaml        models, effort, paths        config/modes.yaml    the five modes
profile/                  workplace profile and debrief log (default seeds)
rehearsal/                Python package: schemas, engine, staging, report, cli
.claude/skills/rehearse/  the /rehearse skill
examples/inputs|outputs/  sample deck and the report it produced
sessions/                 run outputs, git-ignored, may hold work material
tests/                    pytest, no network
docs/                     DESIGN.md
```

## Commands

```bash
pip install -e ".[dev]"                 # once per environment
pytest                                   # 16 tests, mock backend
python scripts/build_app.py              # rebuild app/dist/index.html from roles, modes, profile, schemas
python -m rehearsal.cli run -m preread -i examples/inputs/sample_preread.md --mock
python -m rehearsal.cli stage init|next  # what the skill drives
```

## Conventions

- Role behaviour lives in `roles/*.md`, not in code. Fix a persona there.
- `rehearsal/schemas.py` is the single source of truth for output shapes; the
  app embeds the generated JSON Schema, so a schema change needs a rebuild.
- Prompt assembly is mirrored in two places on purpose: `rehearsal/engine.py`
  (`Prompts`) and the `P` object in `app/template.html`. Keep them aligned.
- After editing anything under `roles/`, `config/`, `profile/` or
  `app/template.html`: run the build script and republish `app/dist/index.html`
  to the existing artifact URL (in README). Never publish to a new URL.
- Never commit `sessions/`. Never put real customer data, real figures or
  internal documents anywhere in this repo, including examples.
- Default model for the CLI is `claude-opus-5-5`; the app uses model tiers
  (`complex` for Coach and Judge, `default` for the panel).
- Commit messages: plain, no model names.
