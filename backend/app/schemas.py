from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ErrorPreview(BaseModel):
    row_number: int
    student_id: str | None
    field_name: str
    error_code: str
    message: str


class ImportSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    status: str
    rows_read: int
    accepted_rows: int
    rejected_rows: int
    new_student_count: int
    updated_student_count: int
    individual_error_count: int
    completed_at: datetime | None
    already_imported: bool = False
    error_preview: list[ErrorPreview] = Field(default_factory=list)


class ImportErrorPage(BaseModel):
    items: list[ErrorPreview]
    page: int
    page_size: int
    total: int


class Pagination(BaseModel):
    total: int
    limit: int
    offset: int
    has_next: bool


class StudentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    full_name: str
    grade_level: int
    section: str
    email: str


class StudentListResponse(BaseModel):
    items: list[StudentListItem]
    pagination: Pagination


class StudentDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: str
    full_name: str
    email: str
    date_of_birth: date
    grade_level: int
    section: str
    maths: Decimal
    science: Decimal
    english: Decimal
    social_studies: Decimal
    second_language: Decimal


class SubjectReportResponse(BaseModel):
    subject: str
    obtained_marks: Decimal
    maximum_marks: Decimal
    percentage: Decimal
    passed: bool


class AcademicReportResponse(BaseModel):
    student_id: str
    full_name: str
    grade_level: int
    section: str
    subjects: list[SubjectReportResponse]
    total_marks: Decimal
    maximum_total_marks: Decimal
    overall_percentage: Decimal
    grade: str
    passed: bool
