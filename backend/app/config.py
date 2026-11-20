from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    database_url: str
    max_import_file_bytes: int
    db_connect_timeout_seconds: int


def get_settings() -> Settings:
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:REPLACE_WITH_LOCAL_PASSWORD@127.0.0.1:5432/es_magico",
        ),
        max_import_file_bytes=int(os.getenv("MAX_IMPORT_FILE_BYTES", "10485760")),
        db_connect_timeout_seconds=int(os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "5")),
    )
