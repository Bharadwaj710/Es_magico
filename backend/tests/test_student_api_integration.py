from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from backend.app.db import Base
from backend.app.models import Student
from backend.app.persistence import persist_import
from backend.app.student_service import get_report, list_students
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
    with Session(engine) as session:
        persist_import(session, FIXTURE, "students_fixture.csv", date(2026, 11, 19))
    yield engine
    verify_test_database(engine)
    Base.metadata.drop_all(engine)
    stamp_test_database_base()
    engine.dispose()


def test_listing_filters_pagination_and_report(database_engine) -> None:
    with Session(database_engine) as session:
        page = list_students(session, "yash", None, None, 20, 0)
        assert page.total == 1
        assert page.items[0]["full_name"] == "Yash Fernandes"

        filtered = list_students(session, None, 12, "A", 5, 0)
        assert filtered.total == len(filtered.items)
        assert all(student["grade_level"] == 12 and student["section"] == "A" for student in filtered.items)

        student, report = get_report(session, "stu00001")
        assert student.student_id == "STU00001"
        assert report.total_marks == Decimal("297.60")
        assert report.overall_percentage == Decimal("59.52")
