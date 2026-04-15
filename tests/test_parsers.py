"""Tests for claudio.parsers."""

import json

import pytest

from claudio.parsers import (
    _calc_cost,
    _clean_user_text,
    _extract_compact_title,
    _extract_text,
    _extract_tool_uses,
    _parse_frontmatter,
    _strip_markdown,
    fmt_cost,
    fmt_ts,
    group_by_project,
    load_history,
    load_project_memory,
    load_todos,
    parse_session,
    project_display,
    session_title,
)

# ---------------------------------------------------------------------------
# _extract_text
# ---------------------------------------------------------------------------


def test_extract_text_list():
    content = [{"type": "text", "text": "foo"}, {"type": "text", "text": "bar"}]
    assert _extract_text(content) == "foo\nbar"


def test_extract_text_skips_non_text_blocks():
    content = [{"type": "tool_use", "name": "Read"}, {"type": "text", "text": "hi"}]
    assert _extract_text(content) == "hi"


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


# ---------------------------------------------------------------------------
# _clean_user_text
# ---------------------------------------------------------------------------


def test_clean_user_text_strips_tags():
    raw = "<ide_opened_file>foo.py</ide_opened_file>\nActual message"
    assert _clean_user_text(raw) == "Actual message"


# ---------------------------------------------------------------------------
# parse_session
# ---------------------------------------------------------------------------


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


def test_parse_session_compact_count(tmp_path):
    jf = tmp_path / "abc.jsonl"
    jf.write_text(
        '{"type":"system","subtype":"compact_boundary","content":"Conversation compacted","timestamp":"2026-01-01T10:00:00.000Z"}\n'
        '{"type":"system","subtype":"compact_boundary","content":"Conversation compacted","timestamp":"2026-01-01T11:00:00.000Z"}\n'
        '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"hi"}]},"timestamp":"2026-01-01T12:00:00.000Z"}\n'
    )
    s = parse_session(jf)
    assert s["compact_count"] == 2


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
    from datetime import datetime

    ts = "2026-01-01T10:00:01.000Z"
    expected = (
        datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime("%Y-%m-%d %H:%M")
    )
    assert fmt_ts(ts) == expected


def test_fmt_ts_unix_ms():
    from datetime import datetime, timezone

    ms = 1735689600000
    expected = (
        datetime.fromtimestamp(ms / 1000, tz=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    )
    assert fmt_ts(ms) == expected


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


# ---------------------------------------------------------------------------
# fmt_cost
# ---------------------------------------------------------------------------


def test_fmt_cost_falsy_returns_empty():
    assert fmt_cost(None) == ""
    assert fmt_cost(0) == ""


@pytest.mark.parametrize(
    "cost,expected",
    [
        (0.009, "$0.0090"),  # below $0.01 -> 4 decimal
        (0.01, "$0.01"),  # boundary -> 2 decimal
        (1.2345, "$1.23"),  # normal
    ],
)
def test_fmt_cost_formatting(cost, expected):
    assert fmt_cost(cost) == expected


# ---------------------------------------------------------------------------
# _strip_markdown
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("```python\ncode\n```\nafter", "after"),  # code block
        ("use `foo` here", "use foo here"),  # inline code
        ("**bold** text", "bold text"),  # bold
        ("_italic_ text", "italic text"),  # underscore
        ("[click](https://example.com)", "click"),  # link
        ("> quoted", "quoted"),  # blockquote
    ],
)
def test_strip_markdown(raw, expected):
    assert _strip_markdown(raw) == expected


def test_strip_markdown_heading():
    result = _strip_markdown("## My Heading\ntext")
    assert "##" not in result
    assert "My Heading" in result


# ---------------------------------------------------------------------------
# _extract_compact_title
# ---------------------------------------------------------------------------


def test_extract_compact_title_no_intro_returns_none():
    assert _extract_compact_title("Just a regular user message.") is None


def test_extract_compact_title_extracts_first_sentence():
    text = (
        "This session is being continued from a previous conversation that ran out of context."
        " The summary below covers the earlier portion of the conversation.\n\n"
        "Summary:\n1. Primary Request and Intent:\n   Fix the auth bug. It affects login.\n"
        "2. Key Technical Concepts:\n   Auth flow"
    )
    assert _extract_compact_title(text) == "Fix the auth bug."


# ---------------------------------------------------------------------------
# _parse_frontmatter
# ---------------------------------------------------------------------------


def test_parse_frontmatter_no_frontmatter():
    meta, body = _parse_frontmatter("just a body")
    assert meta == {}
    assert body == "just a body"


def test_parse_frontmatter_normal():
    text = "---\nname: My File\ntype: user\n---\nBody content"
    meta, body = _parse_frontmatter(text)
    assert meta == {"name": "My File", "type": "user"}
    assert body == "Body content"


# ---------------------------------------------------------------------------
# _calc_cost — additional branches
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# parse_session — additional branches
# ---------------------------------------------------------------------------


def test_parse_session_pr_link_valid(tmp_path):
    jf = tmp_path / "abc.jsonl"
    jf.write_text(
        '{"type":"pr-link","url":"https://github.com/org/repo/pull/1"}\n'
        '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"hi"}]},"timestamp":"2026-01-01T10:00:00.000Z"}\n'
    )
    s = parse_session(jf)
    assert s["pr_link"] == "https://github.com/org/repo/pull/1"


def test_parse_session_pr_link_invalid_scheme(tmp_path):
    jf = tmp_path / "abc.jsonl"
    jf.write_text(
        '{"type":"pr-link","url":"javascript:alert(1)"}\n'
        '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"hi"}]},"timestamp":"2026-01-01T10:00:00.000Z"}\n'
    )
    s = parse_session(jf)
    assert s["pr_link"] is None


def test_parse_session_cost_unknown(tmp_path):
    jf = tmp_path / "abc.jsonl"
    jf.write_text(
        '{"type":"assistant","message":{"role":"assistant","model":"claude-unknown-xyz",'
        '"content":[{"type":"text","text":"hi"}],'
        '"usage":{"input_tokens":1000,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":500}},'
        '"timestamp":"2026-01-01T10:00:00.000Z"}\n'
    )
    s = parse_session(jf)
    assert s["cost_unknown"] is True
    assert s["cost_usd"] is None


def test_parse_session_malformed_json_lines_skipped(tmp_path):
    jf = tmp_path / "abc.jsonl"
    jf.write_text(
        '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"first"}]},"timestamp":"2026-01-01T10:00:00.000Z"}\n'
        "this is not json at all\n"
        '{"type":"user","message":{"role":"user","content":[{"type":"text","text":"second"}]},"timestamp":"2026-01-01T10:00:01.000Z"}\n'
    )
    s = parse_session(jf)
    assert s["message_count"] == 2


def test_parse_session_empty_message_skipped(tmp_path):
    jf = tmp_path / "abc.jsonl"
    jf.write_text(
        '{"type":"assistant","message":{"role":"assistant","model":"claude-sonnet-4-6",'
        '"content":[],"usage":{"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0}},'
        '"timestamp":"2026-01-01T10:00:00.000Z"}\n'
    )
    s = parse_session(jf)
    assert s["message_count"] == 0


def test_parse_session_sidechain_message_included(tmp_path):
    # Parser includes sidechain messages — template filters display, not parser
    jf = tmp_path / "abc.jsonl"
    jf.write_text(
        '{"type":"user","isSidechain":true,"message":{"role":"user","content":[{"type":"text","text":"sidechain msg"}]},'
        '"timestamp":"2026-01-01T10:00:00.000Z"}\n'
    )
    s = parse_session(jf)
    assert s["message_count"] == 1
    assert s["messages"][0]["is_sidechain"] is True


# ---------------------------------------------------------------------------
# strip_home
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# load_history
# ---------------------------------------------------------------------------


def test_load_history_file_not_exists(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "HISTORY_FILE", tmp_path / "nonexistent.jsonl")
    assert load_history() == {}


def test_load_history_groups_and_sorts(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    hf = tmp_path / "history.jsonl"
    hf.write_text(
        json.dumps(
            {
                "project": "/proj-a",
                "display": "older",
                "timestamp": "2026-01-01T09:00:00Z",
                "sessionId": "s1",
            }
        )
        + "\n"
        + json.dumps(
            {
                "project": "/proj-a",
                "display": "newer",
                "timestamp": "2026-01-01T10:00:00Z",
                "sessionId": "s2",
            }
        )
        + "\n"
        + json.dumps(
            {
                "project": "/proj-b",
                "display": "only",
                "timestamp": "2026-01-01T08:00:00Z",
                "sessionId": "s3",
            }
        )
        + "\n"
    )
    monkeypatch.setattr(parsers_module, "HISTORY_FILE", hf)
    history = load_history()
    assert set(history.keys()) == {"/proj-a", "/proj-b"}
    assert history["/proj-a"][0]["display"] == "newer"  # sorted newest-first


def test_load_history_malformed_line_skipped(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    hf = tmp_path / "history.jsonl"
    hf.write_text(
        "not json\n"
        + json.dumps(
            {
                "project": "/proj-a",
                "display": "ok",
                "timestamp": "2026-01-01T10:00:00Z",
                "sessionId": "s1",
            }
        )
        + "\n"
    )
    monkeypatch.setattr(parsers_module, "HISTORY_FILE", hf)
    history = load_history()
    assert len(history["/proj-a"]) == 1


# ---------------------------------------------------------------------------
# load_todos
# ---------------------------------------------------------------------------


def test_load_todos_dir_not_exists(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "TODOS_DIR", tmp_path / "nonexistent")
    assert load_todos() == {}


def test_load_todos_basic(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "TODOS_DIR", tmp_path)
    (tmp_path / "session-uuid-1234.json").write_text(
        json.dumps([{"content": "do something", "status": "pending"}])
    )
    todos = load_todos()
    assert "session-uuid-1234" in todos
    assert todos["session-uuid-1234"][0]["content"] == "do something"


def test_load_todos_agent_filename_splitting(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "TODOS_DIR", tmp_path)
    (tmp_path / "my-session-id-agent-abc123.json").write_text(
        json.dumps([{"content": "task", "status": "done"}])
    )
    todos = load_todos()
    assert "my-session-id" in todos


def test_load_todos_non_list_skipped(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "TODOS_DIR", tmp_path)
    (tmp_path / "bad.json").write_text(json.dumps({"not": "a list"}))
    todos = load_todos()
    assert todos == {}


# ---------------------------------------------------------------------------
# load_project_memory
# ---------------------------------------------------------------------------


def test_load_project_memory_dir_not_exists(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "PROJECTS_DIR", tmp_path)
    result = load_project_memory("nonexistent-slug")
    assert result == {"count": 0, "index": None, "files": []}


def test_load_project_memory_index_vs_files(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "PROJECTS_DIR", tmp_path)
    mem_dir = tmp_path / "my-slug" / "memory"
    mem_dir.mkdir(parents=True)
    (mem_dir / "MEMORY.md").write_text("# Index content")
    (mem_dir / "user_profile.md").write_text("---\nname: My Profile\ntype: user\n---\nBody here")
    result = load_project_memory("my-slug")
    assert result["count"] == 1
    assert result["index"] == "# Index content"
    assert result["files"][0]["name"] == "My Profile"
    assert result["files"][0]["type"] == "user"
    assert result["files"][0]["body"] == "Body here"


def test_load_project_memory_invalid_type_blanked(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "PROJECTS_DIR", tmp_path)
    mem_dir = tmp_path / "my-slug" / "memory"
    mem_dir.mkdir(parents=True)
    (mem_dir / "evil.md").write_text("---\ntype: <script>alert(1)</script>\n---\nBody")
    result = load_project_memory("my-slug")
    assert result["files"][0]["type"] == ""


# ---------------------------------------------------------------------------
# group_by_project — memory_count
# ---------------------------------------------------------------------------


def test_group_by_project_memory_count_excludes_memory_md(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "PROJECTS_DIR", tmp_path)
    mem_dir = tmp_path / "proj-a" / "memory"
    mem_dir.mkdir(parents=True)
    (mem_dir / "MEMORY.md").write_text("# index")
    (mem_dir / "feedback_foo.md").write_text("---\ntype: feedback\n---\nbody")
    (mem_dir / "user_profile.md").write_text("---\ntype: user\n---\nbody")
    sessions = [
        {
            "project_slug": "proj-a",
            "cwd": "/a",
            "started_at": "2026-01-01T00:00:00Z",
            "messages": [],
            "compact_count": 0,
        }
    ]
    groups = group_by_project(sessions)
    assert groups[0]["memory_count"] == 2  # MEMORY.md excluded


# ---------------------------------------------------------------------------
# _parse_cache — mtime-based caching
# ---------------------------------------------------------------------------


def test_parse_cache_populates_on_load(sample_jsonl, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "PROJECTS_DIR", sample_jsonl.parent.parent)
    parsers_module._parse_cache.clear()

    from claudio.parsers import load_all_sessions

    load_all_sessions()

    assert sample_jsonl in parsers_module._parse_cache
    _, cached = parsers_module._parse_cache[sample_jsonl]
    assert cached["session_id"] == "aaaabbbb-0000-0000-0000-000000000001"


def test_parse_cache_invalidates_on_mtime_change(sample_jsonl, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "PROJECTS_DIR", sample_jsonl.parent.parent)
    parsers_module._parse_cache.clear()

    from claudio.parsers import load_all_sessions

    load_all_sessions()

    # Simulate stale cache entry from a previous run
    parsers_module._parse_cache[sample_jsonl] = (0.0, {"stale": True})
    load_all_sessions()

    _, cached = parsers_module._parse_cache[sample_jsonl]
    assert "stale" not in cached
    assert "session_id" in cached


# ---------------------------------------------------------------------------
# sort key — numeric timestamps
# ---------------------------------------------------------------------------


def test_load_all_sessions_sort_handles_numeric_timestamp(tmp_path, monkeypatch):
    import claudio.parsers as parsers_module

    monkeypatch.setattr(parsers_module, "PROJECTS_DIR", tmp_path)
    parsers_module._parse_cache.clear()

    proj = tmp_path / "-Users-test-proj"
    proj.mkdir()

    # Session with ISO timestamp
    (proj / "aaaaaaaa-0000-0000-0000-000000000001.jsonl").write_text(
        '{"type":"user","isSidechain":false,"message":{"role":"user","content":[{"type":"text","text":"iso"}]},'
        '"timestamp":"2026-06-01T12:00:00.000Z","cwd":"/Users/test/proj"}\n'
    )
    # Session with numeric timestamp (ms) — older
    (proj / "aaaaaaaa-0000-0000-0000-000000000002.jsonl").write_text(
        '{"type":"user","isSidechain":false,"message":{"role":"user","content":[{"type":"text","text":"num"}]},'
        '"timestamp":1700000000000,"cwd":"/Users/test/proj"}\n'
    )

    from claudio.parsers import load_all_sessions

    sessions = load_all_sessions()
    assert len(sessions) == 2
    # ISO (newer) should sort first
    assert sessions[0]["started_at"] == "2026-06-01T12:00:00.000Z"
