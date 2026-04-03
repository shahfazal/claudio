"""Tests for claudio.parsers."""

import pytest

from claudio.parsers import (
    _calc_cost,
    _clean_user_text,
    _extract_text,
    _extract_tool_uses,
    fmt_ts,
    group_by_project,
    parse_session,
    project_display,
    session_title,
)

# ---------------------------------------------------------------------------
# _extract_text
# ---------------------------------------------------------------------------


def test_extract_text_string():
    assert _extract_text("hello") == "hello"


def test_extract_text_list():
    content = [{"type": "text", "text": "foo"}, {"type": "text", "text": "bar"}]
    assert _extract_text(content) == "foo\nbar"


def test_extract_text_skips_non_text_blocks():
    content = [{"type": "tool_use", "name": "Read"}, {"type": "text", "text": "hi"}]
    assert _extract_text(content) == "hi"


def test_extract_text_empty():
    assert _extract_text([]) == ""
    assert _extract_text(None) == ""


# ---------------------------------------------------------------------------
# _extract_tool_uses
# ---------------------------------------------------------------------------


def test_extract_tool_uses():
    content = [
        {"type": "tool_use", "name": "Read", "input": {"file_path": "/foo.py"}},
        {"type": "text", "text": "done"},
    ]
    tools = _extract_tool_uses(content)
    assert len(tools) == 1
    assert tools[0]["name"] == "Read"
    assert tools[0]["input"] == {"file_path": "/foo.py"}


def test_extract_tool_uses_empty():
    assert _extract_tool_uses([]) == []
    assert _extract_tool_uses("not a list") == []


# ---------------------------------------------------------------------------
# _clean_user_text
# ---------------------------------------------------------------------------


def test_clean_user_text_strips_tags():
    raw = "<ide_opened_file>foo.py</ide_opened_file>\nActual message"
    assert _clean_user_text(raw) == "Actual message"


def test_clean_user_text_passthrough():
    assert _clean_user_text("plain text") == "plain text"


# ---------------------------------------------------------------------------
# parse_session
# ---------------------------------------------------------------------------

FIXTURES_DIR = __import__("pathlib").Path(__file__).parent / "fixtures"


def test_parse_session_basic(sample_jsonl):
    s = parse_session(sample_jsonl)

    assert s["session_id"] == "aaaabbbb-0000-0000-0000-000000000001"
    assert s["compact_title"] == "Fix the login bug."
    assert s["ai_title"] == "Fix the login bug (ai-title)"
    assert s["cwd"] == "/Users/test/myproject"
    assert s["message_count"] == 5  # compact, u1, a1, u2, a2
    assert s["cost_usd"] is not None and s["cost_usd"] > 0


def test_parse_session_messages_have_roles(sample_jsonl):
    s = parse_session(sample_jsonl)
    roles = [m["role"] for m in s["messages"]]
    assert roles == ["user", "user", "assistant", "user", "assistant"]


def test_parse_session_tool_use_captured(sample_jsonl):
    s = parse_session(sample_jsonl)
    asst_msg = next(m for m in s["messages"] if m["role"] == "assistant")
    assert any(t["name"] == "Read" for t in asst_msg["tool_uses"])


def test_parse_session_cost_calculated(sample_jsonl):
    s = parse_session(sample_jsonl)
    # msg-a1: 100 input + 50 output @ sonnet-4 rates
    # msg-a2: 200 input + 1000 cache_read + 80 output @ sonnet-4 rates
    # sonnet-4: input=$3, cache_read=$0.30, output=$15 per MTok
    expected = (
        (100 * 3 + 50 * 15)  # msg-a1
        + (200 * 3 + 1000 * 0.30 + 80 * 15)  # msg-a2
    ) / 1_000_000
    assert s["cost_usd"] == pytest.approx(expected)


def test_calc_cost_uses_model_pricing():
    usage = {
        "input_tokens": 1_000_000,
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0,
        "output_tokens": 0,
    }
    assert _calc_cost("claude-opus-4-5", usage) == pytest.approx(15.00)
    assert _calc_cost("claude-sonnet-4-6", usage) == pytest.approx(3.00)
    assert _calc_cost("claude-haiku-4-5-20251001", usage) == pytest.approx(0.80)
    assert _calc_cost("claude-unknown-model", usage) is None  # unknown model with tokens → None


def test_parse_session_timestamps(sample_jsonl):
    s = parse_session(sample_jsonl)
    assert s["started_at"] == "2026-01-01T09:59:59.000Z"
    assert s["ended_at"] == "2026-01-01T10:00:15.000Z"


# ---------------------------------------------------------------------------
# session_title
# ---------------------------------------------------------------------------


def test_session_title_priority1_compact_summary(sample_jsonl):
    s = parse_session(sample_jsonl)
    # compact_title wins even though ai_title is also present
    assert session_title(s) == "Fix the login bug."


def test_session_title_priority2_ai_title():
    s = {
        "compact_title": None,
        "ai_title": "Refactor the auth module",
        "messages": [{"role": "user", "text": "do the refactor"}],
        "started_at": "2026-01-01T10:00:00.000Z",
    }
    assert session_title(s) == "Refactor the auth module"


def test_session_title_priority3_first_user_message():
    s = {
        "compact_title": None,
        "ai_title": None,
        "messages": [
            {"role": "user", "text": "**fix** the `login` bug please"},
            {"role": "assistant", "text": "Sure."},
        ],
        "started_at": "2026-01-01T10:00:00.000Z",
    }
    assert session_title(s) == "Fix The Login Bug Please"


def test_session_title_priority3_truncates_at_80():
    s = {
        "compact_title": None,
        "ai_title": None,
        "messages": [{"role": "user", "text": "a" * 100}],
        "started_at": "2026-01-01T10:00:00.000Z",
    }
    assert len(session_title(s)) == 80


def test_session_title_priority4_session_date():
    s = {
        "compact_title": None,
        "ai_title": None,
        "messages": [],
        "started_at": "2026-03-15T10:00:00.000Z",
    }
    assert session_title(s) == "Session 2026-03-15"


def test_session_title_priority4_no_date():
    s = {"compact_title": None, "ai_title": None, "messages": [], "started_at": None}
    assert session_title(s) == "Session"


# ---------------------------------------------------------------------------
# fmt_ts
# ---------------------------------------------------------------------------


def test_fmt_ts_iso_string():
    result = fmt_ts("2026-01-01T10:00:01.000Z")
    assert result == "2026-01-01 10:00"


def test_fmt_ts_unix_ms():
    # 1735689600000 ms = 2025-01-01 00:00 UTC
    result = fmt_ts(1735689600000)
    assert result.startswith("2025-01-01")


def test_fmt_ts_empty():
    assert fmt_ts(None) == ""
    assert fmt_ts("") == ""


# ---------------------------------------------------------------------------
# project_display / group_by_project
# ---------------------------------------------------------------------------


def test_project_display_uses_cwd():
    from pathlib import Path

    home = str(Path.home())
    assert project_display("-Users-someone-myproject", home + "/myproject") == "~/myproject"


def test_project_display_decodes_slug_strips_home():
    from pathlib import Path

    home = str(Path.home())
    slug = home.lstrip("/").replace("/", "-")
    result = project_display("-" + slug + "-myproject", None)
    assert result == "~/myproject"


def test_group_by_project_groups_correctly():
    sessions = [
        {
            "project_slug": "proj-a",
            "cwd": "/a",
            "started_at": "2026-02-01T00:00:00Z",
            "messages": [],
        },
        {
            "project_slug": "proj-a",
            "cwd": "/a",
            "started_at": "2026-01-01T00:00:00Z",
            "messages": [],
        },
        {
            "project_slug": "proj-b",
            "cwd": "/b",
            "started_at": "2026-03-01T00:00:00Z",
            "messages": [],
        },
    ]
    groups = group_by_project(sessions)
    assert len(groups) == 2
    # proj-b has the most recent session → comes first
    assert groups[0]["slug"] == "proj-b"
    assert len(groups[1]["sessions"]) == 2
