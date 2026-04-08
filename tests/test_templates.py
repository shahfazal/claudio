"""Tests for template helper functions."""

import pytest
from markupsafe import Markup

from claudio.templates import archive_icon, brain_icon


@pytest.mark.parametrize("fn", [brain_icon, archive_icon])
def test_icon_returns_markup(fn):
    assert isinstance(fn(), Markup)


@pytest.mark.parametrize("fn", [brain_icon, archive_icon])
def test_icon_size_parameter(fn):
    result = fn(20)
    assert 'width="20"' in result
    assert 'height="20"' in result
