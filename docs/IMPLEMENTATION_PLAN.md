# Implementation Plan

## Completed

- Phase 0: repository foundation, FastAPI health endpoint, React/TypeScript/Vite shell, environment and ignore files.
- Phase 1: CSV profiling, UTF-8/BOM and physical-line-aware reader, deterministic field validation, duplicate tracking, importer, and acceptance tests.
- Phase 2: PostgreSQL models, Alembic initial migration, transactional persistence service, and minimal import/summary/error endpoints.
- Phase 3: database-side student listing/search/filter/pagination, case-insensitive student lookup, and Decimal-based academic reports.
- Phase 4: responsive React import, student directory, and student report screens integrated with the existing API.
- Phase 5: end-to-end verification of backend, frontend build, API smoke paths, and reliability boundaries.

## Phase 2 commands

- Configure `DATABASE_URL` and run `\.venv\Scripts\alembic.exe upgrade head`.
- Start the API with `\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload`.
- Upload CSVs with `POST /api/imports`, inspect a batch with `GET /api/imports/{id}`, and page diagnostics with `GET /api/imports/{id}/errors?page=1&page_size=50`.
- Run tests with `\.venv\Scripts\python.exe -m pytest -q`; set `TEST_DATABASE_URL` to an isolated PostgreSQL database to enable integration tests.

## Next

- Next: review submission readiness and choose only assignment-required follow-up work.

## Deferred

Frontend import and student screens, reports, authentication, Docker, and optional dashboard features remain outside the current phase.
