"""Shared pytest fixtures."""

from pathlib import Path

import pytest

from claudio import parsers as parsers_module
from claudio.app import app as flask_app

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_JSONL = FIXTURES_DIR / "sample.jsonl"


@pytest.fixture(autouse=True)
def _isolate_store(tmp_path, monkeypatch):
    """Point the store at an empty dir for every test.

    sessions_root() prefers the store when it has content; without this, tests
    that monkeypatch PROJECTS_DIR would silently read the developer's real
    ~/.claudio/store. Forcing an empty store makes the resolver fall back to the
    live tree each test controls.
    """
    monkeypatch.setattr(parsers_module, "STORE_PROJECTS_DIR", tmp_path / "_empty_store")


@pytest.fixture()
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


@pytest.fixture()
def sample_jsonl(tmp_path) -> Path:
    """Copy the fixture JSONL into a temp project directory and return its path."""
    proj_dir = tmp_path / "projects" / "-Users-test-myproject"
    proj_dir.mkdir(parents=True)
    dest = proj_dir / "aaaabbbb-0000-0000-0000-000000000001.jsonl"
    dest.write_text(SAMPLE_JSONL.read_text())
    return dest
