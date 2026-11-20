import { AcademicReport, StudentDetails, StudentListResponse } from "../types";
import { request } from "./client";

export interface StudentQuery { search?: string; grade_level?: string; section?: string; limit: number; offset: number; }

export function getStudents(query: StudentQuery): Promise<StudentListResponse> {
  const params = new URLSearchParams({ limit: String(query.limit), offset: String(query.offset) });
  if (query.search) params.set("search", query.search);
  if (query.grade_level) params.set("grade_level", query.grade_level);
  if (query.section) params.set("section", query.section);
  return request<StudentListResponse>(`/students?${params.toString()}`);
}

export function getStudent(studentId: string): Promise<StudentDetails> { return request<StudentDetails>(`/students/${encodeURIComponent(studentId)}`); }
export function getStudentReport(studentId: string): Promise<AcademicReport> { return request<AcademicReport>(`/students/${encodeURIComponent(studentId)}/report`); }
