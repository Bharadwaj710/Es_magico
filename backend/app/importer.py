from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .csv_reader import REQUIRED_FIELDS, CsvInputError, read_csv
from .validators import validate_record


@dataclass(frozen=True)
class RejectedRow:
    line_number: int
    student_id: str | None
    errors: list[dict[str, str]]


@dataclass(frozen=True)
class ImportResult:
    rows_read: int
    accepted: list[dict[str, Any]]
    rejected: list[RejectedRow]
    error_counts: dict[str, int]


def import_csv(path: str | Path, reference_date: date | None = None) -> ImportResult:
    headers, rows = read_csv(path)
    reference = reference_date or date.today()
    positions = {header: index for index, header in enumerate(headers)}
    seen_ids: set[str] = set()
    accepted: list[dict[str, Any]] = []
    rejected: list[RejectedRow] = []
    error_counts: Counter[str] = Counter()

    for row in rows:
        errors: list[dict[str, str]] = []
        student_id: str | None = None
        if len(row.values) != len(headers):
            errors.append({"code": "WRONG_FIELD_COUNT", "field": "__row__", "message": f"expected {len(headers)} fields, got {len(row.values)}"})
        else:
            values = {field: row.values[positions[field]] for field in REQUIRED_FIELDS}
            normalized, errors = validate_record(values, reference)
            candidate_id = normalized.get("student_id")
            student_id = candidate_id
            if candidate_id is not None:
                if candidate_id in seen_ids:
                    errors.append({"code": "DUPLICATE_ID", "field": "student_id", "message": "student_id already appeared earlier"})
                else:
                    seen_ids.add(candidate_id)
        if errors:
            rejected.append(RejectedRow(row.line_number, student_id, errors))
            error_counts.update(error["code"] for error in errors)
        else:
            accepted.append(normalized)

    return ImportResult(len(rows), accepted, rejected, dict(error_counts))
