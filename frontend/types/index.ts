// types/index.ts

export type Severity =
  | "low"
  | "moderate"
  | "high"
  | "contraindicated"
  | "none";

export interface InteractionPair {
  drug1: string;
  drug2: string;
  severity: Severity;
  severityEmoji: string;
  plainExplanation: string;
  whatToWatchFor: string;
  actionRequired: string;
  saferAlternatives: string[];
  mechanism: string;
  sources: string[];
}

export interface AnalysisResult {
  checkId: string;
  pairs: InteractionPair[];
  overallSeverity: Severity;
  summary: string;
  disclaimer: string;
  generatedAt: string;
  cached: boolean;
}

export interface DrugSuggestion {
  name: string;
  rxcui: string;
}

export interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  interactionsFound?: InteractionPair[];
}

export interface HistoryItem {
  id: string;
  drugs: string[];
  date: string;
  overallSeverity: Severity;
  result: AnalysisResult;
}

export interface DrugEntry {
  inputName: string;
  normalizedName: string;
  rxcui?: string;
}

export interface AnalyzeRequest {
  drugs: string[];
  age?: number;
  gender?: string;
  allergies?: string[];
  sessionId?: string;
}

export interface ChatRequest {
  message: string;
  history: Message[];
}