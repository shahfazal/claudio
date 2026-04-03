# Contributing to Claudio

Thanks for your interest in contributing! Claudio is a small local tool — contributions should stay focused and practical.

## Before you open a PR

1. **Run it against your own `~/.claude/`** — make sure it works with your actual sessions, not just the happy path
2. **Keep it local-first** — Claudio reads local files, it should never phone home or require external services
3. **One thing per PR** — bug fix or feature, not both
4. **Run the tests** — `uv run pytest` must pass before opening a PR
5. **Add tests for new behaviour** — if you're adding a feature or fixing a bug,
   add a test that would have caught it. Tests live in `tests/`
6. **Sanitize your submission** — Make sure no personal data appears in your PR.
   This includes real session content, actual project paths from your machine,
   API keys, or anything from your own `~/.claude/`. Use the fixtures in
   `tests/fixtures/` for any sample data.
7. **Set up the pre-push hook** — copy `.private-patterns.example` to
   `.private-patterns` and remove the comment lines (lines starting with `#`
   are not treated as comments by grep — they'll match literally and cause
   false positives on every push). Add your own username and local paths.

## Setup

```bash
git clone https://github.com/shahfazal/claudio
cd claudio
git config core.hooksPath .github/hooks  # install pre-push privacy check
uv run claudio
```

Open `http://127.0.0.1:5000` — it reads from your own `~/.claude/` automatically.

## Testing

```bash
uv run pytest       # tests
uv run ruff check . # lint
uv run ruff format . # format
```

Tests cover session parsing, path handling, and title extraction (compact summary and first-message fallback — no mocking needed, no network calls).
If you're adding a new data source (e.g. a new `~/.claude/` directory)
add a corresponding test with a fixture that mimics the file structure —
don't rely on your own `~/.claude/` being present in tests.

Key things to test:

- Empty sessions (0 msgs) handled gracefully
- Worktree paths parsed correctly
- Malformed JSONL lines don't crash the parser
- Search filtering returns correct counts

## What makes a good contribution

- Bug fixes with a clear description of what was broken and how you verified the fix
- UI improvements that are clean and don't add dependencies
- Support for new `~/.claude/` data sources as Claude Code evolves
- Performance improvements for large session histories

## What to avoid

- Adding cloud sync, authentication, or any network calls
- Heavy dependencies — this should stay lightweight and easy to run locally
- Breaking changes to the core session reading logic without a clear reason

## Opening a PR

- Fork the repo, create a branch, open a PR against `main`
- Describe what you changed and why
- If it's a UI change, include a screenshot
