# Es Magico Student Results Portal

Es Magico is a full-stack student-results portal that validates supplied CSV files, persists accepted students in PostgreSQL, records row-level rejection diagnostics, and exposes searchable student reports through a React frontend.

## Features

- Strict CSV parsing with UTF-8/BOM support and physical-row diagnostics.
- Validation of identifiers, names, emails, dates, grades, sections, and marks.
- Transactional PostgreSQL imports with batch summaries and row errors.
- SHA-256 duplicate-file detection.
- Normalized student-ID upserts that preserve the internal student primary key.
- Database-side search, grade/section filters, stable pagination, and counts.
- Decimal-based academic reports with subject and overall pass/fail results.
- Responsive React screens for imports, students, and reports.

## Architecture and stack

- Backend: Python 3.12+, FastAPI, Pydantic, SQLAlchemy 2, psycopg, Alembic, Pytest.
- Frontend: React, TypeScript, Vite, React Router, Playwright.
- Database: PostgreSQL 16.
- The frontend calls `/api`; Vite proxies that path to FastAPI during local development.

## Project structure

```text
backend/app/        FastAPI routes, CSV processing, persistence, grading
backend/tests/      unit, integration, isolation, and timeout tests
alembic/            database migration environment and revisions
frontend/src/       React application
frontend/tests/     live Playwright verification
docs/               implementation history and decisions
docker-compose.yml  optional PostgreSQL/backend/frontend deployment
```

## Prerequisites

- Python 3.12 or newer.
- Node.js 20 or newer and npm.
- PostgreSQL 16 for local execution.
- Optional: Docker Desktop with Compose.

Create an application role and two databases: `es_magico_test` for application/acceptance data and `es_magico_pytest` for destructive integration tests. Never point both URLs at the same database.

## Environment configuration

Copy `.env.example` to `.env` and replace only the local password placeholders. Keep `.env` untracked.

```text
DATABASE_URL=postgresql+psycopg://es_magico_app:<password>@127.0.0.1:5432/es_magico_test
TEST_DATABASE_URL=postgresql+psycopg://es_magico_app:<password>@127.0.0.1:5432/es_magico_pytest
DB_CONNECT_TIMEOUT_SECONDS=5
MAX_IMPORT_FILE_BYTES=10485760
```

The test fixtures verify `current_database()` through PostgreSQL and allow destructive cleanup only on `es_magico_pytest`.

## Backend setup and execution

From the repository root:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[test]"
.venv\Scripts\alembic.exe upgrade head
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

## Frontend setup and execution

```powershell
cd frontend
npm ci
npm run dev
```

For a different local backend target, set `VITE_PROXY_TARGET` before starting Vite. The production build is created with `npm run build`; run it with `npm run preview`.

## CSV imports

Do not alter the supplied files. Upload a CSV through the UI or with:

```powershell
curl.exe -X POST -F "file=@D:\path\students_small.csv" http://127.0.0.1:8000/api/imports
```

The supplied acceptance results are 25 read/16 accepted/9 rejected for `students_small.csv`, and 5,000 read/4,685 accepted/315 rejected for `students_sample.csv`.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| POST | `/api/imports` | Import one CSV file |
| GET | `/api/imports/{id}` | Retrieve an import summary |
| GET | `/api/imports/{id}/errors?page=1&page_size=50` | Page import errors |
| GET | `/api/students` | Search, filter, sort, and paginate students |
| GET | `/api/students/{student_id}` | Retrieve one student |
| GET | `/api/students/{student_id}/report` | Retrieve the academic report |

Student listing query parameters are `search`, `grade_level`, `section`, `limit`, and `offset`.

## Tests and verification

Run backend tests only after configuring the isolated `TEST_DATABASE_URL`:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

The suite runs destructive cleanup only against `es_magico_pytest`. Build and live browser checks:

```powershell
cd frontend
npm run build
$env:E2E_BASE_URL="http://127.0.0.1:5173"
npm run test:e2e
```

The live Playwright tests require a running FastAPI backend and existing imported data; they do not upload the supplied CSVs.

## Docker

Docker support is provided in `docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`, and `nginx.conf`. Copy `.env.docker.example` to `.env.docker`, set a local PostgreSQL password, and run:

```powershell
docker compose --env-file .env.docker up --build
```

The Compose database uses a named persistent volume. Docker execution was not verified in this environment because the Docker daemon was unavailable.

## Evidence

Live verification artifacts are kept locally under `frontend/test-results/` and are ignored by Git. They include import, desktop student, mobile student, academic report screenshots, and a print-rendered PDF.
