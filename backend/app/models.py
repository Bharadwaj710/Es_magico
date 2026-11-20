from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        CheckConstraint("grade_level BETWEEN 1 AND 12", name="ck_students_grade_level"),
        CheckConstraint("section BETWEEN 'A' AND 'F'", name="ck_students_section"),
        CheckConstraint("maths BETWEEN 0 AND 100", name="ck_students_maths"),
        CheckConstraint("science BETWEEN 0 AND 100", name="ck_students_science"),
        CheckConstraint("english BETWEEN 0 AND 100", name="ck_students_english"),
        CheckConstraint("social_studies BETWEEN 0 AND 100", name="ck_students_social_studies"),
        CheckConstraint("second_language BETWEEN 0 AND 100", name="ck_students_second_language"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    grade_level: Mapped[int] = mapped_column(Integer, nullable=False)
    section: Mapped[str] = mapped_column(String(1), nullable=False)
    maths: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    science: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    english: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    social_studies: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    second_language: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_import_batch_id: Mapped[int | None] = mapped_column(ForeignKey("import_batches.id", ondelete="SET NULL"), nullable=True)

    last_import_batch: Mapped[ImportBatch | None] = relationship(foreign_keys=[last_import_batch_id])


class ImportBatch(Base):
    __tablename__ = "import_batches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    rows_read: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    accepted_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    rejected_rows: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    new_student_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_student_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    individual_error_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    errors: Mapped[list[ImportRowError]] = relationship(back_populates="batch", cascade="all, delete-orphan")


class ImportRowError(Base):
    __tablename__ = "import_row_errors"
    __table_args__ = (Index("ix_import_row_errors_batch_row", "import_batch_id", "physical_row_number"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    import_batch_id: Mapped[int] = mapped_column(ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False)
    physical_row_number: Mapped[int] = mapped_column(Integer, nullable=False)
    student_id: Mapped[str | None] = mapped_column(String(20), nullable=True)
    field_name: Mapped[str] = mapped_column(String(64), nullable=False)
    error_code: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    batch: Mapped[ImportBatch] = relationship(back_populates="errors")
