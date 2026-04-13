"""Tests for Flask routes."""

from unittest.mock import patch

from claudio.parsers import parse_session


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


def test_session_cards_are_links(client, sample_jsonl):
    """Session cards must be <a> elements, not <div onclick>, for keyboard/a11y."""
    session = parse_session(sample_jsonl)
    session["project_slug"] = "-Users-test-myproject"

    with patch("claudio.app.load_all_sessions", return_value=[session]):
        resp = client.get("/")

    html = resp.data.decode()
    assert 'onclick="location.href' not in html
    assert '<a class="session-card"' in html
    assert 'href="/session/' in html



# ---------------------------------------------------------------------------
# /memory route
# ---------------------------------------------------------------------------


def test_memory_route_invalid_slug_chars(client):
    # Slug with angle bracket — must be rejected by the _SLUG_RE guard
    resp = client.get("/memory/bad%3Cslug%3E")
    assert resp.status_code == 400


def test_memory_route_invalid_slug_all_dashes(client):
    # All-dash slug passes character set but has no alphanumeric — must be rejected
    resp = client.get("/memory/---")
    assert resp.status_code == 400


def test_memory_route_not_found(client):
    with patch("claudio.app.load_project_memory", return_value={"count": 0, "index": None, "files": []}):
        resp = client.get("/memory/some-valid-slug")
    assert resp.status_code == 404


def test_memory_route_renders(client):
    memory = {
        "count": 1,
        "index": "# Memory Index",
        "files": [
            {
                "filename": "user_profile.md",
                "name": "User Profile",
                "description": "Who the user is",
                "type": "user",
                "body": "Senior engineer, prefers Python.",
            }
        ],
    }
    with patch("claudio.app.load_project_memory", return_value=memory):
        resp = client.get("/memory/some-valid-slug")
    assert resp.status_code == 200
    assert b"User Profile" in resp.data
    assert b"Senior engineer" in resp.data


# ---------------------------------------------------------------------------
# /session — additional branches
# ---------------------------------------------------------------------------


def test_session_view_with_pr_link(client, sample_jsonl, monkeypatch):
    import claudio.app as app_module

    monkeypatch.setattr(app_module, "PROJECTS_DIR", sample_jsonl.parent.parent)
    original = parse_session(sample_jsonl)
    original["pr_link"] = "https://github.com/org/repo/pull/42"
    with patch("claudio.app.parse_session", return_value=original):
        resp = client.get("/session/aaaabbbb-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    assert b"github.com/org/repo/pull/42" in resp.data


def test_session_view_cost_unknown_rendered(client, sample_jsonl, monkeypatch):
    import claudio.app as app_module

    monkeypatch.setattr(app_module, "PROJECTS_DIR", sample_jsonl.parent.parent)
    original = parse_session(sample_jsonl)
    original["cost_unknown"] = True
    original["cost_usd"] = None
    with patch("claudio.app.parse_session", return_value=original):
        resp = client.get("/session/aaaabbbb-0000-0000-0000-000000000001")
    assert resp.status_code == 200
    assert b"unknown model" in resp.data


def test_session_view_sidechain_not_in_transcript(client, tmp_path, monkeypatch):
    import claudio.app as app_module

    proj_dir = tmp_path / "projects" / "-Users-test-myproject"
    proj_dir.mkdir(parents=True)
    session_id = "cccccccc-0000-0000-0000-000000000001"
    jf = proj_dir / f"{session_id}.jsonl"
    jf.write_text(
        '{"type":"user","isSidechain":false,"message":{"role":"user","content":[{"type":"text","text":"normal msg"}]},'
        '"timestamp":"2026-01-01T10:00:00.000Z","cwd":"/Users/test/myproject"}\n'
        '{"type":"user","isSidechain":true,"message":{"role":"user","content":[{"type":"text","text":"SIDECHAIN SECRET"}]},'
        '"timestamp":"2026-01-01T10:00:01.000Z"}\n'
    )
    monkeypatch.setattr(app_module, "PROJECTS_DIR", tmp_path / "projects")
    resp = client.get(f"/session/{session_id}")
    assert resp.status_code == 200
    assert b"normal msg" in resp.data
    assert b"SIDECHAIN SECRET" not in resp.data


