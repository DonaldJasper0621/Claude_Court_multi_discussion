"""Render a session into a self-contained HTML report."""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .schemas import Session

# USD per million tokens: (input, output, cache read, cache write)
PRICES = {
    "claude-opus-5-5": (4.00, 20.00, 0.20, 5.00),
    "claude-opus-5": (5.00, 25.00, 0.50, 6.25),
    "claude-sonnet-5-5": (2.00, 10.00, 0.20, 2.50),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
    "claude-fable-5-1": (10.00, 50.00, 0.25, 12.50),
}

STANCE_ORDER = {"blocking": 0, "skeptical": 1, "neutral": 2, "supportive": 3}


def estimate_cost(session: Session) -> float | None:
    total = 0.0
    known = False
    for call in session.calls:
        price = PRICES.get(call.model)
        if not price:
            continue
        known = True
        u = call.usage
        total += (
            u.input_tokens * price[0]
            + u.output_tokens * price[1]
            + u.cache_read_input_tokens * price[2]
            + u.cache_creation_input_tokens * price[3]
        ) / 1_000_000
    return total if known else None


def render_report(session: Session) -> str:
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent / "templates"),
        autoescape=select_autoescape(["html", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("report.html.j2")
    panel_sorted = sorted(
        session.panel,
        key=lambda r: STANCE_ORDER.get(r.output.stance, 9) if r.output else 9,
    )
    usage = session.total_usage()
    seconds = round(sum(c.seconds for c in session.calls), 1)
    return template.render(
        s=session,
        panel=panel_sorted,
        usage=usage,
        cost=estimate_cost(session),
        seconds=seconds,
        n_calls=len(session.calls),
    )


def write_report(session: Session, session_dir: Path) -> Path:
    out = session_dir / "report.html"
    out.write_text(render_report(session), encoding="utf-8")
    return out
