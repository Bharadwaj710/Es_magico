# Implementation Notes

## Stack and rationale

The backend uses Python, FastAPI, Pydantic, SQLAlchemy, psycopg, Alembic and Pytest. CSV parsing and validation are standard-library code so the import rules remain deterministic and easy to test. PostgreSQL provides transactional persistence, indexed lookups and Decimal-compatible `NUMERIC(5,2)` marks. The frontend uses React, TypeScript, Vite and React Router with custom CSS; it keeps search, filtering, pagination and academic calculations server-driven.

## Data assumptions and validation

Each record requires `student_id`, `full_name`, `email`, `date_of_birth`, `grade_level`, `section` and five marks. Headers are normalized, blank rows are skipped, extra columns are allowed but ignored, and values are normalized before persistence: IDs/sections are uppercase, emails lowercase, names whitespace-normalized, and marks/dates typed. Dates support ISO and `DD/MM/YYYY`; age must be 5–25 at the import reference date. Grades are 1–12, sections A–F, and marks 0–100. Invalid rows retain every field error.

## Import and database decisions

Alembic owns `students`, `import_batches` and `import_row_errors`; the application never calls `create_all()`. Imports use one transaction for batch metadata, student changes and diagnostics. SHA-256 identifies identical files. Duplicate IDs within one file are rejected; an accepted ID in a later file updates the existing student while preserving its internal primary key. A failed persistence operation rolls back.

The original acceptance run produced 25/16/9 for the small file and 5,000/4,685/315 for the large file. The large file had 348 individual validation errors because a rejected row may contain multiple errors. The small import created 16 students; the large import inserted 4,669 and updated 16, producing 4,685 distinct students. The committed `backend/tests/fixtures/students_fixture.csv` is a smaller synthetic fixture for portable tests and is not the supplied acceptance data.

## Academic reports and API behavior

Totals, percentages and stored marks use `Decimal`. Grades are A+ (90+), A (80+), B (70+), C (60+), D (50+) and F otherwise. A subject passes at 33+; overall passing requires at least 40% and every subject to pass. PostgreSQL performs student search, filtering, counting, stable ordering and pagination. The React report displays backend-calculated values without duplicating grading logic.

## Isolation, reliability and limitations

`DATABASE_URL` is the acceptance/application database; destructive integration tests require the separate `TEST_DATABASE_URL` database `es_magico_pytest` and verify the connected database before cleanup. PostgreSQL connection establishment has a configurable five-second default timeout. A synthetic demo seed is available through `backend.scripts.seed_demo`, but it requires an explicitly supplied separate `DEMO_DATABASE_URL` and refuses `es_magico_test`.

There is no authentication, background import queue, audit history or production observability. Email validation is intentionally basic. Docker Compose files and persistent-volume configuration are supplied, but Docker runtime execution remains unverified when the Docker daemon is unavailable. Native OS print-dialog behavior and a full cross-browser accessibility audit are also outside the verified scope.

## Next steps

If this were extended beyond the assignment: add authentication and authorization, background processing with progress reporting, audit/backup operations, richer operational monitoring, and broader browser/accessibility/performance automation.
