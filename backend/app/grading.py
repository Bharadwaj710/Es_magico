from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping

SUBJECTS = ("maths", "science", "english", "social_studies", "second_language")
MAX_SUBJECT_MARKS = Decimal("100")
MAX_TOTAL_MARKS = Decimal("500")
SUBJECT_PASS_MARK = Decimal("33")
OVERALL_PASS_PERCENTAGE = Decimal("40")
TWO_PLACES = Decimal("0.01")


@dataclass(frozen=True)
class SubjectReport:
    subject: str
    obtained_marks: Decimal
    maximum_marks: Decimal
    percentage: Decimal
    passed: bool


@dataclass(frozen=True)
class AcademicReport:
    subjects: tuple[SubjectReport, ...]
    total_marks: Decimal
    maximum_total_marks: Decimal
    overall_percentage: Decimal
    grade: str
    passed: bool


def _display_decimal(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


def _grade_for_percentage(percentage: Decimal) -> str:
    if percentage >= Decimal("90"):
        return "A+"
    if percentage >= Decimal("80"):
        return "A"
    if percentage >= Decimal("70"):
        return "B"
    if percentage >= Decimal("60"):
        return "C"
    if percentage >= Decimal("50"):
        return "D"
    return "F"


def calculate_report(marks: Mapping[str, Decimal | int | str | None]) -> AcademicReport:
    if any(marks.get(subject) is None for subject in SUBJECTS):
        raise ValueError("Academic report cannot be generated because a subject mark is missing")

    normalized = {subject: Decimal(str(marks[subject])) for subject in SUBJECTS}
    total = sum(normalized.values(), Decimal("0"))
    overall_percentage = total / MAX_TOTAL_MARKS * Decimal("100")
    subject_reports = tuple(
        SubjectReport(
            subject=subject,
            obtained_marks=_display_decimal(normalized[subject]),
            maximum_marks=MAX_SUBJECT_MARKS,
            percentage=_display_decimal(normalized[subject]),
            passed=normalized[subject] >= SUBJECT_PASS_MARK,
        )
        for subject in SUBJECTS
    )
    return AcademicReport(
        subjects=subject_reports,
        total_marks=_display_decimal(total),
        maximum_total_marks=MAX_TOTAL_MARKS,
        overall_percentage=_display_decimal(overall_percentage),
        grade=_grade_for_percentage(overall_percentage),
        passed=overall_percentage >= OVERALL_PASS_PERCENTAGE and all(subject.passed for subject in subject_reports),
    )
