import { expect, test } from "@playwright/test";

type Student = { id: number; student_id: string; full_name: string; grade_level: number; section: string; email: string };
type Report = { student_id: string; total_marks: string; maximum_total_marks: string; overall_percentage: string; grade: string; passed: boolean; subjects: { subject: string; obtained_marks: string; maximum_marks: string; percentage: string; passed: boolean }[] };
const API_BASE = process.env.E2E_API_BASE_URL ?? "/api";

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
