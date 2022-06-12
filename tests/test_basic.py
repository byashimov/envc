from dataclasses import dataclass, field
from datetime import timedelta

import pytest

from lib import EnvconfigError, load


def test_basic(monkeypatch):
    @dataclass
    class Connection:
        timeout: timedelta

    @dataclass
    class Database:
        host: str
        port: int
        connection: Connection

    @dataclass
    class Config:
        rate: float
        database: Database
        debug: bool = False

    monkeypatch.setenv("RATE", "4.2")
    monkeypatch.setenv("DEBUG", "1")
    monkeypatch.setenv("DATABASE_HOST", "localhost")
    monkeypatch.setenv("DATABASE_PORT", "5432")
    monkeypatch.setenv("DATABASE_CONNECTION_TIMEOUT", "1m2s")

    config = load(Config)
    assert config.rate == 4.2
    assert config.debug is True
    assert config.database.host == "localhost"
    assert config.database.port == 5432
    assert config.database.connection.timeout == timedelta(
        minutes=1, seconds=2
    )


def test_missing_env(monkeypatch):
    @dataclass
    class Database:
        host: str
        port: int
        timeout: timedelta

    monkeypatch.setenv("HOST", "localhost")

    with pytest.raises(EnvconfigError, match="PORT is required"):
        load(Database)


def test_value_error(monkeypatch):
    @dataclass
    class Database:
        host: str
        port: int

    monkeypatch.setenv("HOST", "localhost")
    monkeypatch.setenv("PORT", "localhost")

    with pytest.raises(
        EnvconfigError, match="Can't cast PORT=localhost to <class 'int'>"
    ):
        load(Database)


def test_postponed_annotation():
    @dataclass
    class Database:
        host: str

    @dataclass
    class Postponed:
        database: "Database"

    with pytest.raises(
        EnvconfigError,
        match="Postponed evaluation of annotations is not supported: Database",
    ):
        load(Postponed)


def test_prefix_passed(monkeypatch):
    @dataclass
    class Database:
        host: str
        port: int
        timeout: timedelta

    monkeypatch.setenv("DB_HOST", "github.com")
    monkeypatch.setenv("DB_PORT", "1234")
    monkeypatch.setenv("DB_TIMEOUT", "1m")

    config = load(Database, prefix="DB")
    assert config.host == "github.com"
    assert config.port == 1234
    assert config.timeout == timedelta(minutes=1)


def test_uses_defaults():
    @dataclass
    class Defaults:
        debug: bool = True

    config = load(Defaults)
    assert config.debug is True


def test_optional_nested_and_merged(monkeypatch):
    @dataclass
    class Connection:
        timeout: timedelta
        max_idle: int

    @dataclass
    class Database:
        connection: Connection = Connection(
            timeout=timedelta(seconds=1), max_idle=2
        )

    # merge value
    monkeypatch.setenv("CONNECTION_MAX_IDLE", "3")
    config = load(Database)
    assert config.connection.timeout.total_seconds() == 1
    assert config.connection.max_idle == 3


def test_default_factory():
    @dataclass
    class Database:
        endpoints: list = field(default_factory=lambda: ["foo"])

    config = load(Database)
    assert config.endpoints == ["foo"]


def test_uses_given_map(monkeypatch):
    @dataclass
    class Database:
        __envc__ = {
            "port": "LOL",
        }

        host: str
        port: int

    monkeypatch.setenv("HOST", "github.com")
    monkeypatch.setenv("LOL", "5432")

    config = load(Database)
    assert config.host == "github.com"
    assert config.port == 5432
