from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, TextIO

REQUIRED_FIELDS = (
    "student_id",
    "full_name",
    "email",
    "date_of_birth",
    "grade_level",
    "section",
    "maths",
    "science",
    "english",
    "social_studies",
    "second_language",
)


@dataclass(frozen=True)
class CsvRow:
    line_number: int
    values: list[str]


class CsvInputError(ValueError):
    pass


def _counted_lines(stream: TextIO) -> Iterator[str]:
    for line in stream:
        yield line


def _normalize_headers(headers: list[str]) -> list[str]:
    return [header.strip().lower() for header in headers]


def read_csv(path: str | Path) -> tuple[list[str], list[CsvRow]]:
    """Read a UTF-8 CSV while retaining physical row start line numbers."""
    try:
        stream = open(path, "r", encoding="utf-8-sig", newline="")
    except UnicodeDecodeError as exc:
        raise CsvInputError("CSV must be UTF-8 encoded") from exc

    with stream:
        physical_line = 0

        def lines() -> Iterator[str]:
            nonlocal physical_line
            for line in stream:
                physical_line += 1
                yield line

        reader = csv.reader(lines(), strict=True)
        try:
            headers = next(reader)
        except StopIteration as exc:
            raise CsvInputError("CSV is empty") from exc
        except csv.Error as exc:
            raise CsvInputError(f"Invalid CSV near line {physical_line}") from exc

        normalized_headers = _normalize_headers(headers)
        missing = [field for field in REQUIRED_FIELDS if field not in normalized_headers]
        if missing:
            raise CsvInputError(f"Missing required headers: {', '.join(missing)}")

        rows: list[CsvRow] = []
        while True:
            row_start = physical_line + 1
            try:
                values = next(reader)
            except StopIteration:
                break
            except csv.Error as exc:
                rows.append(CsvRow(row_start, []))
                continue
            if not values or all(not value.strip() for value in values):
                continue
            rows.append(CsvRow(row_start, values))

        return normalized_headers, rows
