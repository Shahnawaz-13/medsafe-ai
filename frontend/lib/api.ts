import { AnalysisResult, AnalyzeRequest, DrugSuggestion } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

type ApiObject = Record<string, unknown>;

function asObject(value: unknown): ApiObject {
  return value && typeof value === "object" ? (value as ApiObject) : {};
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" ? value : fallback;
}

function asBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function mapAnalysisResponse(data: unknown): AnalysisResult {
  const obj = asObject(data);

  return {
    checkId: asString(obj.check_id),
    drugsSubmitted: asNumber(obj.drugs_submitted),
    drugsIdentified: asNumber(obj.drugs_identified),

    drugList: asArray(obj.drug_list).map((item) => {
      const d = asObject(item);
      return {
        inputName: asString(d.input_name),
        normalizedName: asString(d.normalized_name),
        rxcui: asString(d.rxcui),
        identified: asBoolean(d.identified),
      };
    }),

    pairsChecked: asNumber(obj.pairs_checked),
    interactionsFound: asNumber(obj.interactions_found),

    pairs: asArray(obj.pairs).map((item) => {
      const p = asObject(item);
      return {
        drug1: asString(p.drug1),
        drug2: asString(p.drug2),
        severity: asString(p.severity, "none") as AnalysisResult["pairs"][number]["severity"],
        severityEmoji: asString(p.severity_emoji, "⚪"),
        plainExplanation: asString(p.plain_explanation),
        whatToWatchFor: asString(p.what_to_watch_for),
        actionRequired: asString(p.action_required),
        saferAlternatives: asArray(p.safer_alternatives).map((x) => asString(x)),
        mechanism: asString(p.mechanism),
        sources: asArray(p.sources).map((x) => asString(x)),
      };
    }),

    overallSeverity: asString(obj.overall_severity, "none") as AnalysisResult["overallSeverity"],
    overallEmoji: asString(obj.overall_emoji, "⚪"),
    summary: asString(obj.summary),
    disclaimer: asString(obj.disclaimer),
    generatedAt: asString(obj.generated_at),
    responseTimeMs: asNumber(obj.response_time_ms),
    aiProvider: asString(obj.ai_provider, "groq"),
    cachedPairs: asNumber(obj.cached_pairs),
    isFallback: asBoolean(obj.is_fallback),
  };
}

async function handleResponse<T>(res: Response): Promise<T> {
  const contentType = res.headers.get("content-type") || "";
  let data: unknown = null;

  if (contentType.includes("application/json")) {
    data = await res.json();
  } else {
    const text = await res.text();
    data = text ? { message: text } : null;
  }

  if (!res.ok) {
    const errorData = asObject(data);

    throw new Error(
      asString(errorData.detail) ||
        asString(errorData.message) ||
        `Request failed with status ${res.status}`
    );
  }

  return data as T;
}

function requireApiUrl(): string {
  if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not defined");
  }
  return API_URL;
}

export async function getDrugAutocomplete(
  query: string
): Promise<DrugSuggestion[]> {
  const base = requireApiUrl();
  const trimmed = query.trim();

  if (trimmed.length < 2) return [];

  const res = await fetch(
    `${base}/api/drug-autocomplete?q=${encodeURIComponent(trimmed)}`
  );

  const data = await handleResponse<unknown>(res);

  const suggestions = Array.isArray(data)
    ? data
    : asArray(asObject(data).suggestions);

  return suggestions
    .map((item) => {
      const obj = asObject(item);
      return {
        name: asString(obj.name || obj.drug_name || obj.display_name || obj.term),
        rxcui: asString(obj.rxcui || obj.id),
      };
    })
    .filter((item) => item.name);
}

export async function analyzeInteractions(
  payload: AnalyzeRequest
): Promise<AnalysisResult> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/analyze-interaction`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      drugs: payload.drugs,
      age: payload.age,
      gender: payload.gender,
      allergies: payload.allergies,
      session_id: payload.sessionId,
    }),
  });

  const data = await handleResponse<unknown>(res);
  return mapAnalysisResponse(data);
}

export async function sendChatMessage(
  message: string,
  currentDrugs: string[] = []
): Promise<{ response: string }> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      current_drugs: currentDrugs,
    }),
  });

  return handleResponse<{ response: string }>(res);
}

export interface HistoryItem {
  checkId: string;
  drugsChecked: string[];
  severity: string;
  checkedAt: string;
  pairsFound: number;
}

export interface HistoryApiResponse {
  checks: HistoryItem[];
  total: number;
}

export async function getHistory(
  limit = 20,
  offset = 0
): Promise<HistoryItem[] | HistoryApiResponse> {
  const base = requireApiUrl();

  const res = await fetch(
    `${base}/api/history?limit=${limit}&offset=${offset}`,
    {
      method: "GET",
      headers: { "Content-Type": "application/json" },
    }
  );

  return handleResponse<HistoryItem[] | HistoryApiResponse>(res);
}

export async function getHistoryItem(checkId: string): Promise<AnalysisResult> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/history/${checkId}`);
  const data = await handleResponse<unknown>(res);

  return mapAnalysisResponse(data);
}

export async function deleteHistoryItem(checkId: string): Promise<void> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/history/${checkId}`, {
    method: "DELETE",
  });

  await handleResponse<unknown>(res);
}

export interface UploadResult {
  drugs: string[];
  rawText: string;
  confidence: number;
  message: string;
}

export async function uploadPrescription(file: File): Promise<UploadResult> {
  const base = requireApiUrl();

  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${base}/api/upload-prescription`, {
    method: "POST",
    body: form,
  });

  return handleResponse<UploadResult>(res);
}

export interface DrugInfo {
  rxcui: string;
  name: string;
  drugClass: string;
  commonUses: string;
  sideEffects: string;
  brandNames: string[];
}

export async function getDrugInfo(rxcui: string): Promise<DrugInfo> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/drug-info/${rxcui}`);

  return handleResponse<DrugInfo>(res);
}
