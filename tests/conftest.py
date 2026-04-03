"""Shared pytest fixtures."""

from pathlib import Path

import pytest

from claudio.app import app as flask_app

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_JSONL = FIXTURES_DIR / "sample.jsonl"


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
