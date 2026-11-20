# Build Log

## 2026-11-19

- Confirmed the workspace was empty and not yet a Git repository.
- Confirmed Python 3.13.3, Node 24.12.0, npm 11.7.0, FastAPI 0.115.6, Pydantic 2.14.3, and Pytest 8.3.4 are available locally.
- Inspected the sample-pack README and both CSV files; the large file includes the documented `parent_phone` extra column.
- Added the Phase 0 scaffold and Phase 1 CSV engine without database integration or application import APIs.

## 2026-11-19 — Phase 2

- Confirmed PostgreSQL 16 is installed and running, Docker Desktop is installed but its daemon is unavailable, and the project virtual environment now contains SQLAlchemy, Alembic, psycopg, and multipart upload support.
- Added `students`, `import_batches`, and `import_row_errors` models plus the initial Alembic migration.
- Added bounded multipart upload handling, transactional persistence, batch summaries, paginated error retrieval, ID-based updates, and identical-file detection.
- Offline migration SQL generation succeeded. Live migration/import verification is blocked by the local PostgreSQL server rejecting the configured placeholder `postgres` password; no credentials or database state were changed.
- The previous frontend npm issue remains an environment-level `ENOTEMPTY` install failure and is outside Phase 2.

## 2026-11-19 — Phase 3

- Added read-only `GET /api/students`, `GET /api/students/{student_id}`, and `GET /api/students/{student_id}/report` endpoints.
- Added database-side filters, stable pagination, exact ID/name search behavior, student response models, and pure Decimal report calculations.
- Added grading boundary, pass-condition, decimal-calculation, missing-mark, and gated PostgreSQL API/service tests.
- Unit suite result: 19 passed, 3 PostgreSQL integration tests skipped because `TEST_DATABASE_URL` is not configured.
- OpenAPI generation exposes all Phase 3 routes. Live PostgreSQL verification remains unavailable because the local server credentials are still not configured.

## 2026-11-19 — Phase 4

- Repaired frontend dependency state with `npm ci`; no npm processes were running and the affected `frontend/node_modules` belonged to this project.
- Added React Router, typed API clients, responsive application layout, import workflow, student directory, and student report pages.
- Added real upload, import summary/error pagination, server-side student search/filter pagination, report display, retry/empty/loading states, print styling, and Vite `/api` proxy configuration.
- Added `frontend/.env.example` with `VITE_API_BASE_URL=/api`.
- Frontend production build passed and Vite served `/` and `/students` successfully. Browser visual verification and database-backed API verification were not available in this environment.

## 2026-11-19 — Phase 5

- PostgreSQL service is running, but `DATABASE_URL` and `TEST_DATABASE_URL` remain unset; Docker daemon is unavailable. No database credentials or shared database state were changed.
- Backend verification: `19 passed, 3 skipped`. Skips are PostgreSQL integration tests requiring an isolated test database.
- API smoke verification: `/api/health` returned `200`; non-CSV upload returned `400` with a clear validation message.
- Frontend verification: `npm run build` passed; Vite served root and `/students` deep-link HTML successfully. Browser automation and database-backed end-to-end workflow remain unverified.
- No application defects requiring backend/schema changes were found during static and smoke review. Added `*.tsbuildinfo` to `.gitignore` for generated build metadata.
