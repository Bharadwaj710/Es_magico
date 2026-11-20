import { NavLink, Outlet, useLocation } from "react-router-dom";
import { HealthStatus } from "./HealthStatus";
import { StudentsIcon, UploadIcon } from "./Icons";

const navigation = [
  { href: "/import", label: "Import results", icon: UploadIcon },
  { href: "/students", label: "Students", icon: StudentsIcon },
];

export function AppLayout() {
  const location = useLocation();
  const current = location.pathname.startsWith("/students") ? "Students" : "Import results";

  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><span className="brand-mark">E</span><span>Es Magico<span className="brand-subtitle">Student Results Portal</span></span></div>
      <nav className="nav-list" aria-label="Main navigation">
        {navigation.map((item) => { const Icon = item.icon; return <NavLink key={item.href} to={item.href} aria-label={item.label} className={({ isActive }) => `nav-link ${isActive ? "active" : ""}`}><span className="nav-icon"><Icon /></span><span className="nav-label">{item.label}</span></NavLink>; })}
      </nav>
      <div className="sidebar-footer"><HealthStatus /></div>
    </aside>
    <div className="main-shell">
      <header className="topbar"><div className="mobile-brand">Es Magico</div><nav className="breadcrumb" aria-label="Breadcrumb"><span>Portal</span><span aria-hidden="true">/</span><strong aria-current="page">{current}</strong></nav><div className="avatar" aria-label="Administrator">AD</div></header>
      <main className="page-content"><Outlet /></main>
    </div>
  </div>;
}
