"""create import and student tables

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_batches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rows_read", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("accepted_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rejected_rows", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("new_student_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_student_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("individual_error_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_import_batches_file_hash", "import_batches", ["file_hash"])
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.String(length=20), nullable=False),
        sa.Column("full_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("grade_level", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=1), nullable=False),
        sa.Column("maths", sa.Numeric(5, 2), nullable=False),
        sa.Column("science", sa.Numeric(5, 2), nullable=False),
        sa.Column("english", sa.Numeric(5, 2), nullable=False),
        sa.Column("social_studies", sa.Numeric(5, 2), nullable=False),
        sa.Column("second_language", sa.Numeric(5, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("last_import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="SET NULL")),
        sa.CheckConstraint("grade_level BETWEEN 1 AND 12", name="ck_students_grade_level"),
        sa.CheckConstraint("section BETWEEN 'A' AND 'F'", name="ck_students_section"),
        sa.CheckConstraint("maths BETWEEN 0 AND 100", name="ck_students_maths"),
        sa.CheckConstraint("science BETWEEN 0 AND 100", name="ck_students_science"),
        sa.CheckConstraint("english BETWEEN 0 AND 100", name="ck_students_english"),
        sa.CheckConstraint("social_studies BETWEEN 0 AND 100", name="ck_students_social_studies"),
        sa.CheckConstraint("second_language BETWEEN 0 AND 100", name="ck_students_second_language"),
        sa.UniqueConstraint("student_id", name="uq_students_student_id"),
    )
    op.create_index("ix_students_student_id", "students", ["student_id"])
    op.create_table(
        "import_row_errors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("import_batch_id", sa.Integer(), sa.ForeignKey("import_batches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("physical_row_number", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.String(length=20), nullable=True),
        sa.Column("field_name", sa.String(length=64), nullable=False),
        sa.Column("error_code", sa.String(length=32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
    )
    op.create_index("ix_import_row_errors_batch_row", "import_row_errors", ["import_batch_id", "physical_row_number"])


def downgrade() -> None:
    op.drop_index("ix_import_row_errors_batch_row", table_name="import_row_errors")
    op.drop_table("import_row_errors")
    op.drop_index("ix_students_student_id", table_name="students")
    op.drop_table("students")
    op.drop_index("ix_import_batches_file_hash", table_name="import_batches")
    op.drop_table("import_batches")
