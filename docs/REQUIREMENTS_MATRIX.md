# Assignment Requirement Matrix

This matrix covers requirements stated in the supplied assignment brief and implementation phases. Evidence refers to repository code or verification runs; it does not infer requirements that were not stated.

| Requirement | Implementation location | Verification evidence | Status | Limitations |
|---|---|---|---|---|
| Parse the supplied student CSV files | `backend/app/csv_reader.py`, `backend/app/importer.py` | Supplied-file acceptance results; unit tests | Complete | No generated substitute data used |
| Validate required fields and report row errors | `backend/app/validators.py`, `backend/app/persistence.py` | 9 small-file and 315 large-file rejected rows persisted | Complete | Validation follows the defined rules |
| Preserve physical row numbers and individual errors | `backend/app/csv_reader.py`, `backend/app/models.py` | 357 persisted individual errors | Complete | — |
| Import accepted records transactionally into PostgreSQL | `backend/app/persistence.py`, `alembic/versions/0001_initial.py` | PostgreSQL acceptance batches 1 and 2 | Complete | PostgreSQL required |
| Handle duplicate files | `backend/app/persistence.py`, `backend/app/api.py` | Backend integration coverage | Complete | Duplicate behavior returns the original batch |
| Upsert existing student IDs | `backend/app/persistence.py` | Batch 2 recorded 4,669 new and 16 updated | Complete | No history table for prior values |
| Expose import summaries and paged errors | `backend/app/api.py`, `frontend/src/pages/ImportPage.tsx` | Live browser test 1 | Complete | Acceptance files were not uploaded during browser verification |
| Search and filter students server-side | `backend/app/student_service.py`, `backend/app/api.py` | Live browser test 2 | Complete | No authentication |
| Case-insensitive lookup and stable pagination | `backend/app/student_service.py` | Live browser test 2 and integration tests | Complete | — |
| Generate academic reports from stored marks | `backend/app/grading.py`, `backend/app/api.py` | Five real reports and Decimal cross-checks | Complete | — |
| Implement grade boundaries and pass rules | `backend/app/grading.py` | Grading tests and live passing/failing reports | Complete | Rules are the implemented assignment policy |
| Provide React screens and responsive behavior | `frontend/src/pages`, `frontend/src/components`, `frontend/src/styles.css` | Four live Playwright tests; desktop/mobile screenshots | Complete | Browser matrix is Chromium-focused |
| Use PostgreSQL/Alembic schema | `backend/app/models.py`, `alembic/` | Migration and schema inspection | Complete | No SQLite fallback |
| Isolate destructive integration tests | `backend/tests/db_guard.py`, integration fixtures | 27 backend tests passed; database identity checks | Complete | Requires a separately created PostgreSQL test database |
| Bound PostgreSQL connection establishment | `backend/app/config.py`, `backend/app/db.py` | Focused timeout test; measured 5.016-second failure | Complete | Timeout is configurable through environment |
| Supply Docker execution support | `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml` | Files prepared; Docker daemon unavailable | Partial | Docker execution remains unverified |
| Provide documentation and reproducible setup | `README.md`, `NOTES.md`, `.env.example` | Repository audit | Complete | Local passwords must be supplied by evaluator |
