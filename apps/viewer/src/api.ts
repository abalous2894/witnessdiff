import type { ComparisonRunDetail, ComparisonRunSummary, HealthResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
    ...init,
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function fetchHealth(): Promise<HealthResponse> {
  return request<HealthResponse>("/health");
}

export function fetchRuns(): Promise<ComparisonRunSummary[]> {
  return request<ComparisonRunSummary[]>("/v1/runs");
}

export function fetchRun(id: string): Promise<ComparisonRunDetail> {
  return request<ComparisonRunDetail>(`/v1/runs/${id}`);
}

export function seedSilentOmissionDemo(): Promise<ComparisonRunDetail> {
  return request<ComparisonRunDetail>("/v1/demo/silent-omission", { method: "POST" });
}
