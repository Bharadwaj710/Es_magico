import { useEffect, useState } from "react";
import { getHealth } from "../api/health";

type HealthState = "checking" | "connected" | "unavailable";

export function HealthStatus() {
  const [state, setState] = useState<HealthState>("checking");

  useEffect(() => {
    const controller = new AbortController();
    getHealth(controller.signal).then(() => {
      if (!controller.signal.aborted) setState("connected");
    }).catch(() => {
      if (!controller.signal.aborted) setState("unavailable");
    });
    return () => controller.abort();
  }, []);

  const labels: Record<HealthState, string> = { checking: "Checking API", connected: "API connected", unavailable: "API unavailable" };
  return <div className={`health-status ${state}`} aria-live="polite"><span className="status-dot" aria-hidden="true" />{labels[state]}</div>;
}
