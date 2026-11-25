"""Load config.yaml, modes.yaml, role personas, and the workplace profile.

Where the configuration comes from, in order:

1. `REHEARSAL_ROOT` (a directory holding config.yaml), if set.
2. The nearest `.rehearsal/` directory walking up from the current directory.
   `rehearse init` creates one inside a project, with its own editable copy of
   the defaults, so each project can tune roles and profile and commit them.
3. The defaults bundled with the package (`rehearsal/assets/`). Read-only;
   sessions then go to `<cwd>/.rehearsal/sessions`.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ASSETS = Path(__file__).resolve().parent / "assets"
PROJECT_DIRNAME = ".rehearsal"


class ConfigError(Exception):
    pass


@dataclass
class Role:
    id: str
    name: str
    layer: str  # "mechanism" | "panel"
    body: str
    path: Path


@dataclass
class Mode:
    id: str
    title: str
    description: str
    input_hint: str
    panel: list[str]
    emphasis: str
    judge_focus: str
    judge_schema: str = "JudgeBrief"  # name of the schema the Judge answers with


@dataclass
class Config:
    base: Path       # directory holding config.yaml; relative paths resolve here
    project: Path    # the project this run belongs to (sessions live under it)
    models: dict[str, str]
    effort: dict[str, str]
    max_tokens: int
    max_concurrency: int
    output_language: str
    paths: dict[str, str]
    modes: dict[str, Mode] = field(default_factory=dict)
    roles: dict[str, Role] = field(default_factory=dict)

    # ----- resolved paths ------------------------------------------------- #
    @property
    def root(self) -> Path:  # kept for callers that predate `base`
        return self.base

    @property
    def bundled(self) -> bool:
        return _is_under(self.base, ASSETS)

    def path(self, key: str) -> Path:
        return self.base / self.paths[key]

    @property
    def sessions_dir(self) -> Path:
        if self.bundled:
            return self.project / PROJECT_DIRNAME / "sessions"
        return self.path("sessions")

    # ----- role access ---------------------------------------------------- #
    def mechanism(self, role_id: str) -> Role:
        role = self.roles.get(role_id)
        if role is None or role.layer != "mechanism":
            raise ConfigError(f"Mechanism role '{role_id}' not found under {self.path('roles')}/mechanism")
        return role

    def panelist(self, role_id: str) -> Role:
        role = self.roles.get(role_id)
        if role is None or role.layer != "panel":
            available = ", ".join(sorted(r.id for r in self.roles.values() if r.layer == "panel"))
            raise ConfigError(f"Panel role '{role_id}' not found. Available: {available}")
        return role

    def panel_roles(self) -> list[Role]:
        return sorted((r for r in self.roles.values() if r.layer == "panel"), key=lambda r: r.id)

    # ----- profile -------------------------------------------------------- #
    def read_profile(self) -> str:
        return _read_optional(self.path("profile"))

    def read_debrief_log(self) -> str:
        return _read_optional(self.path("debrief_log"))


# --------------------------------------------------------------------------- #
# Discovery
# --------------------------------------------------------------------------- #


def find_base(start: Path | None = None) -> tuple[Path, Path]:
    """Return (base, project). See the module docstring for the order."""
    env = os.environ.get("REHEARSAL_ROOT")
    if env:
        base = Path(env).expanduser().resolve()
        if not (base / "config.yaml").exists():
            raise ConfigError(f"REHEARSAL_ROOT={base} has no config.yaml")
        project = base.parent if base.name == PROJECT_DIRNAME else base
        return base, project
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / PROJECT_DIRNAME / "config.yaml").exists():
            return candidate / PROJECT_DIRNAME, candidate
    return ASSETS, here


def load_config(root: Path | None = None, project: Path | None = None) -> Config:
    """`root` is the directory holding config.yaml (a `.rehearsal/` dir, the
    bundled assets, or any directory laid out the same way)."""
    if root is not None:
        base = Path(root).resolve()
        if not (base / "config.yaml").exists():
            raise ConfigError(f"{base} has no config.yaml")
        if project:
            proj = Path(project).resolve()
        elif base.name == PROJECT_DIRNAME:
            proj = base.parent
        elif _is_under(base, ASSETS):
            proj = Path.cwd().resolve()  # bundled defaults never own a project
        else:
            proj = base
    else:
        base, proj = find_base()
        if project:
            proj = Path(project).resolve()

    raw = yaml.safe_load((base / "config.yaml").read_text(encoding="utf-8")) or {}
    try:
        cfg = Config(
            base=base,
            project=proj,
            models=dict(raw["models"]),
            effort=dict(raw["effort"]),
            max_tokens=int(raw.get("max_tokens", 8000)),
            max_concurrency=int(raw.get("max_concurrency", 6)),
            output_language=str(raw.get("output_language", "en")),
            paths=dict(raw["paths"]),
        )
    except KeyError as e:
        raise ConfigError(f"config.yaml is missing key {e}") from e

    cfg.modes = _load_modes(cfg.path("modes"))
    cfg.roles = _load_roles(cfg.path("roles"))

    for mode in cfg.modes.values():
        for rid in mode.panel:
            cfg.panelist(rid)  # validates
    for required in ("coach", "advocate", "challenger", "judge"):
        cfg.mechanism(required)
    return cfg


# --------------------------------------------------------------------------- #
# Project setup
# --------------------------------------------------------------------------- #


def init_project(target: Path, *, force: bool = False) -> list[Path]:
    """Create `<target>/.rehearsal/` with an editable copy of the defaults and
    drop the bundled skills into `<target>/.claude/skills/`. Returns the paths
    written. Existing files are kept unless `force`."""
    target = Path(target).resolve()
    dest = target / PROJECT_DIRNAME
    written: list[Path] = []

    def copy(src: Path, dst: Path) -> None:
        if dst.exists() and not force:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        written.append(dst)

    for name in ("config.yaml", "modes.yaml"):
        copy(ASSETS / name, dest / name)
    for sub in ("roles", "profile"):
        for src in sorted((ASSETS / sub).rglob("*.md")):
            copy(src, dest / src.relative_to(ASSETS))
    (dest / "sessions").mkdir(parents=True, exist_ok=True)
    (dest / "scenarios").mkdir(parents=True, exist_ok=True)
    gi = dest / ".gitignore"
    if not gi.exists():
        gi.write_text("# Run outputs may contain work material. Never commit.\nsessions/\n", encoding="utf-8")
        written.append(gi)
    for skill_dir in sorted(p for p in (ASSETS / "skills").iterdir() if p.is_dir()):
        copy(skill_dir / "SKILL.md", target / ".claude" / "skills" / skill_dir.name / "SKILL.md")
    return written


def install_skills(home: Path | None = None, *, force: bool = False) -> list[Path]:
    """Install the bundled skills at user level (`~/.claude/skills/`) so
    `/rehearse` works in every project on this machine."""
    home = Path(home) if home else Path.home()
    written: list[Path] = []
    for skill_dir in sorted(p for p in (ASSETS / "skills").iterdir() if p.is_dir()):
        dst = home / ".claude" / "skills" / skill_dir.name / "SKILL.md"
        if dst.exists() and not force:
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(skill_dir / "SKILL.md", dst)
        written.append(dst)
    return written


# --------------------------------------------------------------------------- #
# Loading helpers
# --------------------------------------------------------------------------- #


def _load_modes(path: Path) -> dict[str, Mode]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    modes: dict[str, Mode] = {}
    for mode_id, m in raw.items():
        try:
            modes[mode_id] = Mode(
                id=mode_id,
                title=m["title"],
                description=m.get("description", ""),
                input_hint=m.get("input_hint", ""),
                panel=list(m["panel"]),
                emphasis=m["emphasis"].strip(),
                judge_focus=m["judge_focus"].strip(),
                judge_schema=str(m.get("judge_schema", "JudgeBrief")),
            )
        except KeyError as e:
            raise ConfigError(f"modes.yaml: mode '{mode_id}' is missing key {e}") from e
    if not modes:
        raise ConfigError(f"No modes defined in {path}")
    return modes


def _load_roles(roles_dir: Path) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for layer in ("mechanism", "panel"):
        for path in sorted((roles_dir / layer).glob("*.md")):
            role = parse_role_file(path, default_layer=layer)
            if role.id in roles:
                raise ConfigError(f"Duplicate role id '{role.id}' ({path} and {roles[role.id].path})")
            roles[role.id] = role
    return roles


def parse_role_file(path: Path, default_layer: str = "panel") -> Role:
    text = path.read_text(encoding="utf-8")
    meta, body = split_frontmatter(text)
    role_id = str(meta.get("id") or path.stem)
    return Role(
        id=role_id,
        name=str(meta.get("name") or role_id.replace("_", " ").title()),
        layer=str(meta.get("layer") or default_layer),
        body=body.strip(),
        path=path,
    )


def split_frontmatter(text: str) -> tuple[dict, str]:
    """Split a Markdown file with optional YAML frontmatter delimited by '---'."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    _, fm, body = parts
    meta = yaml.safe_load(fm) or {}
    if not isinstance(meta, dict):
        meta = {}
    return meta, body


def _read_optional(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        return ""


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False
