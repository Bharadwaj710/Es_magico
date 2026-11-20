import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "./components/AppLayout";
import { NotFoundPage } from "./components/States";
import { ImportPage } from "./pages/ImportPage";
import { StudentReportPage } from "./pages/StudentReportPage";
import { StudentsPage } from "./pages/StudentsPage";
import "./styles.css";

function App() {
  return <BrowserRouter><Routes><Route element={<AppLayout />}><Route path="/" element={<Navigate to="/import" replace />} /><Route path="/import" element={<ImportPage />} /><Route path="/students" element={<StudentsPage />} /><Route path="/students/:studentId" element={<StudentReportPage />} /><Route path="*" element={<NotFoundPage />} /></Route></Routes></BrowserRouter>;
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
