"""User-owned session mirror (PR1: sync + backfill).

Claude Code deletes session files from ``~/.claude/projects/`` on the
``cleanupPeriodDays`` schedule. Claudio derives everything from those files, so
the sweep silently erases history. This module mirrors live session files into
Claudio's own ``store`` directory, which the sweep never touches.

The store holds the same ``.jsonl`` files in the same format, so the existing
parser reads it unchanged. Data flows one way only: live -> store. The store is
append-only; this module never deletes from it.

Scope of this module (PR1): mirror sync + first-run backfill. Stats still read
the live tree. Pointing stats at the store, gzip of cold sessions, and the
health card are later PRs. Standard library only.
"""

import json
import logging
import os
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX platforms
    fcntl = None

LIVE_PROJECTS_DIR = Path.home() / ".claude" / "projects"
STORE_DIR = Path.home() / ".claudio" / "store"
STORE_PROJECTS_DIR = STORE_DIR / "projects"
INDEX_PATH = STORE_DIR / "index.json"
LOCK_PATH = STORE_DIR / ".sync.lock"

INDEX_SCHEMA_VERSION = 1


# ---------------------------------------------------------------------------
# Atomic file helpers
# ---------------------------------------------------------------------------


def _atomic_copy(src, dst):
    """Copy src to dst via a temp file in dst's dir, then rename. Atomic."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(dst.parent), prefix=".sync-", suffix=".tmp")
    os.close(fd)
    try:
        shutil.copyfile(src, tmp)
        os.replace(tmp, dst)
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _atomic_write_json(path, data):
    """Write JSON to path atomically (temp file in same dir, then rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".index-", suffix=".tmp")
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
# Index I/O
# ---------------------------------------------------------------------------


def read_index(path=None):
    """Return the stored index dict, or a fresh empty one if missing/corrupt."""
    if path is None:
        path = INDEX_PATH
    empty = {"schema_version": INDEX_SCHEMA_VERSION, "sessions": {}, "memory": {}}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return empty
    if not isinstance(data, dict) or data.get("schema_version") != INDEX_SCHEMA_VERSION:
        return empty
    if not isinstance(data.get("sessions"), dict):
        data["sessions"] = {}
    if not isinstance(data.get("memory"), dict):
        data["memory"] = {}
    return data


def archive_stats(index=None):
    """Summarize what the store holds, derived from the index (no FS walk)."""
    if index is None:
        index = read_index()
    sessions = index.get("sessions", {})
    memory = index.get("memory", {})
    session_bytes = sum(e.get("size", 0) for e in sessions.values())
    memory_bytes = sum(e.get("size", 0) for e in memory.values())
    return {
        "archived_count": len(sessions),
        "live_count": sum(1 for e in sessions.values() if e.get("live")),
        "archive_only_count": sum(1 for e in sessions.values() if not e.get("live")),
        "memory_count": len(memory),
        "store_bytes": session_bytes + memory_bytes,
        "last_sync_at": index.get("last_sync_at"),
    }


# ---------------------------------------------------------------------------
# Lock (serialize concurrent Claudio instances)
# ---------------------------------------------------------------------------


class _SyncLock:
    """Best-effort exclusive lock via fcntl.flock; released on process exit.

    If the lock is already held by another instance, ``acquired`` is False and
    the caller skips its sync. On platforms without fcntl, locking is a no-op
    (best effort) and ``acquired`` is True.
    """

    def __init__(self, path):
        self.path = Path(path)
        self.acquired = False
        self._fh = None

    def __enter__(self):
        if fcntl is None:
            self.acquired = True
            return self
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = open(self.path, "w", encoding="utf-8")
        try:
            fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.acquired = True
        except OSError:
            self.acquired = False
            self._fh.close()
            self._fh = None
        return self

    def __exit__(self, *exc):
        if self._fh is not None:
            try:
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
            self._fh.close()
            self._fh = None
        return False


# ---------------------------------------------------------------------------
# Sync
# ---------------------------------------------------------------------------


def _stat(path):
    st = path.stat()
    return st.st_size, st.st_mtime


def _mark_live(entry, now_iso):
    """Mark a session entry as live, clearing any stale swept_at from a prior
    sweep (the session has reappeared on disk)."""
    entry["live"] = True
    entry["last_synced"] = now_iso
    entry.pop("swept_at", None)


def _sync_memory_dir(proj_dir, store_projects_dir, mem_index, now_iso, summary):
    """Mirror a project's memory/*.md files into the store.

    Memory files are not append-only (they are edited), so any size or mtime
    change re-copies. Vanished memory files are left in the store (durable);
    they are never deleted.
    """
    mem_src = proj_dir / "memory"
    if not mem_src.exists():
        return
    for mf in sorted(mem_src.glob("*.md")):
        key = f"{proj_dir.name}/memory/{mf.name}"
        try:
            size, mtime = _stat(mf)
        except OSError as exc:
            summary["anomalies"].append({"key": key, "reason": f"stat failed: {exc}"})
            continue
        entry = mem_index.get(key)
        dst = store_projects_dir / proj_dir.name / "memory" / mf.name
        if (
            entry is not None
            and dst.exists()
            and size == entry.get("size")
            and mtime == entry.get("mtime")
        ):
            continue
        try:
            _atomic_copy(mf, dst)
        except OSError as exc:
            summary["anomalies"].append({"key": key, "reason": f"copy failed: {exc}"})
            continue
        mem_index[key] = {"size": size, "mtime": mtime, "last_synced": now_iso}
        summary["memory_synced"] += 1


def sync(
    live_projects_dir=None,
    store_projects_dir=None,
    index_path=None,
    lock_path=None,
    now=None,
):
    """Mirror live session files into the store. Append-only, never deletes.

    Returns a summary dict with counts. Idempotent: an unchanged tree copies
    nothing. All paths are injectable for testing.
    """
    if live_projects_dir is None:
        live_projects_dir = LIVE_PROJECTS_DIR
    if store_projects_dir is None:
        store_projects_dir = STORE_PROJECTS_DIR
    if index_path is None:
        index_path = INDEX_PATH
    if lock_path is None:
        lock_path = LOCK_PATH
    if now is None:
        now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    live_projects_dir = Path(live_projects_dir)
    store_projects_dir = Path(store_projects_dir)

    summary = {
        "copied": 0,
        "updated": 0,
        "skipped": 0,
        "swept": 0,
        "memory_synced": 0,
        "anomalies": [],
        "live_count": 0,
        "stored_count": 0,
        "locked_out": False,
        "first_run": False,
    }

    with _SyncLock(lock_path) as lock:
        if not lock.acquired:
            summary["locked_out"] = True
            return summary

        index = read_index(index_path)
        sessions = index["sessions"]
        summary["first_run"] = len(sessions) == 0
        seen = set()

        if live_projects_dir.exists():
            for proj_dir in sorted(live_projects_dir.iterdir()):
                if not proj_dir.is_dir():
                    continue
                for src in sorted(proj_dir.glob("*.jsonl")):
                    key = f"{proj_dir.name}/{src.name}"
                    seen.add(key)
                    summary["live_count"] += 1
                    dst = store_projects_dir / proj_dir.name / src.name
                    try:
                        src_size, src_mtime = _stat(src)
                    except OSError as exc:
                        summary["anomalies"].append({"key": key, "reason": f"stat failed: {exc}"})
                        continue

                    entry = sessions.get(key)
                    if entry is None or not dst.exists():
                        try:
                            _atomic_copy(src, dst)
                        except OSError as exc:
                            summary["anomalies"].append(
                                {"key": key, "reason": f"copy failed: {exc}"}
                            )
                            continue
                        sessions[key] = {
                            "size": src_size,
                            "mtime": src_mtime,
                            "live": True,
                            "first_seen": now_iso,
                            "last_synced": now_iso,
                        }
                        summary["copied"] += 1
                        continue

                    archived_size = entry.get("size", 0)
                    if src_size < archived_size:
                        # No-shrink rule: a smaller source must never overwrite a
                        # good archived copy. Flag possible corruption / path reuse.
                        summary["anomalies"].append(
                            {
                                "key": key,
                                "reason": f"source smaller than archive "
                                f"({src_size} < {archived_size}); not overwriting",
                            }
                        )
                        _mark_live(entry, now_iso)
                        continue

                    if src_size > archived_size or src_mtime != entry.get("mtime"):
                        try:
                            _atomic_copy(src, dst)
                        except OSError as exc:
                            summary["anomalies"].append(
                                {"key": key, "reason": f"copy failed: {exc}"}
                            )
                            continue
                        entry["size"] = src_size
                        entry["mtime"] = src_mtime
                        _mark_live(entry, now_iso)
                        summary["updated"] += 1
                    else:
                        _mark_live(entry, now_iso)
                        summary["skipped"] += 1

                _sync_memory_dir(proj_dir, store_projects_dir, index["memory"], now_iso, summary)

        # Index entries not seen on disk this run are swept (gone from live).
        # Mark them cold but keep the archived copy. gzip of cold sessions is a
        # later PR (it needs the parser to read .jsonl.gz).
        for key, entry in sessions.items():
            if key not in seen and entry.get("live", True):
                entry["live"] = False
                entry["swept_at"] = now_iso
                summary["swept"] += 1

        summary["stored_count"] = len(sessions)
        index["last_sync_at"] = now_iso
        try:
            _atomic_write_json(index_path, index)
        except OSError as exc:
            logging.warning("Could not write store index %s: %s", index_path, exc)

    return summary


def sync_on_startup():
    """Run the mirror sync once at process startup. Best effort; never blocks launch."""
    try:
        summary = sync()
    except Exception as exc:  # pragma: no cover - defensive, never block launch
        logging.warning("Store sync failed: %s", exc)
        return None

    if summary["locked_out"]:
        logging.info("Store sync skipped: another instance holds the lock.")
        return summary

    logging.info(
        "Store sync: %d copied, %d updated, %d skipped, %d swept, %d memory (%d in store).",
        summary["copied"],
        summary["updated"],
        summary["skipped"],
        summary["swept"],
        summary["memory_synced"],
        summary["stored_count"],
    )
    for anomaly in summary["anomalies"]:
        logging.warning("Store sync anomaly [%s]: %s", anomaly["key"], anomaly["reason"])
    return summary
