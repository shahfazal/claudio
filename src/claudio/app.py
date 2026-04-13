"""Flask application — routes and entry point."""

import logging
import os
import re

from flask import Flask, render_template
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
from claudio.templates import BASE, HEALTH_TMPL, INDEX_TMPL, MEMORY_TMPL, SESSION_TMPL, archive_icon, brain_icon

app = Flask(__name__)

# Register inline templates with a DictLoader so {% extends %} works
_dict_loader = DictLoader(
    {
        "base.html": BASE,
        "index.html": INDEX_TMPL,
        "session.html": SESSION_TMPL,
        "memory.html": MEMORY_TMPL,
        "health.html": HEALTH_TMPL,
    }
)
_loaders = [ldr for ldr in [_dict_loader, app.jinja_env.loader] if ldr is not None]
app.jinja_env.loader = ChoiceLoader(_loaders)


@app.context_processor
def inject_health():
    return {"health": check_environment()}


app.jinja_env.globals.update(
    session_title=session_title, fmt_ts=fmt_ts, fmt_cost=fmt_cost,
    strip_home=strip_home, brain_icon=brain_icon, archive_icon=archive_icon,
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.route("/")
def index():
    sessions = load_all_sessions()
    for s in sessions:
        s["title"] = session_title(s)
    groups = group_by_project(sessions)
    return render_template(
        "index.html",
        groups=groups,
        total=len(sessions),
        n_projects=len(groups),
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


_SLUG_RE = re.compile(r"^[a-zA-Z0-9-]*[a-zA-Z0-9][a-zA-Z0-9-]*$")


@app.route("/memory/<project_slug>")
def project_memory(project_slug: str):
    if not _SLUG_RE.match(project_slug):
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
