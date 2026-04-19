// lib/utils.ts
import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { Severity } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getSeverityConfig(severity: Severity) {
  const configs = {
    contraindicated: {
      bg:     "bg-red-50",
      border: "border-red-300",
      text:   "text-red-800",
      badge:  "bg-red-100 text-red-800",
      emoji:  "🚫",
      label:  "CONTRAINDICATED",
    },
    high: {
      bg:     "bg-orange-50",
      border: "border-orange-300",
      text:   "text-orange-800",
      badge:  "bg-orange-100 text-orange-800",
      emoji:  "🔴",
      label:  "HIGH",
    },
    moderate: {
      bg:     "bg-yellow-50",
      border: "border-yellow-300",
      text:   "text-yellow-800",
      badge:  "bg-yellow-100 text-yellow-800",
      emoji:  "🟡",
      label:  "MODERATE",
    },
    low: {
      bg:     "bg-green-50",
      border: "border-green-300",
      text:   "text-green-800",
      badge:  "bg-green-100 text-green-800",
      emoji:  "🟢",
      label:  "LOW",
    },
    none: {
      bg:     "bg-gray-50",
      border: "border-gray-200",
      text:   "text-gray-600",
      badge:  "bg-gray-100 text-gray-600",
      emoji:  "⚪",
      label:  "NO INTERACTION",
    },
  };
  return configs[severity] ?? configs.none;
}

export const DISCLAIMER =
  "MedSafe AI provides general drug interaction information " +
  "for educational purposes only. This tool does not constitute " +
  "medical advice and is not a substitute for professional " +
  "consultation. Always consult a licensed physician or pharmacist " +
  "before making any medication decisions. In case of emergency, " +
  "call your local emergency services immediately.";