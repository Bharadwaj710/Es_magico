# Es Magico Student Results Portal

## Purpose

Build a reliable portal that validates messy student-result CSV files, imports valid records, explains rejected rows, and later displays searchable academic reports.

## Stack

- Backend: Python 3.12+, FastAPI, Pydantic, SQLAlchemy, standard-library CSV, Pytest.
- Frontend: React, TypeScript, Vite, and Tailwind CSS.
- PostgreSQL is the Phase 2 database; Docker deployment remains deferred.

## Conventions

Use small typed modules, pure validation functions, explicit error codes, deterministic tests, and meaningful names. Keep formatting and lint configuration close to the tool defaults. Do not add dependencies without a concrete need.

## Architecture and phase rules

Keep CSV reading, field validation, import orchestration, and grading separate. Phase 0 establishes the repository and health endpoint. Phase 1 implements only dataset profiling and the independent CSV validation engine. Phase 2 adds PostgreSQL persistence and a narrow import API. Full student APIs, import screens, reports, and deployment belong to later phases.

## Testing

Run the focused Pytest suite and acceptance tests against the supplied CSV files. Tests must exercise actual processing and must not encode sample-specific corrections.

## Security

Never commit secrets. Treat uploaded files as untrusted input, use safe file handling, enforce size/type limits at the API boundary when uploads are added, and do not execute or interpret CSV content as code.

Avoid unnecessary dependencies, infrastructure, abstraction, and optimization.
