from __future__ import annotations

import hashlib
from datetime import date, datetime, timezone
from pathlib import Path
from typing import BinaryIO

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .importer import ImportResult, import_csv
from .models import ImportBatch, ImportRowError, Student


class AlreadyImported(Exception):
    def __init__(self, batch: ImportBatch) -> None:
        self.batch = batch


def _student_values(record: dict[str, object]) -> dict[str, object]:
    return {key: record[key] for key in ("student_id", "full_name", "email", "date_of_birth", "grade_level", "section", "maths", "science", "english", "social_studies", "second_language")}


def _hash_file(file_obj: BinaryIO) -> str:
    digest = hashlib.sha256()
    while chunk := file_obj.read(1024 * 1024):
        digest.update(chunk)
    file_obj.seek(0)
    return digest.hexdigest()


def persist_import(
    session: Session,
    file_path: str | Path,
    filename: str,
    reference_date: date | None = None,
) -> tuple[ImportBatch, bool]:
    with Path(file_path).open("rb") as file_obj:
        file_hash = _hash_file(file_obj)
    existing = session.scalar(select(ImportBatch).where(ImportBatch.file_hash == file_hash).order_by(ImportBatch.id.desc()))
    if existing is not None:
        raise AlreadyImported(existing)

    result: ImportResult = import_csv(file_path, reference_date)
    batch = ImportBatch(original_filename=filename[:255], file_hash=file_hash, status="PROCESSING")
    session.add(batch)
    session.flush()

    ids = [record["student_id"] for record in result.accepted]
    existing_students = {}
    if ids:
        existing_students = {student.student_id: student for student in session.scalars(select(Student).where(Student.student_id.in_(ids))).all()}
    new_count = 0
    updated_count = 0
    for record in result.accepted:
        student_id = record["student_id"]
        student = existing_students.get(student_id)
        if student is None:
            student = Student(**_student_values(record), last_import_batch_id=batch.id)
            session.add(student)
            new_count += 1
        else:
            for key, value in _student_values(record).items():
                setattr(student, key, value)
            student.last_import_batch_id = batch.id
            updated_count += 1

    for rejected in result.rejected:
        for error in rejected.errors:
            session.add(ImportRowError(import_batch_id=batch.id, physical_row_number=rejected.line_number, student_id=rejected.student_id, field_name=error["field"], error_code=error["code"], message=error["message"]))

    batch.status = "COMPLETED"
    batch.rows_read = result.rows_read
    batch.accepted_rows = len(result.accepted)
    batch.rejected_rows = len(result.rejected)
    batch.new_student_count = new_count
    batch.updated_student_count = updated_count
    batch.individual_error_count = sum(result.error_counts.values())
    batch.completed_at = datetime.now(timezone.utc)
    session.commit()
    session.refresh(batch)
    return batch, False
