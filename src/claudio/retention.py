"""Session-retention detector, calibrated against the durable store.

Claude Code deletes session transcripts from ``~/.claude/projects/`` on the
``cleanupPeriodDays`` schedule. Since PR1/PR2a, Claudio mirrors those files into
its own store before they are swept, so the loss is no longer silent or
permanent. This module reads the store index and reports what was swept,
calibrated against ``cleanupPeriodDays``:

- Sessions that vanished after aging past ``cleanupPeriodDays`` are routine
  retention and are reported as preserved (informational, no alarm).
- Sessions that vanished sooner than ``cleanupPeriodDays`` explains are flagged
  as unexpected (possible manual or external deletion), since the configured
  window does not account for them.

Read-only over the store index. Standard library only.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
DEFAULT_CLEANUP_DAYS = 30

_FIX_TEXT = (
    "Set cleanupPeriodDays to a large value (e.g. 3650) in ~/.claude/settings.json "
    "before the next launch. Do not set it to 0, which disables transcript "
    "persistence entirely."
)
_NOTE_TEXT = "Claudio cannot recover sessions deleted from disk before they were mirrored."

# Result of the single startup detection, stashed so the per-request health
# check can surface it without re-reading the store.
_STARTUP_RESULT: dict | None = None


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def _to_utc_dt(ts):
    """Parse an ISO-8601 string to a UTC datetime. Returns None if unparseable."""
    if not isinstance(ts, str):
        return None
    s = ts.strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _mtime_dt(mtime):
    """Parse an epoch-seconds file mtime to a UTC datetime. None if unparseable."""
    if isinstance(mtime, bool) or not isinstance(mtime, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(mtime, tz=timezone.utc)
    except (OSError, ValueError, OverflowError):
        return None


def read_cleanup_period(settings_path=None):
    """Return (cleanup_period_days, is_default) from ~/.claude/settings.json.

    Absent key or missing/malformed file falls back to the effective default of
    30 days with is_default=True. Never raises.
    """
    if settings_path is None:
        settings_path = SETTINGS_PATH
    try:
        data = json.loads(Path(settings_path).read_text(encoding="utf-8"))
        val = data.get("cleanupPeriodDays")
        if not isinstance(val, bool) and isinstance(val, (int, float)) and val > 0:
            return int(val), False
    except (OSError, ValueError, json.JSONDecodeError):
        pass
    return DEFAULT_CLEANUP_DAYS, True


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _archive_message(r):
    setting = "cleanupPeriodDays {}{}".format(
        r["cleanup_period_days"], " (default)" if r["cleanup_is_default"] else ""
    )
    if r["archive_only_count"] == 0:
        return (
            f"Live history and archive are in sync ({r['live_count']} session(s)); nothing swept."
        )
    if r["unexpected_count"] == 0:
        return (
            f"{r['archive_only_count']} session(s) were swept from disk by Claude Code's "
            f"retention ({setting}) and are preserved in your archive."
        )
    return (
        f"{r['unexpected_count']} of {r['archive_only_count']} archived session(s) vanished from "
        f"disk sooner than {setting} explains (possible manual or external deletion). "
        "All are preserved in your archive."
    )


def evaluate_archive(index, cleanup_period_days, cleanup_is_default):
    """Classify swept sessions in the store index against cleanupPeriodDays.

    Returns a health-style result dict. ``ok`` is False only when at least one
    session vanished sooner than the retention window explains.
    """
    from claudio.store import archive_stats

    stats = archive_stats(index)
    sessions = index.get("sessions", {})

    unexpected = 0
    for entry in sessions.values():
        if entry.get("live"):
            continue
        swept_dt = _to_utc_dt(entry.get("swept_at"))
        mtime_dt = _mtime_dt(entry.get("mtime"))
        # Only flag when we can date it AND it is younger than the window. An
        # undatable swept session is treated as routine, not alarmed.
        if swept_dt is not None and mtime_dt is not None:
            if (swept_dt - mtime_dt).days < cleanup_period_days:
                unexpected += 1

    result = {
        **stats,
        "ok": unexpected == 0,
        "unexpected_count": unexpected,
        "cleanup_period_days": cleanup_period_days,
        "cleanup_is_default": cleanup_is_default,
        "fix": _FIX_TEXT,
        "note": _NOTE_TEXT,
    }
    result["message"] = _archive_message(result)
    return result


def detect_on_startup():
    """Read the store index once at startup, classify, stash and log the result.

    Best effort: any failure is logged and swallowed so it never blocks launch.
    """
    global _STARTUP_RESULT
    try:
        from claudio.store import read_index

        index = read_index()
        cleanup_days, is_default = read_cleanup_period()
        result = evaluate_archive(index, cleanup_days, is_default)
    except Exception as exc:  # pragma: no cover - defensive, never block launch
        logging.warning("Retention detection failed: %s", exc)
        return None

    _STARTUP_RESULT = result
    if not result["ok"]:
        logging.warning("Retention: %s", result["message"])
    return result


def startup_result():
    """Return the stashed startup detection result, or None if it has not run."""
    return _STARTUP_RESULT
