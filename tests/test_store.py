"""Tests for src/claudio/store.py (user-owned session mirror, PR1)."""

import json
from datetime import datetime, timezone

import pytest

from claudio import store as store_mod
from claudio.store import _SyncLock, read_index, sync

FIXED_NOW = datetime(2026, 5, 31, 14, 0, 0, tzinfo=timezone.utc)


def _raise_oserror(*args, **kwargs):
    raise OSError("simulated failure")


def _make_live(root, tree):
    """Build a live projects tree: {slug: {filename: content}}."""
    for slug, files in tree.items():
        d = root / slug
        d.mkdir(parents=True, exist_ok=True)
        for name, content in files.items():
            (d / name).write_text(content, encoding="utf-8")
    return root


def _paths(tmp_path):
    return {
        "live_projects_dir": tmp_path / "live",
        "store_projects_dir": tmp_path / "store" / "projects",
        "index_path": tmp_path / "store" / "index.json",
        "lock_path": tmp_path / "store" / ".sync.lock",
        "now": FIXED_NOW,
    }


# ---------------------------------------------------------------------------
# Backfill
# ---------------------------------------------------------------------------


def test_backfill_mirrors_all_and_byte_matches(tmp_path):
    p = _paths(tmp_path)
    _make_live(
        p["live_projects_dir"],
        {
            "proj-alpha": {"s1.jsonl": '{"a":1}\n', "s2.jsonl": '{"a":2}\n'},
            "proj-beta": {"s3.jsonl": '{"b":3}\n'},
        },
    )

    summary = sync(**p)

    assert summary["copied"] == 3
    assert summary["updated"] == 0
    assert summary["first_run"] is True
    assert summary["stored_count"] == 3

    # Archive byte-matches every source
    for slug, name in [
        ("proj-alpha", "s1.jsonl"),
        ("proj-alpha", "s2.jsonl"),
        ("proj-beta", "s3.jsonl"),
    ]:
        src = (p["live_projects_dir"] / slug / name).read_bytes()
        dst = (p["store_projects_dir"] / slug / name).read_bytes()
        assert src == dst


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------


def test_sync_idempotent(tmp_path):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})

    sync(**p)
    second = sync(**{**p, "now": datetime(2026, 6, 1, tzinfo=timezone.utc)})

    assert second["copied"] == 0
    assert second["updated"] == 0
    assert second["skipped"] == 1
    assert second["first_run"] is False


# ---------------------------------------------------------------------------
# Append / growth
# ---------------------------------------------------------------------------


def test_appended_session_recopies(tmp_path):
    p = _paths(tmp_path)
    src = p["live_projects_dir"] / "proj-alpha" / "s1.jsonl"
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    sync(**p)

    # Append a line and bump mtime
    src.write_text('{"a":1}\n{"a":2}\n', encoding="utf-8")
    summary = sync(**{**p, "now": datetime(2026, 6, 1, tzinfo=timezone.utc)})

    assert summary["updated"] == 1
    assert summary["copied"] == 0
    dst = p["store_projects_dir"] / "proj-alpha" / "s1.jsonl"
    assert dst.read_text(encoding="utf-8") == '{"a":1}\n{"a":2}\n'


# ---------------------------------------------------------------------------
# No-shrink rule
# ---------------------------------------------------------------------------


def test_no_shrink_does_not_overwrite_and_flags_anomaly(tmp_path):
    p = _paths(tmp_path)
    src = p["live_projects_dir"] / "proj-alpha" / "s1.jsonl"
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n{"a":2}\n{"a":3}\n'}})
    sync(**p)

    # Source truncates to something smaller than the archived copy
    src.write_text('{"a":1}\n', encoding="utf-8")
    summary = sync(**{**p, "now": datetime(2026, 6, 1, tzinfo=timezone.utc)})

    assert summary["updated"] == 0
    assert len(summary["anomalies"]) == 1
    assert summary["anomalies"][0]["key"] == "proj-alpha/s1.jsonl"
    assert "smaller" in summary["anomalies"][0]["reason"]
    # Archive keeps the larger, good copy
    dst = p["store_projects_dir"] / "proj-alpha" / "s1.jsonl"
    assert dst.read_text(encoding="utf-8") == '{"a":1}\n{"a":2}\n{"a":3}\n'


# ---------------------------------------------------------------------------
# Sweep
# ---------------------------------------------------------------------------


def test_swept_session_marked_cold_but_kept(tmp_path):
    p = _paths(tmp_path)
    _make_live(
        p["live_projects_dir"],
        {"proj-alpha": {"s1.jsonl": '{"a":1}\n', "s2.jsonl": '{"a":2}\n'}},
    )
    sync(**p)

    # Claude Code sweeps s1 off disk
    (p["live_projects_dir"] / "proj-alpha" / "s1.jsonl").unlink()
    summary = sync(**{**p, "now": datetime(2026, 6, 1, tzinfo=timezone.utc)})

    assert summary["swept"] == 1
    # Archived copy of the swept session is retained on disk
    assert (p["store_projects_dir"] / "proj-alpha" / "s1.jsonl").exists()

    index = read_index(p["index_path"])
    assert index["sessions"]["proj-alpha/s1.jsonl"]["live"] is False
    assert index["sessions"]["proj-alpha/s1.jsonl"]["swept_at"] == "2026-06-01T00:00:00+00:00"
    assert index["sessions"]["proj-alpha/s2.jsonl"]["live"] is True


def test_swept_session_not_recounted_on_later_runs(tmp_path):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    sync(**p)
    (p["live_projects_dir"] / "proj-alpha" / "s1.jsonl").unlink()
    sync(**{**p, "now": datetime(2026, 6, 1, tzinfo=timezone.utc)})

    third = sync(**{**p, "now": datetime(2026, 6, 2, tzinfo=timezone.utc)})
    assert third["swept"] == 0  # already cold; not counted again


# ---------------------------------------------------------------------------
# Robustness
# ---------------------------------------------------------------------------


def test_corrupt_index_treated_as_empty(tmp_path):
    p = _paths(tmp_path)
    p["index_path"].parent.mkdir(parents=True, exist_ok=True)
    p["index_path"].write_text("{ not json", encoding="utf-8")
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})

    summary = sync(**p)
    assert summary["copied"] == 1
    assert read_index(p["index_path"])["sessions"]["proj-alpha/s1.jsonl"]["live"] is True


def test_missing_live_dir_no_crash(tmp_path):
    p = _paths(tmp_path)  # live dir never created
    summary = sync(**p)
    assert summary["copied"] == 0
    assert summary["live_count"] == 0
    assert summary["stored_count"] == 0


# ---------------------------------------------------------------------------
# Lock
# ---------------------------------------------------------------------------


def test_lock_blocks_concurrent_sync(tmp_path):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})

    # Hold the lock, then attempt a sync: it should bail out without copying.
    with _SyncLock(p["lock_path"]) as held:
        assert held.acquired is True
        summary = sync(**p)

    assert summary["locked_out"] is True
    assert summary["copied"] == 0
    # Nothing was mirrored while locked out
    assert not (p["store_projects_dir"] / "proj-alpha" / "s1.jsonl").exists()


def test_atomic_copy_cleans_up_temp_on_failure(tmp_path, monkeypatch):
    src = tmp_path / "src.jsonl"
    src.write_text("payload", encoding="utf-8")
    dst = tmp_path / "out" / "dst.jsonl"
    monkeypatch.setattr(store_mod.shutil, "copyfile", _raise_oserror)

    with pytest.raises(OSError):
        store_mod._atomic_copy(src, dst)
    # The interrupted copy leaves no partial temp file behind.
    assert list((tmp_path / "out").glob(".sync-*")) == []
    assert not dst.exists()


def test_atomic_write_json_cleans_up_temp_on_failure(tmp_path, monkeypatch):
    target = tmp_path / "out" / "index.json"
    monkeypatch.setattr(store_mod.os, "replace", _raise_oserror)

    with pytest.raises(OSError):
        store_mod._atomic_write_json(target, {"a": 1})
    assert list((tmp_path / "out").glob(".index-*")) == []
    assert not target.exists()


def test_lock_noop_when_fcntl_unavailable(tmp_path, monkeypatch):
    # On platforms without fcntl, locking degrades to a no-op (always acquires).
    monkeypatch.setattr(store_mod, "fcntl", None)
    with _SyncLock(tmp_path / "x.lock") as lock:
        assert lock.acquired is True


# ---------------------------------------------------------------------------
# read_index schema handling
# ---------------------------------------------------------------------------


def test_read_index_wrong_schema_version_returns_empty(tmp_path):
    p = tmp_path / "index.json"
    p.write_text(json.dumps({"schema_version": 999, "sessions": {"x": {}}}), encoding="utf-8")
    idx = read_index(p)
    assert idx["schema_version"] == store_mod.INDEX_SCHEMA_VERSION
    assert idx["sessions"] == {}


def test_read_index_sessions_not_dict_is_coerced(tmp_path):
    p = tmp_path / "index.json"
    p.write_text(json.dumps({"schema_version": 1, "sessions": []}), encoding="utf-8")
    assert read_index(p)["sessions"] == {}


# ---------------------------------------------------------------------------
# Anomaly + graceful-failure branches
# ---------------------------------------------------------------------------


def test_copy_failure_flagged_as_anomaly(tmp_path, monkeypatch):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    monkeypatch.setattr(store_mod, "_atomic_copy", _raise_oserror)

    summary = sync(**p)
    assert summary["copied"] == 0
    assert summary["anomalies"][0]["key"] == "proj-alpha/s1.jsonl"
    assert summary["anomalies"][0]["reason"].startswith("copy failed")


def test_stat_failure_flagged_as_anomaly(tmp_path, monkeypatch):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    monkeypatch.setattr(store_mod, "_stat", _raise_oserror)

    summary = sync(**p)
    assert summary["copied"] == 0
    assert summary["anomalies"][0]["reason"].startswith("stat failed")


def test_update_copy_failure_flagged_as_anomaly(tmp_path, monkeypatch):
    p = _paths(tmp_path)
    src = p["live_projects_dir"] / "proj-alpha" / "s1.jsonl"
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    sync(**p)  # real backfill first

    src.write_text('{"a":1}\n{"a":2}\n', encoding="utf-8")
    monkeypatch.setattr(store_mod, "_atomic_copy", _raise_oserror)
    summary = sync(**{**p, "now": datetime(2026, 6, 1, tzinfo=timezone.utc)})

    assert summary["updated"] == 0
    assert any(a["reason"].startswith("copy failed") for a in summary["anomalies"])


def test_index_write_failure_is_not_fatal(tmp_path, monkeypatch):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    monkeypatch.setattr(store_mod, "_atomic_write_json", _raise_oserror)

    # Copy still succeeds; a failed index write is logged, not raised.
    summary = sync(**p)
    assert summary["copied"] == 1
    assert (p["store_projects_dir"] / "proj-alpha" / "s1.jsonl").exists()


# ---------------------------------------------------------------------------
# sync_on_startup (default paths + summary logging)
# ---------------------------------------------------------------------------


def _point_module_at(tmp_path, monkeypatch):
    live = tmp_path / "live"
    monkeypatch.setattr(store_mod, "LIVE_PROJECTS_DIR", live)
    monkeypatch.setattr(store_mod, "STORE_PROJECTS_DIR", tmp_path / "store" / "projects")
    monkeypatch.setattr(store_mod, "INDEX_PATH", tmp_path / "store" / "index.json")
    monkeypatch.setattr(store_mod, "LOCK_PATH", tmp_path / "store" / ".sync.lock")
    return live


def test_sync_on_startup_mirrors_using_default_paths(tmp_path, monkeypatch):
    live = _point_module_at(tmp_path, monkeypatch)
    _make_live(live, {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})

    summary = store_mod.sync_on_startup()
    assert summary["copied"] == 1
    assert summary["locked_out"] is False
    assert (tmp_path / "store" / "projects" / "proj-alpha" / "s1.jsonl").exists()


def test_sync_on_startup_locked_out_returns_summary(tmp_path, monkeypatch):
    live = _point_module_at(tmp_path, monkeypatch)
    _make_live(live, {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})

    with _SyncLock(store_mod.LOCK_PATH):
        summary = store_mod.sync_on_startup()
    assert summary["locked_out"] is True
    assert summary["copied"] == 0


# ---------------------------------------------------------------------------
# Memory mirroring
# ---------------------------------------------------------------------------


def _make_memory(live_projects_dir, slug, files):
    d = live_projects_dir / slug / "memory"
    d.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (d / name).write_text(content, encoding="utf-8")


def test_memory_files_mirrored_into_store(tmp_path):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    _make_memory(
        p["live_projects_dir"], "proj-alpha", {"MEMORY.md": "# index", "note.md": "a note"}
    )

    summary = sync(**p)
    assert summary["memory_synced"] == 2
    dst = p["store_projects_dir"] / "proj-alpha" / "memory"
    assert dst.joinpath("note.md").read_text(encoding="utf-8") == "a note"
    assert dst.joinpath("MEMORY.md").read_text(encoding="utf-8") == "# index"

    index = read_index(p["index_path"])
    assert "proj-alpha/memory/note.md" in index["memory"]


def test_memory_sync_idempotent(tmp_path):
    p = _paths(tmp_path)
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    _make_memory(p["live_projects_dir"], "proj-alpha", {"note.md": "a note"})
    sync(**p)

    second = sync(**{**p, "now": datetime(2026, 6, 2, tzinfo=timezone.utc)})
    assert second["memory_synced"] == 0


def test_memory_recopies_on_change(tmp_path):
    p = _paths(tmp_path)
    note = p["live_projects_dir"] / "proj-alpha" / "memory" / "note.md"
    _make_live(p["live_projects_dir"], {"proj-alpha": {"s1.jsonl": '{"a":1}\n'}})
    _make_memory(p["live_projects_dir"], "proj-alpha", {"note.md": "original"})
    sync(**p)

    note.write_text("edited and longer", encoding="utf-8")
    summary = sync(**{**p, "now": datetime(2026, 6, 2, tzinfo=timezone.utc)})
    assert summary["memory_synced"] == 1
    dst = p["store_projects_dir"] / "proj-alpha" / "memory" / "note.md"
    assert dst.read_text(encoding="utf-8") == "edited and longer"
