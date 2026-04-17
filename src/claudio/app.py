"""Flask application: routes and entry point."""

import json
import logging
import os
import re
from datetime import date as date_type
from datetime import datetime, timezone

from flask import Flask, Response, render_template, request
from jinja2 import ChoiceLoader, DictLoader

from claudio.health import check_environment
from claudio.parsers import (
    PROJECTS_DIR,
    fmt_cost,
    fmt_ts,
    group_by_project,
    load_all_sessions,
    load_history,
    load_project_memory,
    load_todos,
    parse_session,
    session_title,
    strip_home,
)
from claudio.templates import (
    BASE,
    HEALTH_TMPL,
    INDEX_TMPL,
    MEMORY_TMPL,
    SESSION_TMPL,
    STATS_TMPL,
    archive_icon,
    brain_icon,
    pie_icon,
)

app = Flask(__name__)

# Register inline templates with a DictLoader so {% extends %} works
_dict_loader = DictLoader(
    {
        "base.html": BASE,
        "index.html": INDEX_TMPL,
        "session.html": SESSION_TMPL,
        "memory.html": MEMORY_TMPL,
        "health.html": HEALTH_TMPL,
        "stats.html": STATS_TMPL,
    }
)
_loaders = [ldr for ldr in [_dict_loader, app.jinja_env.loader] if ldr is not None]
app.jinja_env.loader = ChoiceLoader(_loaders)


@app.context_processor
def inject_health():
    return {"health": check_environment()}


app.jinja_env.globals.update(
    session_title=session_title,
    fmt_ts=fmt_ts,
    fmt_cost=fmt_cost,
    strip_home=strip_home,
    brain_icon=brain_icon,
    archive_icon=archive_icon,
    pie_icon=pie_icon,
)


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------


def _export_session(s: dict) -> dict:
    """Flatten a parsed session dict into the portable export schema."""
    slug = s.get("project_slug", "")
    cwd = s.get("cwd") or ("/" + slug.lstrip("-").replace("-", "/"))
    return {
        "uuid": s.get("session_id"),
        "title": session_title(s),
        "created_at": s.get("started_at"),
        "updated_at": s.get("ended_at"),
        "cost": {
            "total": s.get("cost_usd"),
            "cost_unknown": s.get("cost_unknown", False),
        },
        "messages": s.get("message_count", 0),
        "project": {
            "path": strip_home(cwd),
            "slug": slug,
        },
        "compactions": s.get("compact_count", 0),
        "model": s.get("model"),
    }


def _export_pricing() -> dict:
    """Return current pricing config for inclusion in export."""
    from claudio.parsers import PRICING

    return {
        "source": "built-in (parsers.py)",
        "models": {
            model: {
                "input": rates[0],
                "cache_write": rates[1],
                "cache_read": rates[2],
                "output": rates[3],
            }
            for model, rates in PRICING.items()
        },
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    sessions, failures = load_all_sessions()
    for s in sessions:
        s["title"] = session_title(s)
    groups = group_by_project(sessions)
    return render_template(
        "index.html",
        groups=groups,
        total=len(sessions),
        n_projects=len(groups),
        failures=failures,
    )


_SESSION_ID_RE = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


@app.route("/session/<session_id>")
def session_view(session_id: str):
    if not _SESSION_ID_RE.match(session_id):
        return "Invalid session ID", 400
    jsonl_path = None
    if not PROJECTS_DIR.exists():
        return "Session not found", 404
    for proj_dir in PROJECTS_DIR.iterdir():
        candidate = proj_dir / f"{session_id}.jsonl"
        if candidate.exists():
            jsonl_path = candidate
            break

    if jsonl_path is None:
        return "Session not found", 404

    session = parse_session(jsonl_path)
    session["project_slug"] = jsonl_path.parent.name

    todos_map = load_todos()
    todos = todos_map.get(session_id, [])

    history_map = load_history()
    proj_history = history_map.get(session.get("cwd") or "", [])
    if not proj_history:
        for entries in history_map.values():
            matched = [e for e in entries if e["session_id"] == session_id]
            if matched:
                proj_history.extend(matched)

    memory = load_project_memory(jsonl_path.parent.name)

    return render_template(
        "session.html",
        session=session,
        title=session_title(session),
        todos=todos,
        history=proj_history,
        memory=memory,
    )


_SLUG_RE = re.compile(r"^[a-zA-Z0-9-]+$")


@app.route("/memory/<project_slug>")
def project_memory(project_slug: str):
    if not _SLUG_RE.match(project_slug) or not any(c.isalnum() for c in project_slug):
        return "Invalid project slug", 400
    memory = load_project_memory(project_slug)
    if not memory["count"] and not memory["index"]:
        return "No memory found for this project", 404
    label = strip_home("/" + project_slug.lstrip("-").replace("-", "/"))
    return render_template(
        "memory.html",
        memory=memory,
        label=label,
        project_slug=project_slug,
    )


@app.route("/health")
def health_status():
    result = check_environment()
    return render_template("health.html", health=result)


@app.route("/export/sessions.json")
def export_sessions():
    sessions, failures = load_all_sessions()
    export_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    filename_date = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")

    payload = {
        "claudio_version": "0.4.0",
        "export_date": export_date,
        "claude_directory": str(PROJECTS_DIR.parent),
        "total_sessions": len(sessions) + len(failures),
        "parsed_sessions": len(sessions),
        "failed_sessions": [{"path": f["path"], "error": f["error_type"]} for f in failures],
        "sessions": [_export_session(s) for s in sessions],
        "pricing_config": _export_pricing(),
    }

    return Response(
        json.dumps(payload, indent=2, default=str),
        mimetype="application/json",
        headers={
            "Content-Disposition": f'attachment; filename="claudio-export-{filename_date}.json"'
        },
    )


@app.route("/stats")
def stats():
    sessions, failures = load_all_sessions()
    failure_count = len(failures)
    for s in sessions:
        s["title"] = session_title(s)

    def _ts_ms(ts):
        if not ts:
            return None
        if isinstance(ts, (int, float)):
            return int(ts)
        return int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000)

    def _session_date(s):
        ts = s.get("started_at")
        if not ts:
            return None
        ms = _ts_ms(ts)
        if ms is None:
            return None
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).date()

    # Date range filter from query params
    from_str = request.args.get("from", "").strip()
    to_str = request.args.get("to", "").strip()

    from_date = None
    to_date = None
    if from_str:
        try:
            from_date = date_type.fromisoformat(from_str)
        except ValueError:
            from_str = ""
    if to_str:
        try:
            to_date = date_type.fromisoformat(to_str)
        except ValueError:
            to_str = ""

    # Silently swap if the range is inverted
    if from_date and to_date and from_date > to_date:
        from_date, to_date = to_date, from_date
        from_str, to_str = to_str, from_str

    filtered = sessions
    if from_date:
        filtered = [s for s in filtered if (_session_date(s) or date_type.min) >= from_date]
    if to_date:
        filtered = [s for s in filtered if (_session_date(s) or date_type.max) <= to_date]

    groups = group_by_project(filtered) if filtered else []

    sessions_raw = [
        {"ts_ms": _ts_ms(s.get("started_at")), "cost_usd": round(s.get("cost_usd") or 0, 4)}
        for s in filtered
    ]

    top_by_cost = sorted(
        [
            {
                "title": s["title"],
                "cost_usd": round(s.get("cost_usd") or 0, 4),
                "session_id": s["session_id"],
            }
            for s in filtered
            if s.get("cost_usd")
        ],
        key=lambda x: x["cost_usd"],
        reverse=True,
    )

    by_project = sorted(
        [
            {
                "label": g["label"],
                "cost_usd": round(sum(s.get("cost_usd") or 0 for s in g["sessions"]), 4),
                "count": len(g["sessions"]),
            }
            for g in groups
        ],
        key=lambda x: x["cost_usd"],
        reverse=True,
    )

    total_cost = sum(s.get("cost_usd") or 0 for s in filtered)
    total_messages = sum(s.get("message_count") or 0 for s in filtered)
    sessions_with_cost = [s for s in filtered if s.get("cost_usd")]
    avg_cost = (
        (sum(s["cost_usd"] for s in sessions_with_cost) / len(sessions_with_cost))
        if sessions_with_cost
        else 0
    )

    payload = {"sessions_raw": sessions_raw, "top_by_cost": top_by_cost, "by_project": by_project}

    # When the filter produces no results, supply unfiltered data as a ghost
    # backdrop so the blurred chart area shows real shapes instead of blank cards.
    ghost_payload = None
    if not filtered and sessions:
        ghost_groups = group_by_project(sessions)
        ghost_payload = {
            "sessions_raw": [
                {"ts_ms": _ts_ms(s.get("started_at")), "cost_usd": round(s.get("cost_usd") or 0, 4)}
                for s in sessions
            ],
            "top_by_cost": sorted(
                [
                    {
                        "title": s["title"],
                        "cost_usd": round(s.get("cost_usd") or 0, 4),
                        "session_id": s["session_id"],
                    }
                    for s in sessions
                    if s.get("cost_usd")
                ],
                key=lambda x: x["cost_usd"],
                reverse=True,
            ),
            "by_project": sorted(
                [
                    {
                        "label": g["label"],
                        "cost_usd": round(sum(s.get("cost_usd") or 0 for s in g["sessions"]), 4),
                        "count": len(g["sessions"]),
                    }
                    for g in ghost_groups
                ],
                key=lambda x: x["cost_usd"],
                reverse=True,
            ),
        }

    return render_template(
        "stats.html",
        payload=payload,
        ghost_payload=ghost_payload,
        total_sessions=len(filtered),
        total_loaded=len(sessions),
        total_cost=total_cost,
        total_messages=total_messages,
        avg_cost=avg_cost,
        from_str=from_str,
        to_str=to_str,
        failure_count=failure_count,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    port = int(os.environ.get("PORT", 5001))
    host = os.environ.get("HOST", "127.0.0.1")
    debug = os.environ.get("DEBUG", "").lower() in ("1", "true")
    if not debug:
        logging.getLogger("werkzeug").setLevel(logging.ERROR)
    print(f"\n  claudio → http://{host}:{port}\n")
    app.run(host=host, port=port, debug=debug)
