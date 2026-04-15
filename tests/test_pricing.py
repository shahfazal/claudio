"""Tests for pricing config loading and table building."""

import json
from pathlib import Path

import pytest

from claudio.parsers import PRICING, _build_pricing_table, load_pricing_config

_DEFAULT_PATH = Path(__file__).parent.parent / "src" / "claudio" / "pricing.default.json"


# ---------------------------------------------------------------------------
# load_pricing_config
# ---------------------------------------------------------------------------


def test_load_pricing_config_reads_user_file(tmp_path):
    user_file = tmp_path / "pricing.json"
    user_file.write_text(
        json.dumps(
            {
                "last_updated": "2026-01-01",
                "models": {
                    "my-custom-model": {
                        "input": 1.0,
                        "cache_write": 1.25,
                        "cache_read": 0.1,
                        "output": 5.0,
                    }
                },
            }
        )
    )

    config = load_pricing_config(user_path=user_file, default_path=_DEFAULT_PATH)

    assert "my-custom-model" in config["models"]


def test_load_pricing_config_copies_default_on_first_run(tmp_path):
    user_file = tmp_path / ".claudio" / "pricing.json"
    assert not user_file.exists()

    config = load_pricing_config(user_path=user_file, default_path=_DEFAULT_PATH)

    assert user_file.exists()
    assert "models" in config
    assert len(config["models"]) > 0


def test_load_pricing_config_falls_back_on_corrupt_user_file(tmp_path):
    user_file = tmp_path / "pricing.json"
    user_file.write_text("not valid json {{{")

    config = load_pricing_config(user_path=user_file, default_path=_DEFAULT_PATH)

    # Should return the default config
    assert "models" in config
    assert len(config["models"]) > 0


def test_load_pricing_config_default_has_last_updated(tmp_path):
    user_file = tmp_path / "no-file.json"

    config = load_pricing_config(user_path=user_file, default_path=_DEFAULT_PATH)

    assert "last_updated" in config


# ---------------------------------------------------------------------------
# _build_pricing_table
# ---------------------------------------------------------------------------


def test_build_pricing_table_produces_4_tuples():
    config = {
        "models": {
            "test-model": {"input": 3.0, "cache_write": 3.75, "cache_read": 0.3, "output": 15.0},
        }
    }

    table = _build_pricing_table(config)

    assert "test-model" in table
    assert table["test-model"] == (3.0, 3.75, 0.3, 15.0)


def test_build_pricing_table_skips_malformed_entries():
    config = {
        "models": {
            "good-model": {"input": 1.0, "cache_write": 1.25, "cache_read": 0.1, "output": 5.0},
            "bad-model": {"input": "not-a-number", "output": "also-bad"},  # unparseable values
        }
    }

    table = _build_pricing_table(config)

    assert "good-model" in table
    assert "bad-model" not in table


def test_build_pricing_table_defaults_cache_rates():
    """cache_write and cache_read should default if omitted."""
    config = {
        "models": {
            "minimal-model": {"input": 4.0, "output": 16.0},
        }
    }

    table = _build_pricing_table(config)

    assert "minimal-model" in table
    inp, cw, cr, out = table["minimal-model"]
    assert inp == 4.0
    assert out == 16.0
    assert cw == pytest.approx(5.0)  # 4.0 * 1.25
    assert cr == pytest.approx(0.4)  # 4.0 * 0.1


def test_build_pricing_table_empty_models():
    table = _build_pricing_table({"models": {}})
    assert table == {}


# ---------------------------------------------------------------------------
# PRICING module-level table (regression — values must match default JSON)
# ---------------------------------------------------------------------------


def test_pricing_table_loaded_from_config():
    """PRICING must be populated from pricing.default.json, not hardcoded."""
    default = json.loads(_DEFAULT_PATH.read_text())
    for model in default["models"]:
        assert model in PRICING, f"Model {model!r} missing from PRICING table"


def test_pricing_sonnet_rates():
    """Spot-check a known model's rates haven't drifted."""
    inp, cw, cr, out = PRICING["claude-sonnet-4-6"]
    assert inp == 3.0
    assert out == 15.0


def test_pricing_haiku_rates():
    inp, cw, cr, out = PRICING["claude-haiku-3-20240307"]
    assert inp == 0.25
    assert out == 1.25
