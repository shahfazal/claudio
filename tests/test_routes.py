"""Tests for Flask routes."""

from unittest.mock import patch

from claudio.parsers import parse_session


def test_index_returns_200(client):
    with patch("claudio.app.load_all_sessions", return_value=[]):
        resp = client.get("/")
    assert resp.status_code == 200
    assert b"claudio" in resp.data


def test_index_lists_sessions(client, sample_jsonl):
    session = parse_session(sample_jsonl)
    session["project_slug"] = "-Users-test-myproject"

    with patch("claudio.app.load_all_sessions", return_value=[session]):
        resp = client.get("/")

    assert resp.status_code == 200
    assert b"Fix the login bug" in resp.data


def test_session_view_invalid_id(client):
    resp = client.get("/session/does-not-exist")
    assert resp.status_code == 400


def test_session_view_not_found(client):
    resp = client.get("/session/ffffffff-ffff-ffff-ffff-ffffffffffff")
    assert resp.status_code == 404


def test_session_view_renders(client, sample_jsonl, tmp_path, monkeypatch):
    """Patch PROJECTS_DIR so the route can find the fixture session."""
    import claudio.app as app_module

    monkeypatch.setattr(app_module, "PROJECTS_DIR", sample_jsonl.parent.parent)
    resp = client.get("/session/aaaabbbb-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    assert b"Fix the login bug" in resp.data
    assert b"Can you fix the login bug?" in resp.data


def test_index_session_title_precomputed(client, sample_jsonl):
    """Route must set s['title'] before passing sessions to the template."""
    session = parse_session(sample_jsonl)
    session["project_slug"] = "-Users-test-myproject"
    assert "title" not in session  # not set by parser

    with patch("claudio.app.load_all_sessions", return_value=[session]):
        resp = client.get("/")

    assert resp.status_code == 200
    assert "title" in session  # route must have set it
    assert session["title"] == "Fix the login bug."


def test_theme_toggle_elements_present(client):
    with patch("claudio.app.load_all_sessions", return_value=[]):
        resp = client.get("/")
    html = resp.data.decode()
    assert "theme-btn" in html
    assert "cycleTheme" in html
    assert "claudio-theme" in html
