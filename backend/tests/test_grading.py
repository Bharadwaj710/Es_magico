from decimal import Decimal

import pytest

from backend.app.grading import SUBJECTS, calculate_report


def marks(value: str | int) -> dict[str, Decimal]:
    return {subject: Decimal(str(value)) for subject in SUBJECTS}


@pytest.mark.parametrize(
    ("percentage", "grade"),
    [("90", "A+"), ("89.99", "A"), ("80", "A"), ("79.99", "B"), ("70", "B"), ("69.99", "C"), ("60", "C"), ("59.99", "D"), ("50", "D"), ("49.99", "F")],
)
def test_grade_boundaries(percentage: str, grade: str) -> None:
    report = calculate_report(marks(percentage))
    assert report.grade == grade


def test_decimal_calculations_and_pass_conditions() -> None:
    report = calculate_report({"maths": Decimal("33.3"), "science": Decimal("34.4"), "english": Decimal("35.5"), "social_studies": Decimal("36.6"), "second_language": Decimal("37.7")})
    assert report.total_marks == Decimal("177.50")
    assert report.overall_percentage == Decimal("35.50")
    assert report.grade == "F"
    assert report.passed is False

    passing = calculate_report(marks("40"))
    assert passing.overall_percentage == Decimal("40.00")
    assert passing.passed is True


def test_one_subject_below_threshold_fails() -> None:
    subject_marks = marks("50")
    subject_marks["science"] = Decimal("32.99")
    report = calculate_report(subject_marks)
    assert report.overall_percentage >= Decimal("40")
    assert report.passed is False
    assert next(subject for subject in report.subjects if subject.subject == "science").passed is False


def test_missing_marks_are_rejected() -> None:
    incomplete = marks("50")
    incomplete["english"] = None
    with pytest.raises(ValueError, match="mark is missing"):
        calculate_report(incomplete)
