export interface ErrorPreview { row_number: number; student_id: string | null; field_name: string; error_code: string; message: string; }
export interface ImportSummary { id: number; original_filename: string; status: string; rows_read: number; accepted_rows: number; rejected_rows: number; new_student_count: number; updated_student_count: number; individual_error_count: number; completed_at: string | null; already_imported: boolean; error_preview: ErrorPreview[]; }
export interface ImportErrorPage { items: ErrorPreview[]; page: number; page_size: number; total: number; }
export interface StudentListItem { id: number; student_id: string; full_name: string; grade_level: number; section: string; email: string; }
export interface StudentListResponse { items: StudentListItem[]; pagination: { total: number; limit: number; offset: number; has_next: boolean }; }
export interface StudentDetails extends StudentListItem { date_of_birth: string; maths: string; science: string; english: string; social_studies: string; second_language: string; }
export interface SubjectReport { subject: string; obtained_marks: string; maximum_marks: string; percentage: string; passed: boolean; }
export interface AcademicReport { student_id: string; full_name: string; grade_level: number; section: string; subjects: SubjectReport[]; total_marks: string; maximum_total_marks: string; overall_percentage: string; grade: string; passed: boolean; }
