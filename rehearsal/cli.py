"""`rehearse` command line."""

from __future__ import annotations

import argparse
import asyncio
import sys
import webbrowser
from pathlib import Path

from . import __version__
from .config import Config, ConfigError, load_config
from .debrief import append_to_log, format_log_entry, hit_rate, run_debrief
from .engine import Engine, load_session, save_session
from .llm import AnthropicLLM, MockLLM
from .report import write_report

CONFIDENTIALITY_NOTE = (
    "Reminder: input should be de-identified structure, logic and assumptions. "
    "No customer data, real figures, or verbatim internal documents."
)


def _err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


def _progress(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def _read_input(spec: str) -> str:
    if spec == "-":
        return sys.stdin.read()
    path = Path(spec)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #


def cmd_run(cfg: Config, args: argparse.Namespace) -> int:
    mode = cfg.modes.get(args.mode)
    if mode is None:
        _err(f"unknown mode '{args.mode}'. Available: {', '.join(cfg.modes)}")
        return 2
    try:
        input_text = _read_input(args.input)
    except FileNotFoundError as e:
        _err(str(e))
        return 2
    if not input_text.strip():
        _err("input is empty")
        return 2

    panel_ids: list[str] | None = None
    if args.panel:
        panel_ids = [p.strip() for p in args.panel.split(",") if p.strip()]
    if args.add:
        panel_ids = list(panel_ids or mode.panel)
        for extra in (p.strip() for p in args.add.split(",")):
            if extra and extra not in panel_ids:
                panel_ids.append(extra)
    try:
        for rid in panel_ids or []:
            cfg.panelist(rid)
    except ConfigError as e:
        _err(str(e))
        return 2

    if args.language:
        cfg.output_language = args.language

    _progress(CONFIDENTIALITY_NOTE)
    if args.mock:
        llm = MockLLM()
        _progress("Mock mode: no model calls will be made.")
    else:
        try:
            llm = AnthropicLLM()
        except Exception as e:  # noqa: BLE001
            _err(f"could not create Anthropic client: {e}")
            return 1

    engine = Engine(cfg, llm, progress=_progress, mock=args.mock)
    session = asyncio.run(
        engine.run(mode_id=args.mode, input_text=input_text, worry=args.worry, panel_ids=panel_ids)
    )
    out_dir = save_session(session, cfg.sessions_dir)
    report = write_report(session, out_dir)

    if session.judge:
        _progress(f"\nVerdict: {session.judge.verdict.upper()} — {session.judge.headline}")
    if session.errors:
        _progress(f"{len(session.errors)} role(s) failed: {', '.join(session.errors)}")
    print(out_dir)
    _progress(f"Report: {report}")
    if not args.no_open:
        webbrowser.open(report.resolve().as_uri())
    return 0 if not session.errors else 3


def cmd_modes(cfg: Config, _args: argparse.Namespace) -> int:
    for mode in cfg.modes.values():
        print(f"{mode.id:12s} {mode.title} — {mode.description}")
        print(f"{'':12s} panel: {', '.join(mode.panel)}")
        print(f"{'':12s} input: {mode.input_hint}")
    return 0


def cmd_roles(cfg: Config, _args: argparse.Namespace) -> int:
    print("Mechanism (always present):")
    for rid in ("coach", "advocate", "challenger", "judge"):
        print(f"  {rid:22s} {cfg.mechanism(rid).name}")
    print("Panel (select with --panel / --add):")
    for role in cfg.panel_roles():
        print(f"  {role.id:22s} {role.name}")
    return 0


def cmd_debrief(cfg: Config, args: argparse.Namespace) -> int:
    path = Path(args.session)
    if not path.exists():
        candidate = cfg.sessions_dir / args.session
        if candidate.exists():
            path = candidate
        else:
            _err(f"session not found: {args.session}")
            return 2
    session = load_session(path)
    try:
        debrief = run_debrief(session)
    except (EOFError, KeyboardInterrupt):
        print("\naborted", file=sys.stderr)
        return 130
    session.debrief = debrief
    session_dir = path if path.is_dir() else path.parent
    save_session(session, session_dir.parent)
    write_report(session, session_dir)
    append_to_log(cfg.path("debrief_log"), format_log_entry(session, debrief))
    asked, total = hit_rate(debrief)
    print(f"\nRecorded. Predicted questions asked: {asked}/{total}. "
          f"Unpredicted: {len(debrief.unpredicted)}. Appended to {cfg.path('debrief_log')}.")
    return 0


def cmd_sessions(cfg: Config, _args: argparse.Namespace) -> int:
    dirs = sorted(p for p in cfg.sessions_dir.iterdir() if p.is_dir()) if cfg.sessions_dir.exists() else []
    if not dirs:
        print("no sessions yet")
        return 0
    for d in dirs:
        try:
            s = load_session(d)
            verdict = s.judge.verdict if s.judge else "—"
            flag = " (debriefed)" if s.debrief else ""
            print(f"{d.name:36s} {verdict:7s} {s.judge.headline if s.judge else ''}{flag}")
        except Exception:  # noqa: BLE001
            print(f"{d.name:36s} (unreadable)")
    return 0


def cmd_profile(cfg: Config, _args: argparse.Namespace) -> int:
    print(cfg.path("profile"))
    return 0


# --------------------------------------------------------------------------- #
# Parser
# --------------------------------------------------------------------------- #


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="rehearse",
        description="Pre-meeting rehearsal room: a simulated stakeholder panel for your decks, memos and decisions.",
    )
    p.add_argument("--version", action="version", version=f"rehearse {__version__}")
    p.add_argument("--root", type=Path, help="Project root containing config.yaml (default: search upward from cwd).")
    sub = p.add_subparsers(dest="command", required=True)

    r = sub.add_parser("run", help="Run a rehearsal on a piece of material.")
    r.add_argument("-m", "--mode", required=True, help="framing | method | preread | stakeholder | decide")
    r.add_argument("-i", "--input", required=True, help="Path to a Markdown/text file, or - for stdin.")
    r.add_argument("-w", "--worry", help="What you are most worried about, in a sentence.")
    r.add_argument("-p", "--panel", help="Comma-separated panel role ids; replaces the mode default.")
    r.add_argument("-a", "--add", help="Comma-separated panel role ids to add to the default.")
    r.add_argument("--language", help="Override output language (e.g. en, zh-TW).")
    r.add_argument("--mock", action="store_true", help="Run without calling the model (pipeline check).")
    r.add_argument("--no-open", action="store_true", help="Do not open the report in a browser.")
    r.set_defaults(func=cmd_run)

    sub.add_parser("modes", help="List modes and their default panels.").set_defaults(func=cmd_modes)
    sub.add_parser("roles", help="List available roles.").set_defaults(func=cmd_roles)
    sub.add_parser("sessions", help="List past sessions.").set_defaults(func=cmd_sessions)
    sub.add_parser("profile", help="Print the path of the workplace profile.").set_defaults(func=cmd_profile)

    d = sub.add_parser("debrief", help="Record what was actually asked in the real meeting.")
    d.add_argument("session", help="Session id or path (directory or session.json).")
    d.set_defaults(func=cmd_debrief)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        cfg = load_config(args.root)
    except ConfigError as e:
        _err(str(e))
        return 2
    return int(args.func(cfg, args))


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
