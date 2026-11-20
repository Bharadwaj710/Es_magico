from __future__ import annotations

import time

from backend.app.config import Settings, get_settings
from backend.app.db import create_database_engine


def test_connection_timeout_defaults_to_five_seconds(monkeypatch) -> None:
    monkeypatch.delenv("DB_CONNECT_TIMEOUT_SECONDS", raising=False)
    assert get_settings().db_connect_timeout_seconds == 5


def test_invalid_postgresql_connection_is_bounded() -> None:
    engine = create_database_engine(
        Settings(
            database_url="postgresql+psycopg://invalid:invalid@127.0.0.1:59999/unavailable",
            max_import_file_bytes=10485760,
            db_connect_timeout_seconds=1,
        )
    )
    started = time.monotonic()
    try:
        try:
            engine.connect()
        except Exception:
            pass
        else:
            raise AssertionError("invalid PostgreSQL connection unexpectedly succeeded")
    finally:
        engine.dispose()
    assert time.monotonic() - started < 3
