# Implementation Notes

## Data assumptions and validation

- Required columns are `student_id`, `full_name`, `email`, `date_of_birth`, `grade_level`, `section`, `maths`, `science`, `english`, `social_studies`, and `second_language`.
- Header names are normalized; the large supplied file's extra `parent_phone` column is ignored after row-width validation.
- IDs are trimmed and uppercased, then validated as 3–20 letters, digits, or hyphens.
- Names are whitespace-normalized and must be 2–100 characters.
- Emails must match the implemented basic email pattern and are lowercased.
- Dates accept `YYYY-MM-DD` and `DD/MM/YYYY`; age must be 5–25 at the import reference date.
- Grade levels are integers 1–12. Sections are single letters A–F.
- All five marks are required numeric values from 0 through 100.
- Blank records are skipped; malformed-width records are counted and rejected.

## Duplicate handling and persistence

- Duplicate IDs within one file are reported as row errors.
- An identical file SHA-256 returns the existing completed batch and does not create another batch.
- Accepted records with an existing normalized ID update that student; the internal primary key is preserved.
- New accepted IDs are inserted. All batch metadata, accepted changes, and row errors commit in one transaction.
- A failed import rolls back the transaction and returns an error response.

## Academic reports

- Marks and report totals use `Decimal`; PostgreSQL marks use `NUMERIC(5,2)`.
- Grades: A+ at 90+, A at 80+, B at 70+, C at 60+, D at 50+, otherwise F.
- A subject passes at 33 or above.
- Overall passing requires at least 40% and every subject to pass.
- The frontend displays API report values and does not recalculate grades or pass/fail states.

## Database design

- Alembic owns the schema; the application does not call `Base.metadata.create_all()`.
- `students`, `import_batches`, and `import_row_errors` are linked by foreign keys.
- Student IDs are unique and listing indexes support the primary lookup paths.
- Query results are ordered by `student_id`, then internal `id`, for stable pagination.
- The application database is `es_magico_test`; destructive integration tests use only `es_magico_pytest`.
- PostgreSQL connection establishment has a configurable five-second default timeout.

## Error handling and pagination

- Invalid uploads return 400, oversized uploads return 413, missing entities return 404, and database failures return 503 where handled by the API.
- Import error pages are ordered by stored error ID and use page/page-size parameters.
- Student filtering, counting, ordering, and pagination execute in PostgreSQL rather than in React.

## Known limitations

- There is no authentication or authorization layer.
- The import endpoint accepts one upload at a time and has no background job queue.
- The basic email validation is intentionally not a complete RFC email validator.
- Docker files are supplied but were not executed because Docker Desktop's daemon was unavailable during verification.
- Actual OS print-dialog behavior is not automated; print CSS/PDF rendering was verified.

## Future improvements

These are intentionally not implemented for the assignment submission: authentication, background imports, richer dashboards, audit history, automated backup/restore, production observability, and expanded accessibility/performance testing.
