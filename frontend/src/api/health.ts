import { request } from "./client";

type HealthResponse = { status: string };

export async function getHealth(signal?: AbortSignal): Promise<void> {
  const response = await request<HealthResponse>("/health", { signal });
  if (response.status !== "ok") throw new Error("Health check returned an unexpected status");
}
