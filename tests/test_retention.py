"""Tests for src/claudio/retention.py (archive-calibrated retention detector)."""

import json
from datetime import datetime, timezone

import claudio.retention as ret
import claudio.store as store_mod
from claudio.retention import (
    _mtime_dt,
    _to_utc_dt,
    detect_on_startup,
    evaluate_archive,
    read_cleanup_period,
    startup_result,
)


def _epoch(y, m, d):
    return datetime(y, m, d, tzinfo=timezone.utc).timestamp()


def _index(sessions=None, memory=None, last="2026-06-02T00:00:00+00:00"):
    return {
        "schema_version": 1,
        "sessions": sessions or {},
        "memory": memory or {},
        "last_sync_at": last,
    }


def _cold(swept_at, mtime, size=100):
    return {"size": size, "mtime": mtime, "live": False, "swept_at": swept_at}


# ---------------------------------------------------------------------------
# _to_utc_dt / _mtime_dt
# ---------------------------------------------------------------------------


def test_to_utc_dt_parses_iso_with_z():
    assert _to_utc_dt("2026-04-01T09:12:00Z") == datetime(2026, 4, 1, 9, 12, tzinfo=timezone.utc)


def test_to_utc_dt_rejects_nonstring_and_garbage():
    assert _to_utc_dt(123) is None
    assert _to_utc_dt(None) is None
    assert _to_utc_dt("not-a-date") is None


def test_mtime_dt_parses_epoch_seconds():
    secs = datetime(2026, 4, 1, tzinfo=timezone.utc).timestamp()
    assert _mtime_dt(secs) == datetime(2026, 4, 1, tzinfo=timezone.utc)


def test_mtime_dt_rejects_nonnumeric_and_bool():
    assert _mtime_dt("x") is None
    assert _mtime_dt(True) is None
    assert _mtime_dt(None) is None


# ---------------------------------------------------------------------------
# read_cleanup_period
# ---------------------------------------------------------------------------


def test_cleanup_period_present(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"cleanupPeriodDays": 3650}))
    assert read_cleanup_period(p) == (3650, False)


def test_cleanup_period_absent_key_uses_default(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text(json.dumps({"theme": "dark"}))
    assert read_cleanup_period(p) == (30, True)


def test_cleanup_period_missing_file_uses_default(tmp_path):
    assert read_cleanup_period(tmp_path / "nope.json") == (30, True)


def test_cleanup_period_malformed_file_uses_default(tmp_path):
    p = tmp_path / "settings.json"
    p.write_text("{ not json")
    assert read_cleanup_period(p) == (30, True)


# ---------------------------------------------------------------------------
# evaluate_archive
# ---------------------------------------------------------------------------


def test_evaluate_archive_empty_is_in_sync():
    r = evaluate_archive(_index(), 30, True)
    assert r["ok"] is True
    assert r["archive_only_count"] == 0
    assert "in sync" in r["message"]


def test_evaluate_archive_all_live_no_warning():
    sessions = {"p/a.jsonl": {"size": 10, "mtime": _epoch(2026, 5, 1), "live": True}}
    r = evaluate_archive(_index(sessions), 30, True)
    assert r["ok"] is True
    assert r["live_count"] == 1
    assert r["archive_only_count"] == 0


def test_evaluate_archive_routine_sweep_is_preserved_not_alarmed():
    # Swept after aging ~49 days, well past the 30-day window: routine.
    sessions = {"p/a.jsonl": _cold("2026-05-20T00:00:00+00:00", _epoch(2026, 4, 1))}
    r = evaluate_archive(_index(sessions), 30, True)
    assert r["ok"] is True
    assert r["archive_only_count"] == 1
    assert r["unexpected_count"] == 0
    assert "preserved in your archive" in r["message"]


def test_evaluate_archive_younger_than_window_is_unexpected():
    # Vanished only 5 days after last activity, but window is 30 days.
    sessions = {"p/a.jsonl": _cold("2026-05-20T00:00:00+00:00", _epoch(2026, 5, 15))}
    r = evaluate_archive(_index(sessions), 30, True)
    assert r["ok"] is False
    assert r["unexpected_count"] == 1
    assert "sooner than" in r["message"]


def test_evaluate_archive_high_cleanup_flags_vanished_session():
    # The "3650 bug": a session vanished but the window is 10 years, so the
    # retention sweep cannot explain it -> unexpected, not routine.
    sessions = {"p/a.jsonl": _cold("2026-05-20T00:00:00+00:00", _epoch(2026, 4, 1))}
    r = evaluate_archive(_index(sessions), 3650, False)
    assert r["ok"] is False
    assert r["unexpected_count"] == 1
    assert "cleanupPeriodDays 3650" in r["message"]


def test_evaluate_archive_undatable_cold_session_is_routine():
    sessions = {"p/a.jsonl": {"size": 10, "mtime": None, "live": False}}  # no swept_at
    r = evaluate_archive(_index(sessions), 30, True)
    assert r["ok"] is True
    assert r["archive_only_count"] == 1
    assert r["unexpected_count"] == 0


def test_evaluate_archive_includes_store_stats():
    sessions = {"p/a.jsonl": {"size": 100, "mtime": _epoch(2026, 5, 1), "live": True}}
    memory = {"p/memory/x.md": {"size": 50}}
    r = evaluate_archive(_index(sessions, memory), 30, True)
    assert r["archived_count"] == 1
    assert r["memory_count"] == 1
    assert r["store_bytes"] == 150
    assert r["last_sync_at"] == "2026-06-02T00:00:00+00:00"


# ---------------------------------------------------------------------------
# detect_on_startup
# ---------------------------------------------------------------------------


def test_detect_on_startup_reads_index_and_stashes(monkeypatch):
    sessions = {"p/a.jsonl": _cold("2026-05-20T00:00:00+00:00", _epoch(2026, 5, 15))}
    monkeypatch.setattr(store_mod, "read_index", lambda *a, **k: _index(sessions))
    monkeypatch.setattr(ret, "read_cleanup_period", lambda *a, **k: (30, True))

    result = detect_on_startup()
    assert result["ok"] is False  # younger-than-window -> unexpected
    assert result["unexpected_count"] == 1
    assert startup_result() is result
