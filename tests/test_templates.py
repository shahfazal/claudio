"""Tests for template helper functions."""

from claudio.templates import brain_icon


def test_icon_size_parameter():
    result = brain_icon(20)
    assert 'width="20"' in result
    assert 'height="20"' in result
