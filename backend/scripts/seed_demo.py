from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import get_settings
from backend.app.persistence import AlreadyImported, persist_import

DEMO_DATABASE_URL = "DEMO_DATABASE_URL"
DEMO_FILENAME = "synthetic_demo_students.csv"
DEMO_CSV = """student_id,full_name,email,date_of_birth,grade_level,section,maths,science,english,social_studies,second_language
DEMO-001,Synthetic Demo Student One,demo.one@example.edu,2012-01-01,9,A,80,82,84,86,88
DEMO-002,Synthetic Demo Student Two,demo.two@example.edu,2011-02-02,10,B,65,67,69,71,73
DEMO-003,Synthetic Demo Student Three,demo.three@example.edu,2013-03-03,8,C,45,50,55,60,65
"""


def main() -> None:
    database_url = os.getenv(DEMO_DATABASE_URL)
    if not database_url:
        raise SystemExit("Set DEMO_DATABASE_URL to a separate demo database before running the seed script.")
    database_name = urlsplit(database_url.replace("postgresql+psycopg://", "postgresql://", 1)).path.lstrip("/")
    if database_name == "es_magico_test":
        raise SystemExit("Refusing to seed the protected acceptance database es_magico_test.")

    settings = get_settings()
    connect_args = {"connect_timeout": settings.db_connect_timeout_seconds} if database_url.startswith("postgresql") else {}
    engine = create_engine(database_url, pool_pre_ping=True, connect_args=connect_args)
    try:
        with tempfile.TemporaryDirectory() as directory:
            csv_path = Path(directory) / DEMO_FILENAME
            csv_path.write_text(DEMO_CSV, encoding="utf-8", newline="")
            with Session(engine) as session:
                try:
                    batch, _ = persist_import(session, csv_path, DEMO_FILENAME, date(2026, 1, 1))
                    print(f"Seeded synthetic demo data: batch={batch.id}, students={batch.accepted_rows}, rejected={batch.rejected_rows}")
                except AlreadyImported as duplicate:
                    print(f"Synthetic demo data already seeded: batch={duplicate.batch.id}")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
