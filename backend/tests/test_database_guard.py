from __future__ import annotations

import pytest

from backend.tests import db_guard


def test_test_database_requires_dedicated_database(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://role:secret@127.0.0.1:5432/es_magico_test")
    monkeypatch.setenv("TEST_DATABASE_URL", "postgresql+psycopg://role:secret@127.0.0.1:5432/es_magico_pytest")
    assert db_guard.require_test_database_url().endswith("/es_magico_pytest")


@pytest.mark.parametrize(
    "test_url",
    [
        None,
        "postgresql+psycopg://role:secret@127.0.0.1:5432/es_magico_test",
        "postgresql+psycopg://role:secret@127.0.0.1:5432/other_database",
    ],
)
def test_invalid_test_database_configuration_fails_closed(
    monkeypatch: pytest.MonkeyPatch, test_url: str | None
) -> None:
    monkeypatch.setattr(db_guard, "_load_environment", lambda: None)
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://role:secret@127.0.0.1:5432/es_magico_test")
    if test_url is None:
        monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    else:
        monkeypatch.setenv("TEST_DATABASE_URL", test_url)
    with pytest.raises(RuntimeError):
        db_guard.require_test_database_url()


def test_same_database_configuration_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(db_guard, "_load_environment", lambda: None)
    same_url = "postgresql+psycopg://role:secret@127.0.0.1:5432/es_magico_pytest"
    monkeypatch.setenv("DATABASE_URL", same_url)
    monkeypatch.setenv("TEST_DATABASE_URL", same_url)
    with pytest.raises(RuntimeError, match="different databases"):
        db_guard.require_test_database_url()
