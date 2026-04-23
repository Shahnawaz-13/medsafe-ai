// lib/api.ts
import {
  AnalysisResult,
  DrugSuggestion,
  AnalyzeRequest,
} from "@/types";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ── Error handling ────────────────────────────────────────────────────
class APIError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
    this.name   = "APIError";
  }
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new APIError(
      body?.detail?.message ||
      body?.message ||
      "Something went wrong. Please try again.",
      res.status,
    );
  }
  return res.json();
}

// ── API functions ─────────────────────────────────────────────────────
export async function analyzeInteractions(
  payload: AnalyzeRequest,
): Promise<AnalysisResult> {
  const res = await fetch(`${API_URL}/api/analyze-interaction`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify(payload),
  });
  return handleResponse<AnalysisResult>(res);
}

export async function getDrugAutocomplete(
  query: string,
): Promise<DrugSuggestion[]> {
  if (query.length < 2) return [];

  const res = await fetch(
    `${API_URL}/api/drug-autocomplete?q=${encodeURIComponent(query)}`
  );

  if (!res.ok) return [];

  const data = await res.json();
  return data.suggestions || [];
}

export async function validateDrug(
  name: string,
): Promise<{ valid: boolean; canonicalName?: string; rxcui?: string }> {
  const res = await fetch(
    `${API_URL}/api/drug-validate?name=${encodeURIComponent(name)}`
  );

  if (!res.ok) return { valid: false };
  const data = await res.json();
  return {
    valid:         data.valid,
    canonicalName: data.canonical_name,
    rxcui:         data.rxcui,
  };
}

export async function sendChatMessage(
  message: string,
  history: { role: string; content: string }[],
): Promise<{ reply: string; timestamp: string }> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body:    JSON.stringify({ message, history }),
  });
  return handleResponse(res);
}

export async function getHistory(page = 1, limit = 10) {
  const res = await fetch(
    `${API_URL}/api/history?page=${page}&limit=${limit}`
  );
  if (!res.ok) return { checks: [], total: 0 };
  return res.json();
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_URL}/health/simple`);
    return res.ok;
  } catch {
    return false;
  }
}

export { APIError };