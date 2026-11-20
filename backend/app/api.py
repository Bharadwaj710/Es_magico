from __future__ import annotations

import os
import tempfile
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .config import get_settings
from .db import get_db
from .models import ImportBatch, ImportRowError
from .persistence import AlreadyImported, persist_import
from .schemas import AcademicReportResponse, ErrorPreview, ImportErrorPage, ImportSummary, Pagination, StudentDetails, StudentListItem, StudentListResponse, SubjectReportResponse
from .student_service import IncompleteAcademicRecord, StudentNotFound, get_report, get_student, list_students

router = APIRouter(prefix="/api")


def _preview(session: Session, batch_id: int, limit: int = 20) -> list[ErrorPreview]:
    errors = session.scalars(select(ImportRowError).where(ImportRowError.import_batch_id == batch_id).order_by(ImportRowError.id).limit(limit)).all()
    return [ErrorPreview(row_number=e.physical_row_number, student_id=e.student_id, field_name=e.field_name, error_code=e.error_code, message=e.message) for e in errors]


def _summary(session: Session, batch: ImportBatch, already_imported: bool = False) -> ImportSummary:
    summary = ImportSummary.model_validate(batch, from_attributes=True)
    return summary.model_copy(update={"already_imported": already_imported, "error_preview": _preview(session, batch.id)})


@router.get("/health")
def api_health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/imports", response_model=ImportSummary, status_code=status.HTTP_201_CREATED)
async def create_import(response: Response, file: UploadFile = File(...), session: Session = Depends(get_db)) -> ImportSummary:
    settings = get_settings()
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="A CSV file is required")
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="es-magico-", suffix=".csv", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
            total = 0
            while chunk := await file.read(1024 * 1024):
                total += len(chunk)
                if total > settings.max_import_file_bytes:
                    raise HTTPException(status_code=413, detail="CSV file exceeds the configured size limit")
                temp_file.write(chunk)
        batch, _ = persist_import(session, temp_path, file.filename, date.today())
        return _summary(session, batch)
    except AlreadyImported as duplicate:
        session.rollback()
        response.status_code = status.HTTP_200_OK
        return _summary(session, duplicate.batch, already_imported=True)
    except HTTPException:
        session.rollback()
        raise
    except (ValueError, UnicodeError) as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Import failed and was rolled back") from exc
    finally:
        if temp_path is not None:
            try:
                os.unlink(temp_path)
            except OSError:
                pass


@router.get("/imports/{batch_id}", response_model=ImportSummary)
def get_import(batch_id: int, session: Session = Depends(get_db)) -> ImportSummary:
    batch = session.get(ImportBatch, batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Import batch not found")
    return _summary(session, batch)


@router.get("/imports/{batch_id}/errors", response_model=ImportErrorPage)
def get_import_errors(batch_id: int, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), session: Session = Depends(get_db)) -> ImportErrorPage:
    if session.get(ImportBatch, batch_id) is None:
        raise HTTPException(status_code=404, detail="Import batch not found")
    total = session.scalar(select(func.count()).select_from(ImportRowError).where(ImportRowError.import_batch_id == batch_id)) or 0
    errors = session.scalars(select(ImportRowError).where(ImportRowError.import_batch_id == batch_id).order_by(ImportRowError.id).offset((page - 1) * page_size).limit(page_size)).all()
    items = [ErrorPreview(row_number=e.physical_row_number, student_id=e.student_id, field_name=e.field_name, error_code=e.error_code, message=e.message) for e in errors]
    return ImportErrorPage(items=items, page=page, page_size=page_size, total=total)


@router.get("/students", response_model=StudentListResponse)
def get_students(
    search: str | None = Query(None, max_length=100),
    grade_level: int | None = Query(None, ge=1, le=12),
    section: str | None = Query(None, min_length=1, max_length=1, pattern="^[A-Fa-f]$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db),
) -> StudentListResponse:
    try:
        page = list_students(session, search.strip() or None if search is not None else None, grade_level, section.upper() if section else None, limit, offset)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    items = [StudentListItem.model_validate(item) for item in page.items]
    return StudentListResponse(items=items, pagination=Pagination(total=page.total, limit=limit, offset=offset, has_next=offset + len(items) < page.total))


@router.get("/students/{student_id}", response_model=StudentDetails)
def get_student_details(student_id: str, session: Session = Depends(get_db)) -> StudentDetails:
    try:
        return StudentDetails.model_validate(get_student(session, student_id))
    except StudentNotFound as exc:
        raise HTTPException(status_code=404, detail="Student not found") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc


@router.get("/students/{student_id}/report", response_model=AcademicReportResponse)
def get_student_report(student_id: str, session: Session = Depends(get_db)) -> AcademicReportResponse:
    try:
        student, report = get_report(session, student_id)
    except StudentNotFound as exc:
        raise HTTPException(status_code=404, detail="Student not found") from exc
    except IncompleteAcademicRecord as exc:
        raise HTTPException(status_code=500, detail="Academic report is unavailable for this student") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return AcademicReportResponse(
        student_id=student.student_id,
        full_name=student.full_name,
        grade_level=student.grade_level,
        section=student.section,
        subjects=[SubjectReportResponse.model_validate(subject.__dict__) for subject in report.subjects],
        total_marks=report.total_marks,
        maximum_total_marks=report.maximum_total_marks,
        overall_percentage=report.overall_percentage,
        grade=report.grade,
        passed=report.passed,
    )
