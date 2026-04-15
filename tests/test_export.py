"""Tests for /export/sessions.json route."""

import json
from unittest.mock import patch


def test_export_returns_json_download(client):
    with patch("claudio.app.load_all_sessions", return_value=[]):
        resp = client.get("/export/sessions.json")

    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    assert "attachment" in resp.headers["Content-Disposition"]
    assert "claudio-export-" in resp.headers["Content-Disposition"]
    assert resp.headers["Content-Disposition"].endswith('.json"')


def test_export_structure(client):
    with patch("claudio.app.load_all_sessions", return_value=[]):
        resp = client.get("/export/sessions.json")

    data = json.loads(resp.data)
    assert data["claudio_version"] == "0.4.0"
    assert "export_date" in data
    assert "claude_directory" in data
    assert data["total_sessions"] == 0
    assert data["parsed_sessions"] == 0
    assert data["failed_sessions"] == []
    assert data["sessions"] == []
    assert "pricing_config" in data


def test_export_session_shape(client, sample_jsonl):
    from claudio.parsers import parse_session

    session = parse_session(sample_jsonl)
    session["project_slug"] = "-Users-test-myproject"

    with patch("claudio.app.load_all_sessions", return_value=[session]):
        resp = client.get("/export/sessions.json")

    data = json.loads(resp.data)
    assert data["total_sessions"] == 1
    s = data["sessions"][0]
    assert s["uuid"] == session["session_id"]
    assert s["title"] == "Fix the login bug."
    assert "cost" in s
    assert "total" in s["cost"]
    assert "project" in s
    assert s["project"]["slug"] == "-Users-test-myproject"
    assert "messages" in s
    assert "compactions" in s
    assert "model" in s
    # Full message content must NOT be present
    assert "text" not in s
    assert "content" not in s


def test_export_pricing_config_present(client):
    with patch("claudio.app.load_all_sessions", return_value=[]):
        resp = client.get("/export/sessions.json")

    data = json.loads(resp.data)
    pricing = data["pricing_config"]
    assert "models" in pricing
    # At least one model entry should be present
    assert len(pricing["models"]) > 0
    first = next(iter(pricing["models"].values()))
    assert "input" in first
    assert "output" in first


def test_export_button_in_nav(client):
    with patch("claudio.app.load_all_sessions", return_value=[]):
        resp = client.get("/")

    html = resp.data.decode()
    assert "/export/sessions.json" in html
    assert "export" in html
