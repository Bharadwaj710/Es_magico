from __future__ import annotations

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from .csv_reader import REQUIRED_FIELDS

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
ID_PATTERN = re.compile(r"^[A-Z0-9-]+$")
SECTION_PATTERN = re.compile(r"^[A-F]$")
INTEGER_PATTERN = re.compile(r"^[+-]?\d+$")
DECIMAL_PATTERN = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$")


def _error(code: str, field: str, message: str) -> dict[str, str]:
    return {"code": code, "field": field, "message": message}


def _required(value: str) -> bool:
    return bool(value.strip())


def _parse_date(value: str) -> date | None:
    from datetime import datetime

    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(value.strip(), fmt)
        except ValueError:
            continue
        if parsed.strftime(fmt) == value.strip():
            return parsed.date()
    return None


def validate_record(values: dict[str, str], reference_date: date) -> tuple[dict[str, Any], list[dict[str, str]]]:
    normalized: dict[str, Any] = {}
    errors: list[dict[str, str]] = []

    student_id = values.get("student_id", "").strip().upper()
    if not _required(values.get("student_id", "")):
        errors.append(_error("MISSING_REQUIRED", "student_id", "student_id is required"))
    elif not 3 <= len(student_id) <= 20 or not ID_PATTERN.fullmatch(student_id):
        errors.append(_error("INVALID_FORMAT", "student_id", "student_id must contain 3-20 letters, digits, or hyphens"))
    else:
        normalized["student_id"] = student_id

    full_name = " ".join(values.get("full_name", "").split())
    if not _required(values.get("full_name", "")):
        errors.append(_error("MISSING_REQUIRED", "full_name", "full_name is required"))
    elif not 2 <= len(full_name) <= 100:
        errors.append(_error("OUT_OF_RANGE", "full_name", "full_name must be 2-100 characters"))
    else:
        normalized["full_name"] = full_name

    email = values.get("email", "").strip().lower()
    if not _required(values.get("email", "")):
        errors.append(_error("MISSING_REQUIRED", "email", "email is required"))
    elif not EMAIL_PATTERN.fullmatch(email):
        errors.append(_error("INVALID_FORMAT", "email", "email has an invalid format"))
    else:
        normalized["email"] = email

    date_value = values.get("date_of_birth", "").strip()
    if not _required(date_value):
        errors.append(_error("MISSING_REQUIRED", "date_of_birth", "date_of_birth is required"))
    else:
        birth_date = _parse_date(date_value)
        if birth_date is None:
            errors.append(_error("INVALID_FORMAT", "date_of_birth", "date_of_birth must be YYYY-MM-DD or DD/MM/YYYY"))
        else:
            age = reference_date.year - birth_date.year - ((reference_date.month, reference_date.day) < (birth_date.month, birth_date.day))
            if not 5 <= age <= 25:
                errors.append(_error("OUT_OF_RANGE", "date_of_birth", "age must be between 5 and 25"))
            else:
                normalized["date_of_birth"] = birth_date

    grade = values.get("grade_level", "").strip()
    if not _required(grade):
        errors.append(_error("MISSING_REQUIRED", "grade_level", "grade_level is required"))
    elif not INTEGER_PATTERN.fullmatch(grade):
        errors.append(_error("INVALID_FORMAT", "grade_level", "grade_level must be a whole number"))
    else:
        grade_number = int(grade)
        if not 1 <= grade_number <= 12:
            errors.append(_error("OUT_OF_RANGE", "grade_level", "grade_level must be between 1 and 12"))
        else:
            normalized["grade_level"] = grade_number

    section = values.get("section", "").strip().upper()
    if not _required(values.get("section", "")):
        errors.append(_error("MISSING_REQUIRED", "section", "section is required"))
    elif not SECTION_PATTERN.fullmatch(section):
        errors.append(_error("INVALID_FORMAT", "section", "section must be one letter from A to F"))
    else:
        normalized["section"] = section

    for field in REQUIRED_FIELDS[6:]:
        raw = values.get(field, "").strip()
        if not _required(raw):
            errors.append(_error("MISSING_REQUIRED", field, f"{field} is required"))
            continue
        if not DECIMAL_PATTERN.fullmatch(raw):
            errors.append(_error("INVALID_FORMAT", field, f"{field} must be numeric"))
            continue
        try:
            mark = Decimal(raw)
        except InvalidOperation:
            errors.append(_error("INVALID_FORMAT", field, f"{field} must be numeric"))
            continue
        if not mark.is_finite():
            errors.append(_error("INVALID_FORMAT", field, f"{field} must be numeric"))
        elif not Decimal("0") <= mark <= Decimal("100"):
            errors.append(_error("OUT_OF_RANGE", field, f"{field} must be between 0 and 100"))
        else:
            normalized[field] = mark

    return normalized, errors
