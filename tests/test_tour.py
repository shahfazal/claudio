"""Tests for the Driver.js help tour wiring."""

from unittest.mock import patch


def test_base_links_driver_css(client):
    with patch("claudio.app.load_all_sessions", return_value=([], [])):
        html = client.get("/").data.decode()
    assert '<link rel="stylesheet" href="/static/css/driver.css">' in html


def test_base_loads_driver_and_tour_scripts(client):
    with patch("claudio.app.load_all_sessions", return_value=([], [])):
        html = client.get("/").data.decode()
    assert '<script defer src="/static/js/driver.js.iife.js"></script>' in html
    assert '<script defer src="/static/js/tour.js"></script>' in html


def test_nav_renders_help_button(client):
    with patch("claudio.app.load_all_sessions", return_value=([], [])):
        html = client.get("/").data.decode()
    # Help button must be a real <button> so the keyboard handler binds.
    assert '<button class="theme-btn help-btn" id="help-btn" type="button"' in html
    assert 'aria-label="Replay tour"' in html


def test_help_button_present_on_stats_page(client):
    with patch("claudio.app.load_all_sessions", return_value=([], [])):
        html = client.get("/stats").data.decode()
    assert 'id="help-btn"' in html


def test_help_button_present_on_memory_page(client):
    memory = {
        "count": 1,
        "index": "# Memory Index",
        "files": [
            {
                "filename": "foo.md",
                "name": "Foo",
                "description": "Foo desc",
                "type": "user",
                "body": "body",
            }
        ],
    }
    with patch("claudio.app.load_project_memory", return_value=memory):
        html = client.get("/memory/some-valid-slug").data.decode()
    assert 'id="help-btn"' in html


def test_help_button_present_on_health_page(client):
    html = client.get("/health").data.decode()
    assert 'id="help-btn"' in html


def test_tour_static_file_served(client):
    """tour.js must ship with the package and be reachable from the browser."""
    resp = client.get("/static/js/tour.js")
    assert resp.status_code == 200
    body = resp.data.decode()
    # Public entry point used by the help button + welcome-modal chain.
    assert "window.startClaudioTour" in body


def test_driver_js_static_file_served(client):
    """Self-hosted driver.js bundle must be present, not pulled from a CDN."""
    resp = client.get("/static/js/driver.js.iife.js")
    assert resp.status_code == 200
    assert b"this.driver=this.driver||{}" in resp.data


def test_driver_css_static_file_served(client):
    resp = client.get("/static/css/driver.css")
    assert resp.status_code == 200
    assert b".driver-popover" in resp.data


def test_index_exposes_tour_anchors(client):
    """The tour's index-page stops target stable selectors. If these markup
    hooks disappear, the tour silently breaks. The optional `.session-card`
    anchor is covered by the existing session-listing tests."""
    with patch("claudio.app.load_all_sessions", return_value=([], [])):
        html = client.get("/").data.decode()
    assert 'class="nav-brand"' in html
    assert 'id="search"' in html
    assert 'class="theme-btn stats-btn' in html


def test_stats_exposes_tour_anchors(client):
    """The stats-page stops anchor against #filterToggle and the export link."""
    with patch("claudio.app.load_all_sessions", return_value=([], [])):
        html = client.get("/stats").data.decode()
    assert 'id="filterToggle"' in html
    # Export anchor: matches the `a.theme-btn[download]` selector in tour.js.
    assert '<a class="theme-btn" href="/export/sessions.json" download' in html
