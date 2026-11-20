import { ImportErrorPage, ImportSummary } from "../types";
import { request } from "./client";

export function uploadImport(file: File): Promise<ImportSummary> {
  const form = new FormData(); form.append("file", file);
  return request<ImportSummary>("/imports", { method: "POST", body: form });
}

export function getImportErrors(id: number, page: number, pageSize = 20): Promise<ImportErrorPage> {
  return request<ImportErrorPage>(`/imports/${id}/errors?page=${page}&page_size=${pageSize}`);
}
