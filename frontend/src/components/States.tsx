import { Link } from "react-router-dom";
import { EmptyIcon } from "./Icons";

export function LoadingState({ label = "Loading" }: { label?: string }) { return <div className="state-card" role="status"><span className="spinner" aria-hidden="true" /><span>{label}...</span></div>; }
export function EmptyState({ title, message }: { title: string; message: string }) { return <div className="state-card empty-state"><div className="empty-icon"><EmptyIcon /></div><h3>{title}</h3><p>{message}</p></div>; }
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) { return <div className="state-card error-state" role="alert"><div className="error-icon" aria-hidden="true">!</div><h3>Something went wrong</h3><p>{message}</p>{onRetry && <button className="button secondary" onClick={onRetry}>Try again</button>}</div>; }
export function NotFoundPage() { return <div className="state-card not-found"><div className="eyebrow">404</div><h1>Page not found</h1><p>The page you're looking for does not exist.</p><Link className="button primary" to="/import">Go to imports</Link></div>; }
export function StatusBadge({ passed, label }: { passed?: boolean; label: string }) { return <span className={`badge ${passed === true ? "success" : passed === false ? "danger" : "neutral"}`}><span className="badge-dot" aria-hidden="true" />{label}</span>; }
