import { expect, test } from "@playwright/test";

type Student = { id: number; student_id: string; full_name: string; grade_level: number; section: string; email: string };
type Report = { student_id: string; total_marks: string; maximum_total_marks: string; overall_percentage: string; grade: string; passed: boolean; subjects: { subject: string; obtained_marks: string; maximum_marks: string; percentage: string; passed: boolean }[] };
const API_BASE = process.env.E2E_API_BASE_URL ?? "/api";

const interceptedSummary = (overrides: Record<string, unknown> = {}) => ({
  id: 99,
  original_filename: "ui3-diagnostics.csv",
  status: "COMPLETED",
  rows_read: 25,
  accepted_rows: 0,
  rejected_rows: 25,
  new_student_count: 0,
  updated_student_count: 0,
  individual_error_count: 25,
  completed_at: null,
  already_imported: false,
  error_preview: [{ row_number: 2, student_id: "STU-QA", field_name: "grade_level", error_code: "INVALID_FORMAT", message: "Invalid grade" }],
  ...overrides,
});

const interceptedError = (rowNumber: number, errorCode = "INVALID_FORMAT") => ({
  row_number: rowNumber,
  student_id: `STU-${rowNumber}`,
  field_name: "grade_level",
  error_code: errorCode,
  message: `Synthetic ${errorCode} diagnostic`,
});

async function json<T>(response: { json(): Promise<unknown> }): Promise<T> { return response.json() as Promise<T>; }

test("live import summary and error pagination are available", async ({ page }) => {
  await page.goto("/import");
  await expect(page.getByRole("heading", { name: "Import results" })).toBeVisible();
  const summary = await json<{ id: number; rows_read: number; accepted_rows: number; rejected_rows: number }>(await page.request.get(`${API_BASE}/imports/1`));
  const errors = await json<{ total: number; items: unknown[] }>(await page.request.get(`${API_BASE}/imports/${summary.id}/errors?page=1&page_size=5`));
  expect(summary).toMatchObject({ id: 1, rows_read: 25, accepted_rows: 16, rejected_rows: 9 });
  expect(errors.total).toBe(9);
  expect(errors.items).toHaveLength(5);
  await page.screenshot({ path: "test-results/import-desktop.png", fullPage: true });
});

test("students page searches, filters, paginates, and navigates", async ({ page }) => {
  const initial = await json<{ items: Student[]; pagination: { total: number; has_next: boolean } }>(await page.request.get(`${API_BASE}/students?limit=20&offset=0`));
  expect(initial.pagination.total).toBe(4685);
  expect(initial.items).toHaveLength(20);
  expect(initial.items.map((item) => item.student_id)).toEqual([...initial.items.map((item) => item.student_id)].sort());
  const chosen = initial.items[0];
  const partial = chosen.full_name.split(" ")[0].slice(0, 4);
  const searchResponse = await page.request.get(`${API_BASE}/students?search=${encodeURIComponent(partial.toLowerCase())}&limit=20&offset=0`);
  expect(searchResponse.ok()).toBeTruthy();
  const search = await json<{ items: Student[]; pagination: { total: number } }>(searchResponse);
  expect(search.items.some((item) => item.full_name.toLowerCase().includes(partial.toLowerCase()))).toBeTruthy();
  const filteredResponse = await page.request.get(`${API_BASE}/students?search=${encodeURIComponent(partial)}&grade_level=${chosen.grade_level}&section=${chosen.section.toLowerCase()}&limit=20&offset=0`);
  const filtered = await json<{ items: Student[]; pagination: { total: number } }>(filteredResponse);
  expect(filtered.items.every((item) => item.grade_level === chosen.grade_level && item.section === chosen.section)).toBeTruthy();
  await page.goto("/students");
  await expect(page.getByRole("heading", { name: "Students" })).toBeVisible();
  await expect(page.getByText("4,685 students")).toBeVisible();
  await page.getByLabel("Search students").fill(partial);
  await expect(page.getByText(partial, { exact: false }).first()).toBeVisible();
  await page.screenshot({ path: "test-results/students-desktop.png", fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload();
  await expect(page.getByRole("heading", { name: "Students" })).toBeVisible();
  await page.screenshot({ path: "test-results/students-mobile.png", fullPage: true });
});

test("five real student reports match backend report data", async ({ page }) => {
  const listing = await json<{ items: Student[] }>(await page.request.get(`${API_BASE}/students?limit=100&offset=0`));
  const reports: Array<{ student: Student; report: Report }> = [];
  const combinations = new Set<string>();
  for (const student of listing.items) {
    const report = await json<Report>(await page.request.get(`${API_BASE}/students/${student.student_id}/report`));
    const key = `${student.grade_level}-${student.section}`;
    if (!combinations.has(key)) {
      reports.push({ student, report });
      combinations.add(key);
    }
    if (reports.length >= 5 && reports.some((item) => !item.report.passed)) break;
  }
  const selected = reports.slice(0, 5);
  if (!selected.some((item) => !item.report.passed)) {
    const failing = reports.find((item) => !item.report.passed);
    if (failing) selected[selected.length - 1] = failing;
  }
  expect(selected.length).toBeGreaterThanOrEqual(5);
  expect(selected.some((item) => item.report.passed)).toBeTruthy();
  expect(selected.some((item) => !item.report.passed)).toBeTruthy();
  for (const item of selected.slice(0, 5)) {
    const total = item.report.subjects.reduce((sum, subject) => sum + Number(subject.obtained_marks), 0);
    expect(Number(item.report.total_marks)).toBeCloseTo(total, 2);
    expect(Number(item.report.overall_percentage)).toBeCloseTo(total / 5, 2);
    await page.goto(`/students/${item.student.student_id}`);
    await expect(page.getByRole("heading", { level: 1, name: item.student.full_name })).toBeVisible();
    await expect(page.getByText(`${item.report.overall_percentage}%`, { exact: false })).toBeVisible();
    await expect(page.getByText(item.report.grade, { exact: true })).toBeVisible();
  }
  await page.screenshot({ path: "test-results/report-desktop.png", fullPage: true });
});

test("unknown student displays a useful not-found state", async ({ page }) => {
  await page.goto("/students/UNKNOWN-STUDENT-999");
  await expect(page.getByText("This student could not be found.")).toBeVisible();
});

test("students clear filters restores the complete server-side listing", async ({ page }) => {
  await page.goto("/students");
  await page.getByLabel("Search students").fill("Rohan");
  await expect(page.getByRole("button", { name: "Clear filters" })).toBeVisible();
  await page.getByRole("button", { name: "Clear filters" }).click();
  await expect(page.getByLabel("Search students")).toHaveValue("");
  await expect(page.getByText("4,685 students")).toBeVisible();
});

test("student report retry recovers from a transient report request failure", async ({ page }) => {
  let attempts = 0;
  await page.route("**/api/students/STU00001/report", async (route) => {
    attempts += 1;
    if (attempts === 1) await route.abort();
    else await route.continue();
  });
  await page.goto("/students/STU00001");
  await expect(page.getByText("The server could not be reached. Check your connection and try again.")).toBeVisible();
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.getByRole("heading", { level: 1, name: "Rohan Kaur" })).toBeVisible();
  expect(attempts).toBeGreaterThan(1);
});

test("import diagnostics failure is visible and retry recovers", async ({ page }) => {
  let diagnosticAttempts = 0;
  await page.route("**/api/imports", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify(interceptedSummary()) });
      return;
    }
    await route.continue();
  });
  await page.route("**/api/imports/99/errors*", async (route) => {
    diagnosticAttempts += 1;
    if (diagnosticAttempts === 1) {
      await route.abort();
      return;
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [interceptedError(2)], page: 1, page_size: 20, total: 1 }) });
  });
  await page.goto("/import");
  await page.locator('input[type="file"]').setInputFiles({ name: "ui3-diagnostics.csv", mimeType: "text/csv", buffer: Buffer.from("student_id,full_name\nSTU-QA,QA Student\n") });
  await page.getByRole("button", { name: "Upload and process" }).click();
  await expect(page.getByText("Validation diagnostics could not be loaded.")).toBeVisible();
  await page.getByRole("button", { name: "Try again" }).click();
  await expect(page.getByRole("table").getByText("INVALID_FORMAT", { exact: true }).first()).toBeVisible();
  expect(diagnosticAttempts).toBeGreaterThan(1);
});

test("import diagnostics show empty results without confusing them with a load failure", async ({ page }) => {
  await page.route("**/api/imports", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify(interceptedSummary({ rows_read: 1, accepted_rows: 1, rejected_rows: 0, individual_error_count: 0, error_preview: [] })) });
      return;
    }
    await route.continue();
  });
  await page.route("**/api/imports/99/errors*", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [], page: 1, page_size: 20, total: 0 }) });
  });
  await page.goto("/import");
  await page.locator('input[type="file"]').setInputFiles({ name: "ui3-clean.csv", mimeType: "text/csv", buffer: Buffer.from("student_id,full_name\nSTU-QA,QA Student\n") });
  await page.getByRole("button", { name: "Upload and process" }).click();
  await expect(page.getByText("No validation errors")).toBeVisible();
  await expect(page.getByText("Validation diagnostics could not be loaded.")).toHaveCount(0);
});

test("import diagnostic filters reset pagination and disclose current-page scope", async ({ page }) => {
  const requestedPages: string[] = [];
  const firstPage = Array.from({ length: 20 }, (_, index) => interceptedError(index + 2));
  const secondPage = Array.from({ length: 5 }, (_, index) => interceptedError(index + 22, "OUT_OF_RANGE"));
  await page.route("**/api/imports", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({ status: 201, contentType: "application/json", body: JSON.stringify(interceptedSummary({ rows_read: 25, rejected_rows: 25, individual_error_count: 25 })) });
      return;
    }
    await route.continue();
  });
  await page.route("**/api/imports/99/errors*", async (route) => {
    const url = new URL(route.request().url());
    const pageNumber = Number(url.searchParams.get("page") ?? "1");
    requestedPages.push(url.toString());
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: pageNumber === 1 ? firstPage : secondPage, page: pageNumber, page_size: 20, total: 25 }) });
  });
  await page.goto("/import");
  await page.locator('input[type="file"]').setInputFiles({ name: "ui3-filter.csv", mimeType: "text/csv", buffer: Buffer.from("student_id,full_name\nSTU-QA,QA Student\n") });
  await page.getByRole("button", { name: "Upload and process" }).click();
  await expect(page.getByText("Page 1")).toBeVisible();
  await page.getByRole("button", { name: "Next" }).click();
  await expect(page.getByText("Page 2")).toBeVisible();
  await page.getByLabel("Filter errors on this page").selectOption("INVALID_FORMAT");
  await expect(page.getByText("Page 1")).toBeVisible();
  await expect(page.getByText("Filtering applies to the currently loaded error page.")).toBeVisible();
  await expect(page.getByRole("table").getByText("INVALID_FORMAT", { exact: true }).first()).toBeVisible();
  expect(requestedPages.some((url) => url.includes("page=2"))).toBeTruthy();
  expect(requestedPages.at(-1)).toContain("page=1");
});

test("shared shell exposes keyboard and semantic accessibility essentials", async ({ page }) => {
  await page.goto("/students");
  await expect(page.getByRole("navigation", { name: "Main navigation" })).toBeVisible();
  await expect(page.getByLabel("Search students")).toBeVisible();
  const headersHaveScope = await page.locator("table thead th").evaluateAll((headers) => headers.every((header) => header.getAttribute("scope") === "col"));
  expect(headersHaveScope).toBeTruthy();
  await page.keyboard.press("Tab");
  await expect(page.locator(":focus")).toHaveAttribute("aria-label", "Import results");
  const focusRing = await page.locator(":focus").evaluate((element) => getComputedStyle(element).boxShadow);
  expect(focusRing).not.toBe("none");
});
