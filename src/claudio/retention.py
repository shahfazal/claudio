"""Session-retention sweep detector (detection-only).

Claude Code deletes session transcripts older than ``cleanupPeriodDays`` on
startup. Claudio derives all of its stats from those transcripts, so a sweep
silently shrinks Claudio's visible history with no signal to the user. This
module checkpoints a few golden numbers each run and warns when the count drops
between runs.

Detection-only: it does not archive, recover, or change how stats are computed.
The only file it writes is the checkpoint. Standard library only.
"""

import json
import logging
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

CHECKPOINT_PATH = Path.home() / ".claudio" / "retention.json"
SETTINGS_PATH = Path.home() / ".claude" / "settings.json"

SCHEMA_VERSION = 1
DEFAULT_CLEANUP_DAYS = 30
SPAN_TRIM_DAYS = 7

_FIX_TEXT = (
    "Set cleanupPeriodDays to a large value (e.g. 3650) in ~/.claude/settings.json "
    "before the next launch. Do not set it to 0, which disables transcript "
    "persistence entirely."
)
_NOTE_TEXT = "Claudio cannot recover sessions already deleted from disk."

_UNSET = object()

# Result of the single startup detection, stashed so the per-request health
# check can surface it without re-detecting or re-writing the checkpoint.
_STARTUP_RESULT: dict | None = None


# ---------------------------------------------------------------------------
# Inputs
# ---------------------------------------------------------------------------


def _to_utc_dt(ts):
    """Parse a session timestamp (epoch-ms int or ISO string) to UTC datetime.

    Returns None for anything unparseable. Never raises.
    """
    if isinstance(ts, bool):  # bool is an int subclass; reject it explicitly
        return None
    if isinstance(ts, (int, float)):
        try:
            return datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        except (OSError, ValueError, OverflowError):
            return None
    if isinstance(ts, str):
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
    return None


def golden_numbers(sessions):
    """Return (sessions_on_disk, earliest_session_ts_iso) for a session list."""
    count = len(sessions)
    earliest = None
    for s in sessions:
        dt = _to_utc_dt(s.get("started_at"))
        if dt is not None and (earliest is None or dt < earliest):
            earliest = dt
    return count, (earliest.isoformat() if earliest is not None else None)


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


def read_claude_version():
    """Best-effort ``claude --version``. Returns a version string or None.

    Never raises and never blocks longer than a few seconds.
    """
    try:
        proc = subprocess.run(
            ["claude", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    line = (proc.stdout or "").strip()
    if not line:
        return None
    token = line.split()[0]
    return token or None


# ---------------------------------------------------------------------------
# Checkpoint I/O
# ---------------------------------------------------------------------------


def read_checkpoint(path=None):
    """Return the stored checkpoint dict, or None if missing/corrupt/wrong schema."""
    if path is None:
        path = CHECKPOINT_PATH
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get("schema_version") != SCHEMA_VERSION:
        return None
    return data


def write_checkpoint(path, data):
    """Write the checkpoint atomically (temp file in the same dir, then rename)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".retention-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        os.replace(tmp, path)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _format_run_date(last_run_at):
    dt = _to_utc_dt(last_run_at)
    return dt.strftime("%Y-%m-%d %H:%M UTC") if dt is not None else "the previous run"


def _warning_message(signals, lost, last_run_at, curr):
    when = _format_run_date(last_run_at)
    parts = []
    if "sweep" in signals:
        n = lost if lost is not None else "Some"
        parts.append(f"{n} session(s) appear to have disappeared from disk since {when}.")
    if "span_trim" in signals:
        parts.append(
            f"The oldest visible session appears to have moved forward by more than "
            f"{SPAN_TRIM_DAYS} days since {when}."
        )
    setting = "cleanupPeriodDays is {}{}.".format(
        curr["cleanup_period_days"],
        " (default)" if curr["cleanup_is_default"] else "",
    )
    parts.append(setting + " This looks like Claude Code's retention sweep.")
    return " ".join(parts)


def evaluate(prev, curr):
    """Compare current golden numbers against the previous checkpoint.

    Returns a health-style result dict (``ok``/``message`` plus detail fields).
    """
    result = {
        "ok": True,
        "message": "No session loss detected",
        "lost": None,
        "signals": [],
        "cleanup_period_days": curr["cleanup_period_days"],
        "cleanup_is_default": curr["cleanup_is_default"],
        "last_run_at": prev.get("last_run_at") if prev else None,
        "first_run": prev is None,
        "fix": _FIX_TEXT,
        "note": _NOTE_TEXT,
    }

    if prev is None:
        result["message"] = "Retention baseline seeded (first run)"
        return result

    signals = []
    lost = None

    prev_count = prev.get("sessions_on_disk")
    curr_count = curr["sessions_on_disk"]
    if isinstance(prev_count, int) and not isinstance(prev_count, bool):
        if curr_count < prev_count:
            lost = prev_count - curr_count
            signals.append("sweep")

    prev_dt = _to_utc_dt(prev.get("earliest_session_ts"))
    curr_dt = _to_utc_dt(curr["earliest_session_ts"])
    if prev_dt is not None and curr_dt is not None:
        if (curr_dt - prev_dt).days > SPAN_TRIM_DAYS:
            signals.append("span_trim")

    if not signals:
        return result

    result["ok"] = False
    result["lost"] = lost
    result["signals"] = signals
    result["message"] = _warning_message(signals, lost, prev.get("last_run_at"), curr)
    return result


def run_detection(
    sessions,
    checkpoint_path=None,
    settings_path=None,
    now=None,
    claude_code_version=_UNSET,
):
    """Scan, compare against the checkpoint, write a fresh checkpoint, return result.

    All inputs are injectable for testing. The checkpoint is always rewritten
    (after the comparison) so the next run compares against this run.
    """
    if checkpoint_path is None:
        checkpoint_path = CHECKPOINT_PATH
    if settings_path is None:
        settings_path = SETTINGS_PATH
    if now is None:
        now = datetime.now(timezone.utc)
    if claude_code_version is _UNSET:
        claude_code_version = read_claude_version()

    count, earliest = golden_numbers(sessions)
    cleanup_days, is_default = read_cleanup_period(settings_path)

    prev = read_checkpoint(checkpoint_path)
    curr = {
        "sessions_on_disk": count,
        "earliest_session_ts": earliest,
        "cleanup_period_days": cleanup_days,
        "cleanup_is_default": is_default,
    }
    result = evaluate(prev, curr)

    checkpoint = {
        "schema_version": SCHEMA_VERSION,
        "last_run_at": now.isoformat(),
        "sessions_on_disk": count,
        "earliest_session_ts": earliest,
        "cleanup_period_days": cleanup_days,
        "cleanup_is_default": is_default,
        "claude_code_version": claude_code_version,
    }
    try:
        write_checkpoint(checkpoint_path, checkpoint)
    except OSError as exc:
        logging.warning("Could not write retention checkpoint %s: %s", checkpoint_path, exc)

    return result


def detect_on_startup():
    """Run detection once at process startup. Stash and log the result.

    Best effort: any failure is logged and swallowed so it never blocks launch.
    """
    global _STARTUP_RESULT
    try:
        from claudio.parsers import load_all_sessions

        sessions, _failures = load_all_sessions()
        result = run_detection(sessions)
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
