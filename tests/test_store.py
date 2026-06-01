"""Tests for src/claudio/store.py (user-owned session mirror, PR1)."""

from datetime import datetime, timezone

from claudio.store import _SyncLock, read_index, sync

FIXED_NOW = datetime(2026, 5, 31, 14, 0, 0, tzinfo=timezone.utc)


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
