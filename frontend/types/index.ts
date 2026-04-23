// types/index.ts
export type Severity =
  | "low"
  | "moderate"
  | "high"
  | "contraindicated"
  | "none";

export interface InteractionPair {
  drug1:             string;
  drug2:             string;
  severity:          Severity;
  severityEmoji:     string;
  plainExplanation:  string;
  whatToWatchFor:    string;
  actionRequired:    string;
  saferAlternatives: string[];
  mechanism:         string;
  sources:           string[];
}

export interface DrugEntry {
  inputName:      string;
  normalizedName: string;
  rxcui?:         string;
  identified:     boolean;
}

export interface AnalysisResult {
  checkId:           string;
  drugsSubmitted:    number;
  drugsIdentified:   number;
  drugList:          DrugEntry[];
  pairsChecked:      number;
  interactionsFound: number;
  pairs:             InteractionPair[];
  overallSeverity:   Severity;
  overallEmoji:      string;
  summary:           string;
  disclaimer:        string;
  generatedAt:       string;
  responseTimeMs:    number;
  aiProvider:        string;
  cachedPairs:       number;
  isFallback:        boolean;
}

export interface DrugSuggestion {
  name:  string;
  rxcui: string;
  score?: number;
}

export interface Message {
  role:              "user" | "assistant";
  content:           string;
  timestamp:         string;
  interactionsFound?: InteractionPair[];
}

export interface HistoryItem {
  checkId:           string;
  drugs:             DrugEntry[];
  overallSeverity:   Severity;
  interactionsFound: number;
  timestamp:         string;
}

export interface AnalyzeRequest {
  drugs:      string[];
  age?:       number;
  gender?:    string;
  allergies?: string[];
  sessionId?: string;
}

export interface ChatMessage {
  role:    "user" | "assistant";
  content: string;
}

export interface AutocompleteResult {
  suggestions: DrugSuggestion[];
  fromCache:   boolean;
}