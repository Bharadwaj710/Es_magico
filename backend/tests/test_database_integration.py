from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.app.db import Base
from backend.app.models import ImportBatch, ImportRowError, Student
from backend.app.persistence import AlreadyImported, persist_import
from backend.tests.db_guard import (
    require_test_database_url,
    stamp_test_database_base,
    upgrade_test_database,
    verify_test_database,
)

FIXTURE = Path(__file__).parent / "fixtures" / "students_fixture.csv"


@pytest.fixture()
def database_engine():
    engine = create_engine(require_test_database_url(), pool_pre_ping=True)
    verify_test_database(engine)
    Base.metadata.drop_all(engine)
    stamp_test_database_base()
    upgrade_test_database()
    yield engine
    verify_test_database(engine)
    Base.metadata.drop_all(engine)
    stamp_test_database_base()
    engine.dispose()


def test_migration_and_small_import(database_engine) -> None:
    with Session(database_engine) as session:
        batch, already_imported = persist_import(session, FIXTURE, "students_fixture.csv", date(2026, 11, 19))
        assert not already_imported
        assert (batch.rows_read, batch.accepted_rows, batch.rejected_rows) == (25, 16, 9)
        assert session.scalar(select(Student.id).limit(1)) is not None
        assert session.scalar(select(ImportRowError.id).where(ImportRowError.import_batch_id == batch.id)) is not None


def test_identical_import_is_reported_without_duplication(database_engine) -> None:
    with Session(database_engine) as session:
        first, _ = persist_import(session, FIXTURE, "students_fixture.csv", date(2026, 11, 19))
        with pytest.raises(AlreadyImported) as duplicate:
            persist_import(session, FIXTURE, "students_fixture.csv", date(2026, 11, 19,))
        assert duplicate.value.batch.id == first.id
        assert session.scalar(select(func.count()).select_from(ImportBatch)) == 1
