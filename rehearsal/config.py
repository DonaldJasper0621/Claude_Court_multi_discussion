"""Load config.yaml, modes.yaml, role personas, and the workplace profile."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


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


@dataclass
class Config:
    root: Path
    models: dict[str, str]
    effort: dict[str, str]
    max_tokens: int
    max_concurrency: int
    output_language: str
    paths: dict[str, str]
    modes: dict[str, Mode] = field(default_factory=dict)
    roles: dict[str, Role] = field(default_factory=dict)

    # ----- resolved paths ------------------------------------------------- #
    def path(self, key: str) -> Path:
        return self.root / self.paths[key]

    @property
    def sessions_dir(self) -> Path:
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
# Loading
# --------------------------------------------------------------------------- #


def find_root(start: Path | None = None) -> Path:
    """Walk up from `start` (default cwd) until a directory with config.yaml."""
    env = os.environ.get("REHEARSAL_ROOT")
    if env:
        root = Path(env).expanduser().resolve()
        if (root / "config.yaml").exists():
            return root
        raise ConfigError(f"REHEARSAL_ROOT={root} has no config.yaml")
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "config.yaml").exists() and (candidate / "modes.yaml").exists():
            return candidate
    raise ConfigError(
        "Could not find config.yaml. Run from inside the project, or set REHEARSAL_ROOT."
    )


def load_config(root: Path | None = None) -> Config:
    root = root or find_root()
    raw = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8")) or {}
    try:
        cfg = Config(
            root=root,
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
