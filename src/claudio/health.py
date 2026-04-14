"""Health checks for Claudio's dependency on ~/.claude/ internals."""

from __future__ import annotations

import json
import time
from datetime import date
from pathlib import Path

from claudio.parsers import parse_session

_CACHE_TTL = 300  # 5 minutes
_cache: dict = {"result": None, "at": 0.0}


def check_claude_directory(claude_dir: Path | None = None) -> dict:
    """Verify ~/.claude/ exists with expected subdirectories."""
    if claude_dir is None:
        claude_dir = Path.home() / ".claude"

    if not claude_dir.exists():
        return {
            "ok": False,
            "message": f"{claude_dir} not found",
            "missing": [str(claude_dir)],
        }

    expected = ["projects", "history.jsonl", "todos"]
    missing = [name for name in expected if not (claude_dir / name).exists()]

    if missing:
        return {
            "ok": False,
            "message": f"Missing: {', '.join(missing)}",
            "missing": missing,
        }

    projects_dir = claude_dir / "projects"
    try:
        project_count = sum(1 for p in projects_dir.iterdir() if p.is_dir())
    except OSError:
        project_count = 0

    return {
        "ok": True,
        "message": f"Found {claude_dir} ({project_count} projects)",
        "missing": [],
    }


def check_session_schema(projects_dir: Path | None = None) -> dict:
    """Spot-check the newest session file against expected schema."""
    if projects_dir is None:
        projects_dir = Path.home() / ".claude" / "projects"

    if not projects_dir.exists():
        return {
            "ok": False,
            "message": "projects/ directory not found",
            "parsed_count": 0,
            "total_count": 0,
        }

    try:
        all_jsonl = sorted(
            projects_dir.glob("*/*.jsonl"),
            key=lambda f: f.stat().st_mtime,
            reverse=True,
        )
    except OSError as exc:
        return {
            "ok": False,
            "message": f"Could not scan sessions: {exc}",
            "parsed_count": 0,
            "total_count": 0,
        }

    total = len(all_jsonl)
    if total == 0:
        return {
            "ok": True,
            "message": "No sessions found",
            "parsed_count": 0,
            "total_count": 0,
        }

    sample = all_jsonl[0]
    try:
        parse_session(sample)
        return {
            "ok": True,
            "message": f"Schema OK (sampled 1 of {total} sessions)",
            "parsed_count": 1,
            "total_count": total,
        }
    except Exception as exc:
        return {
            "ok": False,
            "message": f"Schema check failed: {exc}",
            "parsed_count": 0,
            "total_count": total,
        }


def check_pricing_freshness(pricing_path: Path | None = None) -> dict:
    """Warn if ~/.claudio/pricing.json is older than 90 days."""
    if pricing_path is None:
        pricing_path = Path.home() / ".claudio" / "pricing.json"

    if not pricing_path.exists():
        return {
            "ok": True,
            "message": "Using built-in pricing (no user config)",
            "last_updated": None,
            "days_old": None,
        }

    try:
        data = json.loads(pricing_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {
            "ok": False,
            "message": f"Could not read pricing config: {exc}",
            "last_updated": None,
            "days_old": None,
        }

    last_updated_str = data.get("last_updated")
    if not last_updated_str:
        return {
            "ok": True,
            "message": "Pricing config found (no last_updated field)",
            "last_updated": None,
            "days_old": None,
        }

    try:
        last_updated = date.fromisoformat(last_updated_str)
        days_old = (date.today() - last_updated).days
    except ValueError:
        return {
            "ok": True,
            "message": "Pricing config found (could not parse last_updated date)",
            "last_updated": last_updated_str,
            "days_old": None,
        }

    if days_old > 90:
        return {
            "ok": False,
            "message": f"Pricing config is {days_old} days old — update recommended",
            "last_updated": last_updated_str,
            "days_old": days_old,
        }

    return {
        "ok": True,
        "message": f"Pricing config is {days_old} days old",
        "last_updated": last_updated_str,
        "days_old": days_old,
    }


def check_environment(
    claude_dir: Path | None = None,
    projects_dir: Path | None = None,
    pricing_path: Path | None = None,
) -> dict:
    """Run all health checks. Results cached for 5 min when using default paths."""
    use_cache = claude_dir is None and projects_dir is None and pricing_path is None
    if use_cache:
        now = time.monotonic()
        if _cache["result"] is not None and (now - _cache["at"]) < _CACHE_TTL:
            return _cache["result"]

    checks = {
        "claude_dir": check_claude_directory(claude_dir),
        "schema": check_session_schema(projects_dir),
        "pricing": check_pricing_freshness(pricing_path),
    }

    if not checks["claude_dir"]["ok"] or not checks["schema"]["ok"]:
        status = "error"
    elif not checks["pricing"]["ok"]:
        status = "warning"
    else:
        status = "ok"

    result = {"status": status, "checks": checks}

    if use_cache:
        _cache["result"] = result
        _cache["at"] = time.monotonic()

    return result
