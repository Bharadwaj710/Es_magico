from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlsplit

from dotenv import load_dotenv
from sqlalchemy import Engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUTHORIZED_TEST_DATABASE = "es_magico_pytest"
PROTECTED_DATABASE = "es_magico_test"


def _load_environment() -> None:
    load_dotenv(PROJECT_ROOT / ".env", override=False)


def require_test_database_url() -> str:
    _load_environment()
    value = os.getenv("TEST_DATABASE_URL")
    if not value:
        raise RuntimeError("TEST_DATABASE_URL is required; refusing to run PostgreSQL integration tests")

    parsed = urlsplit(value.replace("postgresql+psycopg://", "postgresql://", 1))
    database = parsed.path.lstrip("/")
    if database not in {AUTHORIZED_TEST_DATABASE}:
        raise RuntimeError(
            f"TEST_DATABASE_URL must target {AUTHORIZED_TEST_DATABASE!r}; refusing destructive test operations"
        )
    if database == PROTECTED_DATABASE:
        raise RuntimeError("Refusing destructive test operations against the acceptance database")

    application_url = os.getenv("DATABASE_URL")
    if application_url:
        application_database = urlsplit(
            application_url.replace("postgresql+psycopg://", "postgresql://", 1)
        ).path.lstrip("/")
        if application_database == database:
            raise RuntimeError("DATABASE_URL and TEST_DATABASE_URL must target different databases")
    return value


def verify_test_database(engine: Engine) -> None:
    with engine.connect() as connection:
        database, user = connection.execute(
            text("SELECT current_database(), current_user")
        ).one()
    if database != AUTHORIZED_TEST_DATABASE:
        raise RuntimeError(
            f"Connected database is {database!r}, expected {AUTHORIZED_TEST_DATABASE!r}; refusing cleanup"
        )
    if database == PROTECTED_DATABASE:
        raise RuntimeError("Connected to the protected acceptance database; refusing cleanup")
    if not user:
        raise RuntimeError("PostgreSQL did not report a connected user; refusing cleanup")


def upgrade_test_database() -> None:
    url = require_test_database_url()
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        check=True,
        cwd=PROJECT_ROOT,
        env={**os.environ, "DATABASE_URL": url},
    )


def stamp_test_database_base() -> None:
    url = require_test_database_url()
    subprocess.run(
        [sys.executable, "-m", "alembic", "stamp", "base"],
        check=True,
        cwd=PROJECT_ROOT,
        env={**os.environ, "DATABASE_URL": url},
    )
