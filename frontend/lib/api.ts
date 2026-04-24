import { AnalysisResult, AnalyzeRequest, DrugSuggestion } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

function mapAnalysisResponse(data: any): AnalysisResult {
  return {
    checkId: data.check_id,
    drugsSubmitted: data.drugs_submitted,
    drugsIdentified: data.drugs_identified,
    drugList: (data.drug_list || []).map((d: any) => ({
      inputName: d.input_name,
      normalizedName: d.normalized_name,
      rxcui: d.rxcui,
      identified: d.identified,
    })),
    pairsChecked: data.pairs_checked,
    interactionsFound: data.interactions_found,
    pairs: (data.pairs || []).map((p: any) => ({
      drug1: p.drug1,
      drug2: p.drug2,
      severity: p.severity,
      severityEmoji: p.severity_emoji || "⚪",
      plainExplanation: p.plain_explanation || "",
      whatToWatchFor: p.what_to_watch_for || "",
      actionRequired: p.action_required || "",
      saferAlternatives: p.safer_alternatives || [],
      mechanism: p.mechanism || "",
      sources: p.sources || [],
    })),
    overallSeverity: data.overall_severity,
    overallEmoji: data.overall_emoji || "⚪",
    summary: data.summary || "",
    disclaimer: data.disclaimer || "",
    generatedAt: data.generated_at || "",
    responseTimeMs: data.response_time_ms || 0,
    aiProvider: data.ai_provider || "groq",
    cachedPairs: data.cached_pairs || 0,
    isFallback: data.is_fallback || false,
  };
}

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

export async function getDrugAutocomplete(
  query: string
): Promise<DrugSuggestion[]> {
  if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not defined");
  }

  const trimmedQuery = query.trim();

  if (trimmedQuery.length < 2) {
    return [];
  }

  const res = await fetch(
    `${API_URL}/api/drug-autocomplete?q=${encodeURIComponent(trimmedQuery)}`
  );

  return handleResponse<DrugSuggestion[]>(res);
}

export async function analyzeInteractions(
  payload: AnalyzeRequest
): Promise<AnalysisResult> {
  if (!API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL is not defined");
  }

  const res = await fetch(`${API_URL}/api/analyze-interaction`, {
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

  const data = await handleResponse<any>(res);
  return mapAnalysisResponse(data);
}