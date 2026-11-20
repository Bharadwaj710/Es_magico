import { NavLink, Outlet, useLocation } from "react-router-dom";

const navigation = [{ href: "/import", label: "Import results", icon: "↑" }, { href: "/students", label: "Students", icon: "○" }];

export function AppLayout() {
  const location = useLocation();
  const current = location.pathname.startsWith("/students") ? "Students" : "Import results";
  return <div className="app-shell"><aside className="sidebar"><div className="brand"><span className="brand-mark">E</span><span>Es Magico<span className="brand-subtitle">Student Results Portal</span></span></div><nav className="nav-list" aria-label="Main navigation">{navigation.map((item) => <NavLink key={item.href} to={item.href} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}><span className="nav-icon">{item.icon}</span>{item.label}</NavLink>)}</nav><div className="sidebar-footer"><span className="status-dot" /> API connected locally</div></aside><div className="main-shell"><header className="topbar"><div className="mobile-brand">Es Magico</div><div className="breadcrumb">Portal <span>/</span> <strong>{current}</strong></div><div className="avatar" aria-label="Administrator">AD</div></header><main className="page-content"><Outlet /></main></div></div>;
}
