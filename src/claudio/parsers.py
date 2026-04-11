"""Data loading and parsing for Claude Code session files."""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude"
PROJECTS_DIR = CLAUDE_DIR / "projects"
HISTORY_FILE = CLAUDE_DIR / "history.jsonl"
TODOS_DIR = CLAUDE_DIR / "todos"

_STRIP_TAG_RE = re.compile(r"<([a-z][a-z_-]*)>.*?</\1>", re.DOTALL | re.IGNORECASE)

# ---------------------------------------------------------------------------
# MODEL PRICING TABLE — update when Anthropic changes rates
# Keys are exact model IDs as they appear in session JSONL.
# Rates are per million tokens: (input, cache_write, cache_read, output)
# Source: https://www.anthropic.com/pricing
# ---------------------------------------------------------------------------
PRICING: dict[str, tuple[float, float, float, float]] = {
    # Claude 4 family
    "claude-opus-4-5": (15.00, 18.75, 1.50, 75.00),
    "claude-sonnet-4-6": (3.00, 3.75, 0.30, 15.00),
    # Claude 3.x family (dated model IDs used by Claude Code)
    "claude-sonnet-4-5-20250929": (3.00, 3.75, 0.30, 15.00),
    "claude-haiku-4-5-20251001": (0.80, 1.00, 0.08, 4.00),
    "claude-opus-3-7-20250219": (15.00, 18.75, 1.50, 75.00),
    "claude-sonnet-3-7-20250219": (3.00, 3.75, 0.30, 15.00),
    "claude-sonnet-3-5-20241022": (3.00, 3.75, 0.30, 15.00),
    "claude-haiku-3-5-20241022": (0.80, 1.00, 0.08, 4.00),
    "claude-opus-3-20240229": (15.00, 18.75, 1.50, 75.00),
    "claude-sonnet-3-20240229": (3.00, 3.75, 0.30, 15.00),
    "claude-haiku-3-20240307": (0.25, 0.30, 0.03, 1.25),
}

# Models that generate no billable API cost (internal/tool-use messages)
_NO_COST_MODELS = {"<synthetic>"}


def _calc_cost(model: str, usage: dict) -> float | None:
    """Return cost in USD, or None if the model is unknown (can't price it)."""
    if model in _NO_COST_MODELS:
        return 0.0
    rates = PRICING.get(model)
    if rates is None:
        # Unknown model — caller must decide how to surface this
        total_tokens = (
            usage.get("input_tokens", 0)
            + usage.get("cache_creation_input_tokens", 0)
            + usage.get("cache_read_input_tokens", 0)
            + usage.get("output_tokens", 0)
        )
        return None if total_tokens > 0 else 0.0
    inp, cw, cr, out = rates
    return (
        usage.get("input_tokens", 0) * inp
        + usage.get("cache_creation_input_tokens", 0) * cw
        + usage.get("cache_read_input_tokens", 0) * cr
        + usage.get("output_tokens", 0) * out
    ) / 1_000_000


# ---------------------------------------------------------------------------
# JSONL content helpers
# ---------------------------------------------------------------------------


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    return "\n".join(
        b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"
    )


def _extract_tool_uses(content) -> list:
    if not isinstance(content, list):
        return []
    return [
        {"name": b.get("name", ""), "input": b.get("input", {})}
        for b in content
        if isinstance(b, dict) and b.get("type") == "tool_use"
    ]


def _clean_user_text(text: str) -> str:
    """Strip IDE/system injection tags injected by Claude Code."""
    prev = None
    while prev != text:
        prev = text
        text = _STRIP_TAG_RE.sub("", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Session parsing
# ---------------------------------------------------------------------------


_COMPACT_SUMMARY_RE = re.compile(
    r"Primary Request and Intent:\s*\n\s*(.*?)(?:\n\s*\d+\.|$)",
    re.DOTALL,
)
_COMPACT_INTRO = "This session is being continued from a previous conversation"
_SENTENCE_END = re.compile(r"[.?!](?:\s|$)")

# Markdown stripping patterns
_MD_CODE_BLOCK = re.compile(r"```.*?```", re.DOTALL)
_MD_INLINE_CODE = re.compile(r"`([^`]+)`")
_MD_BOLD_ITALIC = re.compile(r"\*{1,3}([^*\n]+)\*{1,3}")
_MD_UNDERSCORE = re.compile(r"_{1,3}([^_\n]+)_{1,3}")
_MD_LINK = re.compile(r"\[([^\]]+)\]\([^)]*\)")
_MD_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_MD_BLOCKQUOTE = re.compile(r"^>\s?", re.MULTILINE)


def _first_sentence(text: str) -> str:
    m = _SENTENCE_END.search(text)
    return text[: m.start() + 1].strip() if m else text.strip()


def _strip_markdown(text: str) -> str:
    text = _MD_CODE_BLOCK.sub("", text)
    text = _MD_INLINE_CODE.sub(r"\1", text)
    text = _MD_BOLD_ITALIC.sub(r"\1", text)
    text = _MD_UNDERSCORE.sub(r"\1", text)
    text = _MD_LINK.sub(r"\1", text)
    text = _MD_HEADING.sub("", text)
    text = _MD_BLOCKQUOTE.sub("", text)
    return text.strip()


def _extract_compact_title(text: str) -> str | None:
    """Extract first sentence of 'Primary Request and Intent' from a compact-summary message."""
    if _COMPACT_INTRO not in text:
        return None
    m = _COMPACT_SUMMARY_RE.search(text)
    if not m:
        return None
    body = m.group(1).strip()
    return _first_sentence(body) or None


def parse_session(jsonl_path: Path) -> dict:
    """Parse a single session JSONL file into a structured dict."""
    session_id = jsonl_path.stem
    messages = []
    compact_title = None
    ai_title = None
    cwd = None
    started_at = None
    ended_at = None
    pr_link = None
    model = None
    cost_usd = 0.0
    cost_unknown = False  # True if any message used an unpriced model with tokens
    compact_count = 0

    with open(jsonl_path, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue

            t = obj.get("type")

            if t == "system" and obj.get("subtype") == "compact_boundary":
                compact_count += 1

            elif t == "ai-title":
                ai_title = ai_title or obj.get("aiTitle")

            elif t == "pr-link":
                url = obj.get("url", "")
                if isinstance(url, str) and url.startswith(("https://", "http://")):
                    pr_link = url

            elif t in ("user", "assistant"):
                msg = obj.get("message", {})
                role = msg.get("role", t)
                content = msg.get("content", [])
                ts = obj.get("timestamp")

                if ts:
                    if started_at is None:
                        started_at = ts
                    ended_at = ts

                if cwd is None and t == "user":
                    cwd = obj.get("cwd")

                text = _extract_text(content)
                if role == "user":
                    text = _clean_user_text(text)
                    if compact_title is None:
                        compact_title = _extract_compact_title(text)

                tool_uses = _extract_tool_uses(content) if role == "assistant" else []

                if role == "assistant":
                    msg_model = msg.get("model") or ""
                    if msg_model and msg_model not in _NO_COST_MODELS:
                        model = model or msg_model
                    usage = msg.get("usage")
                    if usage:
                        msg_cost = _calc_cost(msg_model, usage)
                        if msg_cost is None:
                            cost_unknown = True
                        else:
                            cost_usd += msg_cost

                if text.strip() or tool_uses:
                    messages.append(
                        {
                            "role": role,
                            "text": text,
                            "tool_uses": tool_uses,
                            "timestamp": ts,
                            "uuid": obj.get("uuid"),
                            "is_sidechain": obj.get("isSidechain", False),
                        }
                    )

    return {
        "session_id": session_id,
        "compact_title": compact_title,
        "ai_title": ai_title,
        "cwd": cwd,
        "started_at": started_at,
        "ended_at": ended_at,
        "messages": messages,
        "message_count": len(messages),
        "model": model,
        "cost_usd": cost_usd if (not cost_unknown and cost_usd > 0) else None,
        "cost_unknown": cost_unknown,
        "compact_count": compact_count,
        "pr_link": pr_link,
        "path": str(jsonl_path),
    }


def load_all_sessions() -> list:
    """Load metadata for every session across all projects, newest first."""
    sessions = []
    if not PROJECTS_DIR.exists():
        return sessions
    for proj_dir in sorted(PROJECTS_DIR.iterdir()):
        if not proj_dir.is_dir():
            continue
        for jf in sorted(proj_dir.glob("*.jsonl"), key=lambda f: f.stat().st_mtime, reverse=True):
            try:
                s = parse_session(jf)
                s["project_slug"] = proj_dir.name
                sessions.append(s)
            except Exception as exc:
                logging.warning("Failed to parse %s: %s", jf, exc)

    sessions.sort(key=lambda s: s.get("started_at") or "", reverse=True)
    return sessions


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


def load_history() -> dict:
    """Return {project_path: [entry, ...]} sorted newest-first."""
    history: dict = {}
    if not HISTORY_FILE.exists():
        return history
    with open(HISTORY_FILE, encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            raw = raw.strip()
            if not raw:
                continue
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                continue
            proj = obj.get("project", "")
            history.setdefault(proj, []).append(
                {
                    "display": obj.get("display", "").strip(),
                    "timestamp": obj.get("timestamp"),
                    "session_id": obj.get("sessionId"),
                }
            )
    for entries in history.values():
        entries.sort(
            key=lambda e: str(e["timestamp"]) if e["timestamp"] is not None else "", reverse=True
        )
    return history


# ---------------------------------------------------------------------------
# Todos
# ---------------------------------------------------------------------------


def load_todos() -> dict:
    """Return {session_id: [todo, ...]}."""
    todos: dict = {}
    if not TODOS_DIR.exists():
        return todos
    for tf in TODOS_DIR.iterdir():
        if tf.suffix != ".json":
            continue
        try:
            data = json.loads(tf.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(data, list) or not data:
            continue
        # Filename patterns: <session_id>-agent-<agent_id>.json or <pid>.json
        name = tf.stem
        sid = name.split("-agent-")[0] if "-agent-" in name else name
        todos.setdefault(sid, []).extend(data)
    return todos


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------


def fmt_cost(cost) -> str:
    """Format a USD cost for compact display: $0.0042 or $1.23."""
    if not cost:
        return ""
    if cost < 0.01:
        return f"${cost:.4f}"
    return f"${cost:.2f}"


def fmt_ts(ts) -> str:
    if not ts:
        return ""
    try:
        if isinstance(ts, (int, float)):
            dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        else:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.astimezone().strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)[:16]


def session_title(s: dict) -> str:
    # 1. Compact summary — first sentence of "Primary Request and Intent"
    if s.get("compact_title"):
        return s["compact_title"]
    # 2. ai-title event stored in JSONL (no API call — already local)
    if s.get("ai_title"):
        return s["ai_title"]
    # 3. Cleaned first user message — strip markdown, truncate, title-case
    for m in s.get("messages", []):
        if m["role"] == "user" and m["text"].strip():
            t = m["text"].strip()
            if _COMPACT_INTRO in t:
                continue
            clean = _strip_markdown(t)
            if clean:
                return clean[:80].title()
    # 4. Session <date> — last resort
    date = str(s.get("started_at") or "")[:10]
    return f"Session {date}" if date else "Session"


_HOME = str(Path.home())


def strip_home(path: str) -> str:
    """Replace the user's home directory prefix with ~ for display."""
    if path and path.startswith(_HOME):
        return "~" + path[len(_HOME) :]
    return path


def project_display(slug: str, cwd) -> str:
    if cwd:
        return strip_home(cwd)
    return strip_home("/" + slug.lstrip("-").replace("-", "/"))


def group_by_project(sessions: list) -> list:
    """Return list of project dicts sorted by most-recent session."""
    groups: dict = {}
    for s in sessions:
        slug = s["project_slug"]
        if slug not in groups:
            groups[slug] = {
                "slug": slug,
                "label": project_display(slug, s.get("cwd")),
                "cwd": s.get("cwd") or ("/" + slug.lstrip("-").replace("-", "/")),
                "sessions": [],
                "memory_count": 0,
            }
        groups[slug]["sessions"].append(s)

    for slug, group in groups.items():
        memory_dir = PROJECTS_DIR / slug / "memory"
        if memory_dir.exists():
            group["memory_count"] = sum(
                1 for f in memory_dir.iterdir()
                if f.suffix == ".md" and f.name != "MEMORY.md"
            )

    return sorted(
        groups.values(),
        key=lambda g: g["sessions"][0].get("started_at") or "",
        reverse=True,
    )


# ---------------------------------------------------------------------------
# Memory
# ---------------------------------------------------------------------------


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Extract frontmatter from a markdown file. Returns (meta_dict, body)."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta: dict = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            meta[key.strip()] = val.strip()
    return meta, text[end + 5:].strip()


_VALID_MEMORY_TYPES = {"user", "feedback", "project", "reference"}


def load_project_memory(project_slug: str) -> dict:
    """Return parsed memory files for a project slug.

    Returns {"count": int, "index": str|None, "files": [...]}.
    Each file dict: filename, name, description, type, body.
    """
    memory_dir = PROJECTS_DIR / project_slug / "memory"
    if not memory_dir.exists():
        return {"count": 0, "index": None, "files": []}

    index_content: str | None = None
    files: list = []

    for mf in sorted(memory_dir.iterdir()):
        if mf.suffix != ".md":
            continue
        try:
            text = mf.read_text(encoding="utf-8")
        except OSError as exc:
            logging.warning("Could not read memory file %s: %s", mf, exc)
            continue
        if mf.name == "MEMORY.md":
            index_content = text
        else:
            meta, body = _parse_frontmatter(text)
            raw_type = meta.get("type", "")
            files.append({
                "filename": mf.name,
                "name": meta.get("name", mf.stem),
                "description": meta.get("description", ""),
                "type": raw_type if raw_type in _VALID_MEMORY_TYPES else "",
                "body": body,
            })

    return {"count": len(files), "index": index_content, "files": files}
