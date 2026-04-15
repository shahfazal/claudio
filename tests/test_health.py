"""Tests for src/claudio/health.py."""

import json
from unittest.mock import patch

from claudio.health import (
    check_claude_directory,
    check_environment,
    check_pricing_freshness,
    check_session_schema,
)

# ---------------------------------------------------------------------------
# check_claude_directory
# ---------------------------------------------------------------------------


def test_claude_dir_ok(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "projects").mkdir()
    (claude_dir / "history.jsonl").touch()
    (claude_dir / "todos").mkdir()

    result = check_claude_directory(claude_dir)

    assert result["ok"] is True
    assert result["missing"] == []


def test_claude_dir_missing_root(tmp_path):
    result = check_claude_directory(tmp_path / "no-such-dir")

    assert result["ok"] is False
    assert result["missing"]


def test_claude_dir_missing_subdirs(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    # Only create projects/, omit history.jsonl and todos/
    (claude_dir / "projects").mkdir()

    result = check_claude_directory(claude_dir)

    assert result["ok"] is False
    assert "history.jsonl" in result["missing"]
    assert "todos" in result["missing"]


def test_claude_dir_counts_projects(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    projects = claude_dir / "projects"
    projects.mkdir()
    (projects / "-Users-test-proj1").mkdir()
    (projects / "-Users-test-proj2").mkdir()
    (claude_dir / "history.jsonl").touch()
    (claude_dir / "todos").mkdir()

    result = check_claude_directory(claude_dir)

    assert result["ok"] is True
    assert "2 projects" in result["message"]


# ---------------------------------------------------------------------------
# check_session_schema
# ---------------------------------------------------------------------------


def test_session_schema_ok(tmp_path):
    projects_dir = tmp_path / "projects"
    proj = projects_dir / "-Users-test-myproject"
    proj.mkdir(parents=True)
    jf = proj / "aaaabbbb-0000-0000-0000-000000000001.jsonl"
    jf.write_text(
        '{"type":"user","isSidechain":false,"message":{"role":"user","content":[{"type":"text","text":"hello"}]},'
        '"timestamp":"2026-01-01T10:00:00.000Z","cwd":"/Users/test/myproject"}\n'
    )

    result = check_session_schema(projects_dir)

    assert result["ok"] is True
    assert result["total_count"] == 1
    assert result["parsed_count"] == 1


def test_session_schema_no_projects_dir(tmp_path):
    result = check_session_schema(tmp_path / "no-such-dir")

    assert result["ok"] is False
    assert result["total_count"] == 0


def test_session_schema_no_sessions(tmp_path):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()

    result = check_session_schema(projects_dir)

    assert result["ok"] is True
    assert result["total_count"] == 0


def test_session_schema_parse_exception_returns_error(tmp_path):
    """When parse_session raises, check_session_schema must return ok=False."""
    projects_dir = tmp_path / "projects"
    proj = projects_dir / "-Users-test-proj"
    proj.mkdir(parents=True)
    (proj / "deadbeef-0000-0000-0000-000000000001.jsonl").touch()

    with patch("claudio.health.parse_session", side_effect=KeyError("content")):
        result = check_session_schema(projects_dir)

    assert result["ok"] is False
    assert result["parsed_count"] == 0
    assert result["total_count"] == 1
    assert "Schema check failed" in result["message"]


# ---------------------------------------------------------------------------
# check_pricing_freshness
# ---------------------------------------------------------------------------


def test_pricing_freshness_no_file(tmp_path):
    result = check_pricing_freshness(tmp_path / "no-pricing.json")

    assert result["ok"] is True
    assert result["last_updated"] is None


def test_pricing_freshness_fresh(tmp_path):
    pf = tmp_path / "pricing.json"
    pf.write_text(json.dumps({"last_updated": "2026-04-01"}))

    result = check_pricing_freshness(pf)

    assert result["ok"] is True
    assert result["days_old"] is not None
    assert result["days_old"] < 90


def test_pricing_freshness_stale(tmp_path):
    pf = tmp_path / "pricing.json"
    pf.write_text(json.dumps({"last_updated": "2025-01-01"}))

    result = check_pricing_freshness(pf)

    assert result["ok"] is False
    assert result["days_old"] > 90
    assert "days old" in result["message"]


def test_pricing_freshness_no_date_field(tmp_path):
    pf = tmp_path / "pricing.json"
    pf.write_text(json.dumps({"models": {}}))

    result = check_pricing_freshness(pf)

    assert result["ok"] is True
    assert result["last_updated"] is None


def test_pricing_freshness_corrupt_file(tmp_path):
    pf = tmp_path / "pricing.json"
    pf.write_text("not valid json {{{")

    result = check_pricing_freshness(pf)

    assert result["ok"] is False
    assert "Could not read" in result["message"]


# ---------------------------------------------------------------------------
# check_environment (orchestrator)
# ---------------------------------------------------------------------------


def test_environment_ok(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "projects").mkdir()
    (claude_dir / "history.jsonl").touch()
    (claude_dir / "todos").mkdir()

    result = check_environment(
        claude_dir=claude_dir,
        projects_dir=claude_dir / "projects",
        pricing_path=tmp_path / "no-pricing.json",
    )

    assert result["status"] == "ok"
    assert "claude_dir" in result["checks"]
    assert "schema" in result["checks"]
    assert "pricing" in result["checks"]


def test_environment_error_on_missing_dir(tmp_path):
    result = check_environment(
        claude_dir=tmp_path / "no-claude",
        projects_dir=tmp_path / "no-projects",
        pricing_path=tmp_path / "no-pricing.json",
    )

    assert result["status"] == "error"


def test_environment_warning_on_stale_pricing(tmp_path):
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "projects").mkdir()
    (claude_dir / "history.jsonl").touch()
    (claude_dir / "todos").mkdir()

    pf = tmp_path / "pricing.json"
    pf.write_text(json.dumps({"last_updated": "2025-01-01"}))

    result = check_environment(
        claude_dir=claude_dir,
        projects_dir=claude_dir / "projects",
        pricing_path=pf,
    )

    assert result["status"] == "warning"


# ---------------------------------------------------------------------------
# /health route
# ---------------------------------------------------------------------------


def test_health_route_renders(client):
    with patch(
        "claudio.app.check_environment",
        return_value={
            "status": "ok",
            "checks": {
                "claude_dir": {
                    "ok": True,
                    "message": "Found ~/.claude (5 projects)",
                    "missing": [],
                },
                "schema": {
                    "ok": True,
                    "message": "Schema OK (sampled 1 of 5 sessions)",
                    "parsed_count": 1,
                    "total_count": 5,
                },
                "pricing": {
                    "ok": True,
                    "message": "Using built-in pricing (no user config)",
                    "last_updated": None,
                    "days_old": None,
                },
            },
        },
    ):
        resp = client.get("/health")

    assert resp.status_code == 200
    assert b"Health Status" in resp.data
    assert b"OK" in resp.data


def test_health_route_shows_error(client):
    with patch(
        "claudio.app.check_environment",
        return_value={
            "status": "error",
            "checks": {
                "claude_dir": {
                    "ok": False,
                    "message": "~/.claude not found",
                    "missing": ["~/.claude"],
                },
                "schema": {
                    "ok": False,
                    "message": "projects/ directory not found",
                    "parsed_count": 0,
                    "total_count": 0,
                },
                "pricing": {
                    "ok": True,
                    "message": "Using built-in pricing (no user config)",
                    "last_updated": None,
                    "days_old": None,
                },
            },
        },
    ):
        resp = client.get("/health")

    assert resp.status_code == 200
    assert b"ERROR" in resp.data
    assert b"not found" in resp.data


def test_health_banner_shown_on_error(client):
    with patch(
        "claudio.app.check_environment",
        return_value={
            "status": "error",
            "checks": {
                "claude_dir": {"ok": False, "message": "~/.claude not found", "missing": []},
                "schema": {"ok": True, "message": "Schema OK", "parsed_count": 0, "total_count": 0},
                "pricing": {
                    "ok": True,
                    "message": "Using built-in pricing",
                    "last_updated": None,
                    "days_old": None,
                },
            },
        },
    ):
        with patch("claudio.app.load_all_sessions", return_value=[]):
            resp = client.get("/")

    assert b"health-banner" in resp.data
    assert b"not found" in resp.data


def test_health_banner_hidden_when_ok(client):
    with patch(
        "claudio.app.check_environment",
        return_value={
            "status": "ok",
            "checks": {
                "claude_dir": {"ok": True, "message": "All good", "missing": []},
                "schema": {"ok": True, "message": "Schema OK", "parsed_count": 1, "total_count": 1},
                "pricing": {"ok": True, "message": "Fresh", "last_updated": None, "days_old": None},
            },
        },
    ):
        with patch("claudio.app.load_all_sessions", return_value=[]):
            resp = client.get("/")

    # id="health-banner" is only present when the banner div is rendered
    assert b'id="health-banner"' not in resp.data
