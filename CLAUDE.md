# CLAUDE.md

Rehearsal Room: a pre-meeting rehearsal panel for a Business Analyst that
lives inside the projects it reviews. One pipeline (Coach → Advocate,
Challenger, panel → Judge → Coach), three runtimes (Claude Code skill with
file access, Python CLI, claude.ai web app). `README.md` is the map;
`docs/DESIGN.md` is the reasoning.

## Layout

```
rehearsal/                  the package
  assets/                   bundled defaults: config.yaml, modes.yaml, roles/, profile/, skills/
  schemas.py                output contracts (single source of truth; the app embeds the JSON Schema)
  config.py                 discovery: REHEARSAL_ROOT > nearest .rehearsal/ > bundled assets; `init_project`
  engine.py                 Prompts (shared prompt assembly), async API runner, context_block, read_answer_key
  staging.py                staged runner driven by an orchestrator (the skill): prompt files in, JSON out
  report.py + templates/    HTML report
  cli.py                    rehearse run|stage|init|install-skills|where|modes|roles|sessions|debrief
app/template.html           web app source; app/dist/index.html is built by scripts/build_app.py
playground/cobrand-delinquency/   practice case (data, brief, sealed key, its own .rehearsal/)
docs/DESIGN.md
tests/                      pytest, mock backend, no network
```

## Commands

```bash
pip install -e ".[dev]"
pytest                                   # 21 tests
python scripts/build_app.py              # rebuild app/dist/index.html, then republish to the artifact URL in README
rehearse init <dir>                      # give a project its own .rehearsal/ and skills
rehearse where                           # which config/project/sessions are in use
rehearse stage init -m review -i docs/x.md -c analysis/   # what /rehearse drives
```

## Conventions

- Role behaviour lives in `rehearsal/assets/roles/*.md` (defaults) or a
  project's `.rehearsal/roles/` (its copy). Fix a persona there, not in code.
- Prompt assembly is mirrored on purpose in `engine.py` (`Prompts`) and in the
  `P` object of `app/template.html`. Keep them aligned when a block changes.
- After editing anything under `rehearsal/assets/` or `app/template.html`:
  run the build script and republish `app/dist/index.html` to the existing
  artifact URL. Never publish to a new URL.
- Sealed scenario material (`.rehearsal/scenarios/*/*.b64`) is read only by
  the Judge through `--answer-key`. Never decode, quote or summarize it in
  chat, commits or files. The practice project's own `CLAUDE.md` repeats this.
- Never commit any `sessions/` directory. No real customer data, real figures
  or internal documents anywhere in this repo; synthetic data is fine.
- Default CLI model is `claude-opus-5-5`; the app uses tiers (`complex` for
  Coach and Judge, `default` for the panel). Commit messages name no models.
