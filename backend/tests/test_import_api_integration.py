from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import Response
from fastapi import UploadFile
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.app.db import Base
from backend.app.api import create_import, get_import, get_import_errors
from backend.app.models import ImportBatch, ImportRowError, Student
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


def _upload(session: Session, response: Response) -> dict:
    upload = UploadFile(
        file=BytesIO(FIXTURE.read_bytes()),
        filename="students_fixture.csv",
        headers=None,
    )
    summary = asyncio.run(create_import(response, upload, session))
    return summary.model_dump()


def test_first_and_duplicate_uploads_preserve_summary_and_database_state(database_engine) -> None:
    with Session(database_engine) as session:
        first_summary = _upload(session, Response(status_code=201))
    assert first_summary["already_imported"] is False
    assert first_summary["accepted_rows"] == 16
    assert first_summary["rejected_rows"] == 9
    assert first_summary["error_preview"]

    with Session(database_engine) as session:
        before = (
            session.scalar(select(func.count()).select_from(ImportBatch)),
            session.scalar(select(func.count()).select_from(Student)),
            session.scalar(select(func.count()).select_from(ImportRowError)),
        )

    duplicate_response = Response()
    with Session(database_engine) as session:
        duplicate_summary = _upload(session, duplicate_response)
    assert duplicate_response.status_code == 200
    assert duplicate_summary["already_imported"] is True
    assert duplicate_summary["id"] == first_summary["id"]
    assert duplicate_summary["original_filename"] == first_summary["original_filename"]
    assert duplicate_summary["accepted_rows"] == first_summary["accepted_rows"]
    assert duplicate_summary["rejected_rows"] == first_summary["rejected_rows"]
    assert duplicate_summary["error_preview"] == first_summary["error_preview"]

    with Session(database_engine) as session:
        after = (
            session.scalar(select(func.count()).select_from(ImportBatch)),
            session.scalar(select(func.count()).select_from(Student)),
            session.scalar(select(func.count()).select_from(ImportRowError)),
        )
    assert after == before == (1, 16, 9)


def test_import_detail_and_error_pagination_remain_functional(database_engine) -> None:
    with Session(database_engine) as session:
        first = _upload(session, Response(status_code=201))
    batch_id = first["id"]

    with Session(database_engine) as session:
        detail = get_import(batch_id, session)
        assert detail.id == batch_id
        assert detail.already_imported is False

        errors = get_import_errors(batch_id, page=1, page_size=2, session=session)
        assert errors.total == 9
        assert len(errors.items) == 2
