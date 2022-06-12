from datetime import timedelta

import pytest

from lib.classifiers import boolean, duration


@pytest.mark.parametrize(
    "src, expected",
    (
        (
            "1d2h3m4s5ms6µs",
            timedelta(
                days=1,
                hours=2,
                minutes=3,
                seconds=4,
                milliseconds=5,
                microseconds=6,
            ),
        ),
        ("53d", timedelta(days=53)),
        ("100ms", timedelta(milliseconds=100)),
        ("2s500ms", timedelta(seconds=2, milliseconds=500)),
    ),
)
def test_duration(src, expected):
    assert duration(src) == expected


@pytest.mark.parametrize(
    "src, expected",
    (
        ("1", True),
        ("t", True),
        ("y", True),
        ("yes", True),
        ("on", True),
        ("true", True),
        ("TRUE", True),
        ("True", True),
        ("0", False),
        ("f", False),
        ("n", False),
        ("no", False),
        ("off", False),
        ("false", False),
        ("False", False),
        ("FALSE", False),
    ),
)
def test_boolean(src, expected):
    assert boolean(src) is expected


def test_boolean_value_error():
    with pytest.raises(ValueError):
        boolean("foo")
