from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

import pytest

from lib import EnvconfigError, load


def test_generics(monkeypatch):
    @dataclass
    class Generics:
        params: Dict[str, int]
        digits: List[int]
        unique: Set[str]
        frozen: Tuple[int, ...]

    monkeypatch.setenv("PARAMS", "foo:1,bar:2")
    monkeypatch.setenv("DIGITS", "1,2,3")
    monkeypatch.setenv("UNIQUE", "foo,foo,foo,bar")
    monkeypatch.setenv("FROZEN", "4,5,6")

    config = load(Generics)
    assert config.params == {"foo": 1, "bar": 2}
    assert config.digits == [1, 2, 3]
    assert config.unique == {"foo", "bar"}
    assert config.frozen == (4, 5, 6)


def test_generic_tuple(monkeypatch):
    @dataclass
    class Config:
        pi: Tuple[int, int]
        endpoint: Tuple[str, int]

    monkeypatch.setenv("PI", "3,14159")
    monkeypatch.setenv("ENDPOINT", "localhost,5432")

    config = load(Config)
    assert config.pi == (3, 14159)
    assert config.endpoint == ("localhost", 5432)


def test_fixed_tuple_error(monkeypatch):
    @dataclass
    class Config:
        endpoint: Tuple[str, int]

    monkeypatch.setenv("ENDPOINT", "localhost,5432,bar")
    with pytest.raises(
        EnvconfigError,
        match="Invalid length for fixed tuple: expected 2, got 3",
    ):
        load(Config)
