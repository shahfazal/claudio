# claudio

Browse your [Claude Code](https://claude.ai/code) sessions in a local web app.

Reads `~/.claude/` — the same directory Claude Code writes to. No cloud, no sync, no accounts.

<img width="718" height="388" alt="image" src="https://github.com/user-attachments/assets/78ae2709-8b61-423a-be58-8dfc8acd006b" />

## What you get

- All sessions grouped by project, sorted newest-first
- Session titles from compact summaries ("Primary Request and Intent") or the first user message, no API calls, fully local
- Full transcript per session: user turns, assistant responses, tool calls
- Per-session command history and todo sidebar
- Estimated Costº
- Live search across titles and project paths
- Estimated cost per session (see note below)
- Per-project memory browser: reads Claude Code's `memory/` files, linked from the index and session sidebar
- Dark / light / system theme (persisted in `localStorage`)
- Click-to-copy for the project path

º - read below for Cost Estimates

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/): handles Python and dependencies automatically
- Claude Code installed (so `~/.claude/projects/` exists)

## Install & run

```bash
git clone https://github.com/shahfazal/claudio
cd claudio
uv run claudio
```

Open `http://127.0.0.1:5001`. That's it — `uv` creates a venv and installs dependencies on first run.

### Environment variables

| Variable | Default     | Description                     |
| -------- | ----------- | ------------------------------- |
| `PORT`   | `5001`      | Port to listen on               |
| `HOST`   | `127.0.0.1` | Bind address                    |
| `DEBUG`  | _(off)_     | Set to `1` for Flask debug mode |

## Development

```bash
uv run python -m pytest       # 107 tests across parsers, routes, templates, health, export, pricing
uv run python -m ruff check . # lint
uv run python -m ruff format . # format
```

## Project layout

```
src/claudio/
├── app.py                Flask app + routes
├── health.py             Environment health checks
├── parsers.py            JSONL parsing, data loading
├── pricing.default.json  Bundled pricing rates (copied to ~/.claudio/ on first run)
└── templates.py          Jinja2 template strings
tests/
├── fixtures/             Sample JSONL for tests
├── conftest.py
├── test_export.py
├── test_health.py
├── test_parsers.py
├── test_pricing.py
├── test_routes.py
└── test_templates.py
```

## Example session path

```bash
~/.claude/projects/-Users-aturing-claude-worktrees-enigma-decrypt-happy-colossus/7ad5ba28-b562-4ce3-9d76-13c02ec7c4da.jsonl
```

## Cost estimates

The cost shown per session is a **locally calculated estimate**, not a figure from Anthropic. Claudio reads the token usage logged in each assistant message (`input_tokens`, `output_tokens`, cache tokens) and multiplies by the published per-model rates.

A few caveats:

- Anthropic does not write a cost field to `~/.claude/` session files, so there is no authoritative number to read.
- Rates are loaded from `~/.claudio/pricing.json` (editable). Update `last_updated` and the relevant model rates when Anthropic changes pricing. See `/health` in the app for a staleness warning after 90 days.
- Sessions that used a model not in the pricing table show `≈ ?` rather than a potentially wrong number.

Close enough to be useful for understanding relative session cost, but not a billing figure.

## Contributing

Contributions welcome! Before opening a PR:

- Run `uv run python -m ruff check .` and `uv run python -m ruff format .`
- Add tests for new features (see `tests/` for examples)
- Fill out the PR template with description and test plan

**Legal:** Contributions must be your own work, created on your own time and resources,
not subject to employer IP claims. By submitting a PR, you confirm you have the right to
license this work under MIT.

See [CONTRIBUTING.md](CONTRIBUTING.md) for full details.

## ⚠️ Stability & Compatibility

Claudio reads **undocumented local files** created by Claude Code:

- `~/.claude/projects/<slug>/<uuid>.jsonl`: session data
- `~/.claude/history.jsonl`: session index
- `~/.claude/projects/<slug>/memory/`: memory files

**This is fragile by design.** These files, their locations, and their schemas are not a public API. If Anthropic changes where or how sessions are stored, Claudio will break.

### What v0.4 does about it

| Feature              | What it does                                                                                                     |
| -------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Health check**     | Validates `~/.claude/` structure and spot-checks session schema on every page load. Visit `/health` for details. |
| **Export**           | Download all sessions as portable JSON via the nav bar. If Claudio breaks, you keep your data.                   |
| **External pricing** | Rates live in `~/.claudio/pricing.json`, edit manually when Anthropic changes pricing, no code change needed.    |

### If Claudio breaks after a Claude Code update

1. Check `/health` for diagnostics
2. Export your data before investigating
3. File an issue: https://github.com/shahfazal/claudio/issues

This is a **hobby project**, not production software. Enjoy it while it works.

## Changelog

| Version | Commit  | Feature                                             |
| ------- | ------- | --------------------------------------------------- |
| v0.4.0  | ---     | Resilience: health checks, export, external pricing |
| v0.3.0  | b9a60e0 | Compaction count                                    |
| v0.2.0  | c7ef66d | Memory browser                                      |
| v0.1.0  | b2bd054 | Initial release                                     |

## Disclaimer

The name "Claudio" is a nod to Claude Code sessions, and also just a guy's
name. Any resemblance to AI assistants, living or dead, is purely coincidental.

Claudio is an independent open-source tool for browsing locally stored Claude
Code session files on your own machine. It is not affiliated with, endorsed by,
or sponsored by Anthropic. "Claude" is a trademark of Anthropic. Claudio simply
reads files that Claude Code writes to ~/.claude/ and has no connection to
Anthropic's servers or services beyond what Claude Code itself already does.

## License

MIT
