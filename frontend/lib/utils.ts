// lib/utils.ts

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { Severity } from "@/types";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const DISCLAIMER =
  "MedSafe AI provides general drug interaction information " +
  "for educational purposes only. This tool does not " +
  "constitute medical advice and is not a substitute for " +
  "professional consultation. Always consult a licensed " +
  "physician or pharmacist before making any medication " +
  "decisions. In case of emergency, call your local " +
  "emergency services immediately.";

type SeverityConfig = {
  bg: string;
  border: string;
  text: string;
  badge: string;
  emoji: string;
  label: string;
  urgent: boolean;
};

export function getSeverityConfig(severity: Severity) {
  const configs: Record<Severity, SeverityConfig> = {
    contraindicated: {
      bg: "bg-red-50",
      border: "border-red-300",
      text: "text-red-800",
      badge: "bg-red-100 text-red-800 border border-red-200",
      emoji: "🚫",
      label: "CONTRAINDICATED",
      urgent: true,
    },

    high: {
      bg: "bg-orange-50",
      border: "border-orange-300",
      text: "text-orange-800",
      badge: "bg-orange-100 text-orange-800 border border-orange-200",
      emoji: "🔴",
      label: "HIGH",
      urgent: true,
    },

    moderate: {
      bg: "bg-yellow-50",
      border: "border-yellow-300",
      text: "text-yellow-800",
      badge: "bg-yellow-100 text-yellow-800 border border-yellow-200",
      emoji: "🟡",
      label: "MODERATE",
      urgent: false,
    },

    low: {
      bg: "bg-green-50",
      border: "border-green-300",
      text: "text-green-800",
      badge: "bg-green-100 text-green-800 border border-green-200",
      emoji: "🟢",
      label: "LOW",
      urgent: false,
    },

    none: {
      bg: "bg-gray-50",
      border: "border-gray-200",
      text: "text-gray-600",
      badge: "bg-gray-100 text-gray-600 border border-gray-200",
      emoji: "⚪",
      label: "NO INTERACTION",
      urgent: false,
    },
  };

  return configs[severity] ?? configs.none;
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function capitalise(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}