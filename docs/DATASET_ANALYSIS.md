# Dataset Analysis

Profiled from the supplied sample pack on 2026-11-19 using the Phase 1 CSV reader and a reference date of 2026-11-19.

## File findings

| File | Bytes | Encoding/BOM | Line endings | Header fields | Physical lines | Data rows read | Blank records | Widths among physical data rows |
|---|---:|---|---|---:|---:|---:|---:|---|
| `students_small.csv` | 2,176 | UTF-8, no BOM | LF (28) | 11 | 28 | 25 | 2 | 11: 24, 0: 1, 10: 2 |
| `students_sample.csv` | 492,214 | UTF-8 with BOM | CRLF (5,011) | 12 | 5,011 | 5,000 | 10 | 12: 4,985, 0: 5, 11: 9, 13: 8, 1: 3 |

The small file has the required 11 columns. The large file has the same required columns plus the documented `parent_phone` column. Header order and casing are accepted by the implementation; extra fields are ignored after row-width validation.

Blank records are skipped and are not included in `rows_read`. Rows with non-header widths are included in `rows_read` and rejected as whole rows.

## Validation results

| File | Rows read | Accepted | Rejected | Individual errors |
|---|---:|---:|---:|---:|
| `students_small.csv` | 25 | 16 | 9 | 9 |
| `students_sample.csv` | 5,000 | 4,685 | 315 | 348 |

Error-code counts include every issue, while rejected-row counts count each row once:

- `students_small.csv`: `OUT_OF_RANGE` 2, `INVALID_FORMAT` 3, `MISSING_REQUIRED` 2, `WRONG_FIELD_COUNT` 1, `DUPLICATE_ID` 1.
- `students_sample.csv`: `INVALID_FORMAT` 161, `OUT_OF_RANGE` 59, `WRONG_FIELD_COUNT` 15, `MISSING_REQUIRED` 53, `DUPLICATE_ID` 60.

The acceptance counts are produced by processing the files with the rules, not by sample-specific exceptions.
