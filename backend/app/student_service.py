from __future__ import annotations

import re
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .grading import AcademicReport, calculate_report
from .models import Student

ID_LIKE_PATTERN = re.compile(r"^[A-Za-z0-9-]{3,20}$")


@dataclass(frozen=True)
class StudentPage:
    items: list[dict[str, object]]
    total: int


class StudentNotFound(LookupError):
    pass


class IncompleteAcademicRecord(ValueError):
    pass


def _filters(search: str | None, grade_level: int | None, section: str | None):
    predicates = []
    if search:
        if ID_LIKE_PATTERN.fullmatch(search) and any(character.isdigit() or character == "-" for character in search):
            predicates.append(Student.student_id == search.upper())
        else:
            predicates.append(func.lower(Student.full_name).contains(search.lower(), autoescape=True))
    if grade_level is not None:
        predicates.append(Student.grade_level == grade_level)
    if section is not None:
        predicates.append(Student.section == section.upper())
    return predicates


def list_students(session: Session, search: str | None, grade_level: int | None, section: str | None, limit: int, offset: int) -> StudentPage:
    predicates = _filters(search, grade_level, section)
    count_query = select(func.count(Student.id))
    item_query = select(Student.id, Student.student_id, Student.full_name, Student.grade_level, Student.section, Student.email).order_by(Student.student_id.asc(), Student.id.asc()).limit(limit).offset(offset)
    if predicates:
        count_query = count_query.where(*predicates)
        item_query = item_query.where(*predicates)
    total = session.scalar(count_query) or 0
    items = [dict(row) for row in session.execute(item_query).mappings().all()]
    return StudentPage(items=items, total=total)


def get_student(session: Session, student_id: str) -> Student:
    student = session.scalar(select(Student).where(Student.student_id == student_id.strip().upper()))
    if student is None:
        raise StudentNotFound(student_id)
    return student


def get_report(session: Session, student_id: str) -> tuple[Student, AcademicReport]:
    student = get_student(session, student_id)
    try:
        report = calculate_report({subject: getattr(student, subject) for subject in ("maths", "science", "english", "social_studies", "second_language")})
    except (TypeError, ValueError) as exc:
        raise IncompleteAcademicRecord(str(exc)) from exc
    return student, report
