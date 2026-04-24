import { AnalysisResult, AnalyzeRequest, DrugSuggestion } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

// ── Response mapper ───────────────────────────────────────────────────────────

function mapAnalysisResponse(data: any): AnalysisResult {
  return {
    checkId:          data.check_id,
    drugsSubmitted:   data.drugs_submitted,
    drugsIdentified:  data.drugs_identified,
    drugList: (data.drug_list || []).map((d: any) => ({
      inputName:      d.input_name,
      normalizedName: d.normalized_name,
      rxcui:          d.rxcui,
      identified:     d.identified,
    })),
    pairsChecked:       data.pairs_checked,
    interactionsFound:  data.interactions_found,
    pairs: (data.pairs || []).map((p: any) => ({
      drug1:             p.drug1,
      drug2:             p.drug2,
      severity:          p.severity,
      severityEmoji:     p.severity_emoji     || "⚪",
      plainExplanation:  p.plain_explanation  || "",
      whatToWatchFor:    p.what_to_watch_for  || "",
      actionRequired:    p.action_required    || "",
      saferAlternatives: p.safer_alternatives || [],
      mechanism:         p.mechanism          || "",
      sources:           p.sources            || [],
    })),
    overallSeverity: data.overall_severity,
    overallEmoji:    data.overall_emoji   || "⚪",
    summary:         data.summary         || "",
    disclaimer:      data.disclaimer      || "",
    generatedAt:     data.generated_at    || "",
    responseTimeMs:  data.response_time_ms || 0,
    aiProvider:      data.ai_provider     || "groq",
    cachedPairs:     data.cached_pairs    || 0,
    isFallback:      data.is_fallback     || false,
  };
}

// ── Generic response handler ──────────────────────────────────────────────────

async function handleResponse<T>(res: Response): Promise<T> {
  const contentType = res.headers.get("content-type") || "";
  let data: any = null;

  if (contentType.includes("application/json")) {
    data = await res.json();
  } else {
    const text = await res.text();
    data = text ? { message: text } : null;
  }

  if (!res.ok) {
    throw new Error(
      data?.detail ||
      data?.message ||
      `Request failed with status ${res.status}`
    );
  }

  return data as T;
}

// ── Guard helper ──────────────────────────────────────────────────────────────

function requireApiUrl(): string {
  if (!API_URL) throw new Error("NEXT_PUBLIC_API_URL is not defined");
  return API_URL;
}

// ── Drug autocomplete ─────────────────────────────────────────────────────────

export async function getDrugAutocomplete(
  query: string
): Promise<DrugSuggestion[]> {
  const base = requireApiUrl();
  const trimmed = query.trim();
  if (trimmed.length < 2) return [];

  const res = await fetch(
    `${base}/api/drug-autocomplete?q=${encodeURIComponent(trimmed)}`
  );
  return handleResponse<DrugSuggestion[]>(res);
}

// ── Drug interaction analysis ─────────────────────────────────────────────────

export async function analyzeInteractions(
  payload: AnalyzeRequest
): Promise<AnalysisResult> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/analyze-interaction`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      drugs:      payload.drugs,
      age:        payload.age,
      gender:     payload.gender,
      allergies:  payload.allergies,
      session_id: payload.sessionId,
    }),
  });

  const data = await handleResponse<any>(res);
  return mapAnalysisResponse(data);
}

// ── RxChat ────────────────────────────────────────────────────────────────────

export async function sendChatMessage(
  message: string,
  currentDrugs: string[] = []
): Promise<{ response: string }> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/chat`, {
    method:  "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      current_drugs: currentDrugs,
    }),
  });
  return handleResponse<{ response: string }>(res);
}

// ── History ───────────────────────────────────────────────────────────────────

export interface HistoryItem {
  checkId:      string;
  drugsChecked: string[];
  severity:     string;
  checkedAt:    string;
  pairsFound:   number;
}

export async function getHistory(
  limit  = 20,
  offset = 0
): Promise<HistoryItem[]> {
  const base = requireApiUrl();

  const res = await fetch(
    `${base}/api/history?limit=${limit}&offset=${offset}`,
    {
      method:  "GET",
      headers: { "Content-Type": "application/json" },
    }
  );
  return handleResponse<HistoryItem[]>(res);
}

export async function getHistoryItem(checkId: string): Promise<AnalysisResult> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/history/${checkId}`);
  const data = await handleResponse<any>(res);
  return mapAnalysisResponse(data);
}

export async function deleteHistoryItem(checkId: string): Promise<void> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/history/${checkId}`, {
    method: "DELETE",
  });
  await handleResponse<void>(res);
}

// ── Prescription upload (OCR) ─────────────────────────────────────────────────

export interface UploadResult {
  drugs:       string[];
  rawText:     string;
  confidence:  number;
  message:     string;
}

export async function uploadPrescription(
  file: File
): Promise<UploadResult> {
  const base = requireApiUrl();

  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${base}/api/upload-prescription`, {
    method: "POST",
    body:   form,
    // Do NOT set Content-Type — browser sets it automatically with boundary
  });
  return handleResponse<UploadResult>(res);
}

// ── Drug info ─────────────────────────────────────────────────────────────────

export interface DrugInfo {
  rxcui:        string;
  name:         string;
  drugClass:    string;
  commonUses:   string;
  sideEffects:  string;
  brandNames:   string[];
}

export async function getDrugInfo(rxcui: string): Promise<DrugInfo> {
  const base = requireApiUrl();

  const res = await fetch(`${base}/api/drug-info/${rxcui}`);
  return handleResponse<DrugInfo>(res);
}