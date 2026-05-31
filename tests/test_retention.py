"""Tests for src/claudio/retention.py (session-retention sweep detector)."""

import json
from datetime import datetime, timezone

from claudio.retention import (
    SCHEMA_VERSION,
    _to_utc_dt,
    evaluate,
    golden_numbers,
    read_checkpoint,
    read_cleanup_period,
    run_detection,
    write_checkpoint,
)

FIXED_NOW = datetime(2026, 5, 31, 14, 0, 0, tzinfo=timezone.utc)


def _sessions(*timestamps):
    """Build a minimal session list with the given started_at values."""
    return [{"started_at": ts} for ts in timestamps]


def _run(sessions, tmp_path, **kw):
    """run_detection with the checkpoint and settings pinned under tmp_path."""
    kw.setdefault("checkpoint_path", tmp_path / "retention.json")
    kw.setdefault("settings_path", tmp_path / "settings.json")
    kw.setdefault("now", FIXED_NOW)
    kw.setdefault("claude_code_version", "2.1.150")
    return run_detection(sessions, **kw)


# ---------------------------------------------------------------------------
# _to_utc_dt
# ---------------------------------------------------------------------------


def test_to_utc_dt_parses_iso_with_z():
    dt = _to_utc_dt("2026-04-01T09:12:00Z")
    assert dt == datetime(2026, 4, 1, 9, 12, 0, tzinfo=timezone.utc)


def test_to_utc_dt_parses_epoch_millis():
    # 2026-04-01T09:12:00Z in epoch milliseconds
    ms = int(datetime(2026, 4, 1, 9, 12, 0, tzinfo=timezone.utc).timestamp() * 1000)
    assert _to_utc_dt(ms) == datetime(2026, 4, 1, 9, 12, 0, tzinfo=timezone.utc)


def test_to_utc_dt_rejects_garbage_and_bool():
    assert _to_utc_dt("not-a-date") is None
    assert _to_utc_dt(None) is None
    assert _to_utc_dt(True) is None


# ---------------------------------------------------------------------------
# golden_numbers
# ---------------------------------------------------------------------------


def test_golden_numbers_counts_and_finds_earliest():
    count, earliest = golden_numbers(
        _sessions("2026-04-10T00:00:00Z", "2026-04-01T09:12:00Z", "2026-04-20T00:00:00Z")
    )
    assert count == 3
    assert earliest == "2026-04-01T09:12:00+00:00"


def test_golden_numbers_empty():
    assert golden_numbers([]) == (0, None)


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
    p.write_text("{ this is not json")
    assert read_cleanup_period(p) == (30, True)


# ---------------------------------------------------------------------------
# checkpoint I/O
# ---------------------------------------------------------------------------


def test_write_checkpoint_is_atomic_and_leaves_no_temp(tmp_path):
    path = tmp_path / "retention.json"
    write_checkpoint(path, {"schema_version": SCHEMA_VERSION, "sessions_on_disk": 5})

    assert json.loads(path.read_text())["sessions_on_disk"] == 5
    # No leftover temp files from the atomic write
    assert [p.name for p in tmp_path.iterdir()] == ["retention.json"]


def test_read_checkpoint_rejects_corrupt_and_wrong_schema(tmp_path):
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{ not json")
    assert read_checkpoint(corrupt) is None

    wrong = tmp_path / "wrong.json"
    wrong.write_text(json.dumps({"schema_version": 999, "sessions_on_disk": 1}))
    assert read_checkpoint(wrong) is None

    assert read_checkpoint(tmp_path / "missing.json") is None


# ---------------------------------------------------------------------------
# evaluate (pure detection logic)
# ---------------------------------------------------------------------------


def _curr(count, earliest, days=30, default=True):
    return {
        "sessions_on_disk": count,
        "earliest_session_ts": earliest,
        "cleanup_period_days": days,
        "cleanup_is_default": default,
    }


def test_evaluate_first_run_no_warning():
    result = evaluate(None, _curr(10, "2026-04-01T00:00:00Z"))
    assert result["ok"] is True
    assert result["first_run"] is True
    assert result["signals"] == []


def test_evaluate_growth_no_warning():
    prev = {"sessions_on_disk": 5, "earliest_session_ts": "2026-04-01T00:00:00Z"}
    result = evaluate(prev, _curr(8, "2026-04-01T00:00:00Z"))
    assert result["ok"] is True
    assert result["signals"] == []


def test_evaluate_equal_no_warning():
    prev = {"sessions_on_disk": 5, "earliest_session_ts": "2026-04-01T00:00:00Z"}
    result = evaluate(prev, _curr(5, "2026-04-01T00:00:00Z"))
    assert result["ok"] is True
    assert result["signals"] == []


def test_evaluate_sweep_reports_lost_count():
    prev = {
        "sessions_on_disk": 12,
        "earliest_session_ts": "2026-04-01T00:00:00Z",
        "last_run_at": "2026-05-30T10:00:00Z",
    }
    result = evaluate(prev, _curr(4, "2026-04-01T00:00:00Z", days=30, default=True))
    assert result["ok"] is False
    assert result["lost"] == 8
    assert "sweep" in result["signals"]
    assert "8 session(s)" in result["message"]
    assert "cleanupPeriodDays is 30 (default)" in result["message"]


def test_evaluate_span_trim_warns():
    prev = {"sessions_on_disk": 10, "earliest_session_ts": "2026-04-01T00:00:00Z"}
    # earliest jumps forward 9 days (> 7) while count holds steady
    result = evaluate(prev, _curr(10, "2026-04-10T00:00:00Z"))
    assert result["ok"] is False
    assert result["signals"] == ["span_trim"]
    assert result["lost"] is None


def test_evaluate_span_trim_within_threshold_no_warning():
    prev = {"sessions_on_disk": 10, "earliest_session_ts": "2026-04-01T00:00:00Z"}
    # 7-day jump is not "more than 7 days"
    result = evaluate(prev, _curr(10, "2026-04-08T00:00:00Z"))
    assert result["ok"] is True
    assert result["signals"] == []


def test_evaluate_combined_single_result():
    prev = {"sessions_on_disk": 12, "earliest_session_ts": "2026-04-01T00:00:00Z"}
    result = evaluate(prev, _curr(4, "2026-04-15T00:00:00Z"))
    assert result["ok"] is False
    assert set(result["signals"]) == {"sweep", "span_trim"}
    assert result["lost"] == 8


def test_evaluate_survives_checkpoint_missing_count():
    # A prev checkpoint without sessions_on_disk must not crash the comparison.
    prev = {"earliest_session_ts": "2026-04-01T00:00:00Z"}
    result = evaluate(prev, _curr(4, "2026-04-01T00:00:00Z"))
    assert result["ok"] is True


# ---------------------------------------------------------------------------
# run_detection (orchestration + checkpoint persistence)
# ---------------------------------------------------------------------------


def test_run_detection_first_run_seeds_no_warning(tmp_path):
    result = _run(_sessions("2026-04-01T00:00:00Z", "2026-04-10T00:00:00Z"), tmp_path)

    assert result["ok"] is True
    assert result["first_run"] is True

    cp = read_checkpoint(tmp_path / "retention.json")
    assert cp["schema_version"] == SCHEMA_VERSION
    assert cp["sessions_on_disk"] == 2
    assert cp["last_run_at"] == FIXED_NOW.isoformat()
    assert cp["claude_code_version"] == "2.1.150"


def test_run_detection_unchanged_refreshes_checkpoint(tmp_path):
    sessions = _sessions("2026-04-01T00:00:00Z", "2026-04-10T00:00:00Z")
    _run(sessions, tmp_path, now=datetime(2026, 5, 30, tzinfo=timezone.utc))

    result = _run(sessions, tmp_path, now=FIXED_NOW)
    assert result["ok"] is True
    assert result["signals"] == []

    cp = read_checkpoint(tmp_path / "retention.json")
    assert cp["last_run_at"] == FIXED_NOW.isoformat()


def test_run_detection_fewer_files_warns_with_setting(tmp_path):
    (tmp_path / "settings.json").write_text(json.dumps({"cleanupPeriodDays": 30}))
    full = _sessions(*[f"2026-04-{d:02d}T00:00:00Z" for d in range(1, 13)])
    _run(full, tmp_path, now=datetime(2026, 5, 30, 10, 0, tzinfo=timezone.utc))

    swept = _sessions(*[f"2026-05-{d:02d}T00:00:00Z" for d in range(25, 29)])
    result = _run(swept, tmp_path, now=FIXED_NOW)

    assert result["ok"] is False
    assert result["lost"] == 8
    assert result["cleanup_period_days"] == 30
    assert result["cleanup_is_default"] is False


def test_run_detection_corrupt_checkpoint_treated_as_first_run(tmp_path):
    (tmp_path / "retention.json").write_text("{ corrupt")
    result = _run(_sessions("2026-04-01T00:00:00Z"), tmp_path)

    assert result["ok"] is True
    assert result["first_run"] is True
    # The corrupt file is replaced with a valid checkpoint
    assert read_checkpoint(tmp_path / "retention.json")["sessions_on_disk"] == 1


def test_run_detection_missing_settings_reports_default(tmp_path):
    result = _run(_sessions("2026-04-01T00:00:00Z"), tmp_path)
    cp = read_checkpoint(tmp_path / "retention.json")
    assert cp["cleanup_period_days"] == 30
    assert cp["cleanup_is_default"] is True
    assert result["cleanup_is_default"] is True


def test_run_detection_version_unavailable_stored_as_null(tmp_path):
    _run(_sessions("2026-04-01T00:00:00Z"), tmp_path, claude_code_version=None)
    cp = read_checkpoint(tmp_path / "retention.json")
    assert cp["claude_code_version"] is None


# ---------------------------------------------------------------------------
# Privacy: the checkpoint stores only counts, timestamps, and config integers
# ---------------------------------------------------------------------------


def test_checkpoint_contains_no_paths_or_identifiers(tmp_path):
    _run(_sessions("2026-04-01T00:00:00Z", "2026-04-10T00:00:00Z"), tmp_path)
    raw = (tmp_path / "retention.json").read_text()

    assert set(json.loads(raw).keys()) == {
        "schema_version",
        "last_run_at",
        "sessions_on_disk",
        "earliest_session_ts",
        "cleanup_period_days",
        "cleanup_is_default",
        "claude_code_version",
    }
    for needle in ("/Users", "faz", "shahfazal", ".jsonl", "/home/"):
        assert needle not in raw
