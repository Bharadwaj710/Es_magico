# Implementation Notes

## Data assumptions

- Required columns are `student_id`, `full_name`, `email`, `date_of_birth`, `grade_level`, `section`, `maths`, `science`, `english`, `social_studies`, and `second_language`.
- Header names are normalized; the large supplied file's extra `parent_phone` column is ignored after row-width validation.
- IDs are trimmed and uppercased, then validated as 3–20 letters, digits, or hyphens.
- Names are whitespace-normalized and must be 2–100 characters.
- Emails must match the implemented basic email pattern and are lowercased.
- Dates accept `YYYY-MM-DD` and `DD/MM/YYYY`; age must be 5–25 at the import reference date.
- Grade levels are integers 1–12. Sections are single letters A–F.
- All five marks are required numeric values from 0 through 100.
- Blank records are skipped; malformed-width records are counted and rejected.

The large supplied file contains an additional `parent_phone` column. It is accepted as an extra input column but is not part of the persisted student model.

## Validation and normalization

Validation is deterministic and independent of PostgreSQL. Valid values are normalized before persistence: IDs and sections are uppercased, emails are lowercased, names are whitespace-normalized, and accepted dates/marks become typed values.

## Duplicate handling and persistence

- Duplicate IDs within one file are reported as row errors.
- An identical file SHA-256 returns the existing completed batch and does not create another batch.
- Accepted records with an existing normalized ID update that student; the internal primary key is preserved.
- New accepted IDs are inserted. All batch metadata, accepted changes, and row errors commit in one transaction.
- A failed import rolls back the transaction and returns an error response.

The small import created 16 students. The large import inserted 4,669 new students and updated 16 existing students from the first import. The final distinct student count is therefore 4,685.

Duplicate IDs within one file are rejected as row-level errors. Cross-import duplicate IDs are not rejected: they follow the upsert strategy above.

## Transaction and rollback behavior

Each accepted import creates its batch, accepted student changes, rejected-row diagnostics, and completed summary in one transaction. API validation failures and unexpected persistence failures roll back the session. Duplicate-file detection occurs before a second batch is created.

## Academic reports

- Marks and report totals use `Decimal`; PostgreSQL marks use `NUMERIC(5,2)`.
- Grades: A+ at 90+, A at 80+, B at 70+, C at 60+, D at 50+, otherwise F.
- A subject passes at 33 or above.
- Overall passing requires at least 40% and every subject to pass.
- The frontend displays API report values and does not recalculate grades or pass/fail states.

Reports are calculated from the marks actually stored in PostgreSQL. The acceptance verification independently compared selected stored records and report responses using Decimal arithmetic.

## Database design

- Alembic owns the schema; the application does not call `Base.metadata.create_all()`.
- `students`, `import_batches`, and `import_row_errors` are linked by foreign keys.
- Student IDs are unique and listing indexes support the primary lookup paths.
- Query results are ordered by `student_id`, then internal `id`, for stable pagination.
- The application database is `es_magico_test`; destructive integration tests use only `es_magico_pytest`.
- PostgreSQL connection establishment has a configurable five-second default timeout.

The existing Alembic migration defines the three application tables, student-ID uniqueness, mark/grade/section checks, indexes, and foreign keys. No SQLite fallback or application `create_all()` path is used.

## Error handling and pagination

- Invalid uploads return 400, oversized uploads return 413, missing entities return 404, and database failures return 503 where handled by the API.
- Import error pages are ordered by stored error ID and use page/page-size parameters.
- Student filtering, counting, ordering, and pagination execute in PostgreSQL rather than in React.

The API returns structured error responses for invalid uploads, missing students/batches, oversized uploads, and handled database failures. Student pages use the same predicates for their total count and item query.

## Known limitations

- There is no authentication or authorization layer.
- The import endpoint accepts one upload at a time and has no background job queue.
- The basic email validation is intentionally not a complete RFC email validator.
- Docker files are supplied but were not executed because Docker Desktop's daemon was unavailable during verification.
- Actual OS print-dialog behavior is not automated; print CSS/PDF rendering was verified.
- The latest recorded automated result is 29 backend tests and 4 live Chromium Playwright tests; browser coverage is not a full cross-browser/device matrix.

## Future improvements

These are intentionally not implemented for the assignment submission: authentication, background imports, richer dashboards, audit history, automated backup/restore, production observability, and expanded accessibility/performance testing.
