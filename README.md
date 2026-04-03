# claudio

Browse your [Claude Code](https://claude.ai/code) sessions in a local web app.

Reads `~/.claude/` — the same directory Claude Code writes to. No cloud, no sync, no accounts.

## What you get

- All sessions grouped by project, sorted newest-first
- Session titles from compact summaries ("Primary Request and Intent") or the first user message — no API calls, fully local
- Full transcript per session — user turns, assistant responses, tool calls
- Per-session command history and todo sidebar
- Estimated Costº
- Live search across titles and project paths
- Estimated cost per session (see note below)
- Dark / light / system theme (persisted in `localStorage`)
- Click-to-copy for the project path

º - read below for Cost Estimates

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/) — handles Python and dependencies automatically
- Claude Code installed (so `~/.claude/projects/` exists)

## Install & run

```bash
git clone https://github.com/shahfazal/claudio
cd claudio
uv run claudio
```

Open `http://127.0.0.1:5000`. That's it — `uv` creates a venv and installs dependencies on first run.

### Environment variables

| Variable | Default     | Description                     |
| -------- | ----------- | ------------------------------- |
| `PORT`   | `5000`      | Port to listen on               |
| `HOST`   | `127.0.0.1` | Bind address                    |
| `DEBUG`  | _(off)_     | Set to `1` for Flask debug mode |

## Development

```bash
uv run python -m pytest       # tests
uv run python -m ruff check . # lint
uv run python -m ruff format . # format
```

## Project layout

```
src/claudio/
├── app.py        Flask app + routes
├── parsers.py    JSONL parsing, data loading
└── templates.py  Jinja2 template strings
tests/
├── fixtures/     Sample JSONL for tests
├── conftest.py
├── test_parsers.py
└── test_routes.py
```

## Example session path

```bash
~/.claude/projects/-Users-aturing-claude-worktrees-enigma-decrypt-happy-colossus/7ad5ba28-b562-4ce3-9d76-13c02ec7c4da.jsonl
```

## Cost estimates

The cost shown per session is a **locally calculated estimate** — not a figure from Anthropic. Claudio reads the token usage logged in each assistant message (`input_tokens`, `output_tokens`, cache tokens) and multiplies by the published per-model rates.

A few caveats:

- Anthropic does not write a cost field to `~/.claude/` session files, so there is no authoritative number to read.
- Rates are hardcoded in `parsers.py` under `PRICING` and need manual updates when Anthropic changes pricing.
- Sessions that used a model not in the pricing table show `≈ ?` rather than a potentially wrong number.

Close enough to be useful for understanding relative session cost, but not a billing figure.

## Disclaimer

The name "Claudio" is a nod to Claude Code sessions — and also just a guy's
name. Any resemblance to AI assistants, living or dead, is purely coincidental.

Claudio is an independent open-source tool for browsing locally stored Claude
Code session files on your own machine. It is not affiliated with, endorsed by,
or sponsored by Anthropic. "Claude" is a trademark of Anthropic. Claudio simply
reads files that Claude Code writes to ~/.claude/ — it has no connection to
Anthropic's servers or services beyond what Claude Code itself already does.

## License

MIT
