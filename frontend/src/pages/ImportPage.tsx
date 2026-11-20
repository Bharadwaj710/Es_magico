import { ChangeEvent, DragEvent, useEffect, useState } from "react";
import { getImportErrors, uploadImport } from "../api/imports";
import { ApiError } from "../api/client";
import { ErrorPreview, ImportErrorPage, ImportSummary } from "../types";
import { EmptyState, LoadingState, StatusBadge } from "../components/States";
import { PageHeader } from "../components/PageHeader";

const MAX_FILE_BYTES = 10 * 1024 * 1024;
const formatBytes = (bytes: number) => `${(bytes / 1024 / 1024).toFixed(2)} MB`;

export function ImportPage() {
  const [file, setFile] = useState<File | null>(null);
  const [summary, setSummary] = useState<ImportSummary | null>(null);
  const [errors, setErrors] = useState<ImportErrorPage | null>(null);
  const [errorFilter, setErrorFilter] = useState("");
  const [errorPage, setErrorPage] = useState(1);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [loadingErrors, setLoadingErrors] = useState(false);
  const [message, setMessage] = useState("");

  function selectFile(next?: File) {
    setMessage(""); setSummary(null); setErrors(null); setErrorPage(1);
    if (!next) return;
    if (!next.name.toLowerCase().endsWith(".csv")) { setMessage("Please choose a CSV file."); setFile(null); return; }
    if (next.size > MAX_FILE_BYTES) { setMessage("This file exceeds the 10 MB upload limit."); setFile(null); return; }
    setFile(next);
  }
  function handleDrop(event: DragEvent<HTMLDivElement>) { event.preventDefault(); setDragging(false); selectFile(event.dataTransfer.files[0]); }
  function handleChange(event: ChangeEvent<HTMLInputElement>) { selectFile(event.target.files?.[0]); }
  async function handleUpload() { if (!file) return; setUploading(true); setMessage(""); try { setSummary(await uploadImport(file)); } catch (error) { setMessage(error instanceof ApiError ? error.message : "The import could not be completed."); } finally { setUploading(false); } }

  useEffect(() => { if (!summary) return; setLoadingErrors(true); getImportErrors(summary.id, errorPage).then(setErrors).catch(() => setErrors(null)).finally(() => setLoadingErrors(false)); }, [summary, errorPage]);
  const visibleErrors = errors?.items.filter((item) => !errorFilter || item.error_code === errorFilter) ?? [];
  const errorCodes = [...new Set(summary?.error_preview.map((item) => item.error_code) ?? [])];

  return <><PageHeader eyebrow="DATA OPERATIONS" title="Import results" description="Upload a student results CSV and review validation outcomes." /><section className="upload-grid"><div className={`upload-card ${dragging ? "dragging" : ""}`} onDragOver={(event) => { event.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={handleDrop}><div className="upload-icon">↑</div><h2>Drop your CSV here</h2><p>or browse from your computer</p><label className="button primary file-button">Choose CSV file<input type="file" accept=".csv,text/csv" onChange={handleChange} /></label><p className="upload-hint">UTF-8 CSV · max 10 MB</p>{file && <div className="selected-file"><span className="file-badge">CSV</span><div><strong>{file.name}</strong><small>{formatBytes(file.size)}</small></div><button className="icon-button" aria-label="Remove selected file" onClick={() => setFile(null)}>×</button></div>}{message && <div className="inline-error" role="alert">{message}</div>}{file && !uploading && <button className="button secondary upload-action" onClick={handleUpload}>Upload and process</button>}{uploading && <LoadingState label="Processing file" />}</div><div className="info-card"><div className="eyebrow">WORKFLOW</div><h2>One clean source of truth</h2><p>Every row is checked against the portal’s validation rules. Accepted records become searchable students; rejected rows remain available with precise diagnostics.</p><div className="workflow"><div><span>01</span><p>Select a CSV</p></div><div><span>02</span><p>Validate and import</p></div><div><span>03</span><p>Review exceptions</p></div></div></div></section>{summary && <><section className="section-block"><div className="section-heading"><div><div className="eyebrow">IMPORT #{summary.id}</div><h2>{summary.original_filename}</h2></div><StatusBadge label={summary.already_imported ? "Already imported" : summary.status} passed={summary.status === "COMPLETED"} /></div><div className="metric-grid"><Metric label="Rows read" value={summary.rows_read} /><Metric label="Accepted" value={summary.accepted_rows} tone="success" /><Metric label="Rejected rows" value={summary.rejected_rows} tone="danger" /><Metric label="Validation issues" value={summary.individual_error_count} tone={summary.individual_error_count ? "warning" : "success"} /><Metric label="New students" value={summary.new_student_count} /><Metric label="Updated students" value={summary.updated_student_count} /></div></section><section className="section-block"><div className="section-heading"><div><div className="eyebrow">VALIDATION LOG</div><h2>Rejected row details</h2></div>{errorCodes.length > 0 && <select className="select compact" aria-label="Filter errors" value={errorFilter} onChange={(event) => setErrorFilter(event.target.value)}><option value="">All error codes</option>{errorCodes.map((code) => <option key={code}>{code}</option>)}</select>}</div>{loadingErrors ? <LoadingState label="Loading errors" /> : visibleErrors.length === 0 ? <EmptyState title="No validation errors" message="All processed rows are valid." /> : <ErrorTable errors={visibleErrors} />}{errors && errors.total > errors.page_size && <Pagination page={errorPage} hasNext={errorPage * errors.page_size < errors.total} onChange={setErrorPage} />}</section></>}{!summary && !file && <section className="section-block"><EmptyState title="No imports yet" message="Select a CSV above to begin importing student results." /></section>}</>;
}

function Metric({ label, value, tone = "" }: { label: string; value: number; tone?: string }) { return <div className="metric"><span>{label}</span><strong className={tone}>{value.toLocaleString()}</strong></div>; }
function ErrorTable({ errors }: { errors: ErrorPreview[] }) { return <div className="table-wrap"><table><thead><tr><th>Row</th><th>Student ID</th><th>Field</th><th>Error code</th><th>Message</th></tr></thead><tbody>{errors.map((error, index) => <tr key={`${error.row_number}-${error.field_name}-${index}`}><td>{error.row_number}</td><td className="mono">{error.student_id ?? "—"}</td><td>{error.field_name}</td><td><span className="code-badge">{error.error_code}</span></td><td>{error.message}</td></tr>)}</tbody></table></div>; }
function Pagination({ page, hasNext, onChange }: { page: number; hasNext: boolean; onChange: (page: number) => void }) { return <div className="pagination"><button className="button secondary" disabled={page === 1} onClick={() => onChange(page - 1)}>Previous</button><span>Page {page}</span><button className="button secondary" disabled={!hasNext} onClick={() => onChange(page + 1)}>Next</button></div>; }
