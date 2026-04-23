// components/InteractionCard.tsx
"use client";

import { useState } from "react";
import {
  ChevronDown,
  ChevronUp,
  AlertTriangle,
  Eye,
  Zap,
  Pill,
} from "lucide-react";
import { InteractionPair } from "@/types";
import { getSeverityConfig } from "@/lib/utils";
import SeverityBadge from "./SeverityBadge";

interface Props {
  pair:  InteractionPair;
  index: number;
}

export default function InteractionCard({ pair, index }: Props) {
  const [expanded, setExpanded] = useState(false);
  const config = getSeverityConfig(pair.severity);

  const hasDetails =
    pair.mechanism ||
    pair.sources?.length > 0;

  return (
    <div
      className={`
        rounded-xl border-2 p-5 transition-all duration-200
        ${config.border} ${config.bg}
      `}
    >
      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="min-w-0">
          <p className="text-xs font-medium text-gray-400 uppercase
                        tracking-wide mb-1">
            Interaction {index + 1}
          </p>
          <h3 className={`
            text-base font-bold leading-tight ${config.text}
          `}>
            {pair.drug1}
            <span className="mx-2 font-normal text-gray-400">+</span>
            {pair.drug2}
          </h3>
        </div>
        <SeverityBadge severity={pair.severity} size="sm" />
      </div>

      {/* ── Explanation ─────────────────────────────────────────── */}
      {pair.plainExplanation ? (
        <p className="text-sm leading-relaxed text-gray-700 mb-3">
          {pair.plainExplanation}
        </p>
      ) : (
        <p className="text-sm text-gray-500 italic mb-3">
          No interaction data found in current databases.
          Always consult your pharmacist.
        </p>
      )}

      {/* ── Watch for ───────────────────────────────────────────── */}
      {pair.whatToWatchFor && (
        <div className="flex gap-2 rounded-lg bg-yellow-50 border
                        border-yellow-200 p-3 mb-3">
          <Eye className="h-4 w-4 mt-0.5 shrink-0 text-yellow-600" />
          <div>
            <p className="text-xs font-semibold text-yellow-800 mb-0.5">
              What to watch for:
            </p>
            <p className="text-xs text-yellow-700">
              {pair.whatToWatchFor}
            </p>
          </div>
        </div>
      )}

      {/* ── Action required ─────────────────────────────────────── */}
      {pair.actionRequired && (
        <div className={`
          flex gap-2 rounded-lg p-3 mb-3
          ${config.urgent
            ? "bg-red-50 border border-red-200"
            : "bg-blue-50 border border-blue-200"
          }
        `}>
          <AlertTriangle className={`
            h-4 w-4 mt-0.5 shrink-0
            ${config.urgent ? "text-red-600" : "text-blue-600"}
          `} />
          <p className={`
            text-xs font-semibold
            ${config.urgent ? "text-red-800" : "text-blue-800"}
          `}>
            {pair.actionRequired}
          </p>
        </div>
      )}

      {/* ── Safer alternatives ──────────────────────────────────── */}
      {pair.saferAlternatives && pair.saferAlternatives.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center gap-1.5 mb-2">
            <Pill className="h-3.5 w-3.5 text-green-600" />
            <p className="text-xs font-semibold text-gray-600">
              Safer alternatives:
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {pair.saferAlternatives.map((alt) => (
              <span
                key={alt}
                className="rounded-full bg-green-100 px-3 py-1
                           text-xs font-medium text-green-700
                           border border-green-200"
              >
                {alt}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* ── Technical details (collapsible) ─────────────────────── */}
      {hasDetails && (
        <>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-xs text-gray-400
                       hover:text-gray-600 transition-colors mt-1"
          >
            {expanded
              ? <ChevronUp  className="h-3.5 w-3.5" />
              : <ChevronDown className="h-3.5 w-3.5" />
            }
            {expanded ? "Hide" : "Show"} technical details
          </button>

          {expanded && (
            <div className="mt-3 rounded-lg bg-gray-50 border
                            border-gray-200 p-3">
              {pair.mechanism && (
                <div className="mb-2">
                  <div className="flex items-center gap-1.5 mb-1">
                    <Zap className="h-3 w-3 text-gray-500" />
                    <p className="text-xs font-semibold text-gray-500">
                      Mechanism:
                    </p>
                  </div>
                  <p className="text-xs text-gray-500 leading-relaxed">
                    {pair.mechanism}
                  </p>
                </div>
              )}
              {pair.sources && pair.sources.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-400 mb-1">
                    Sources:
                  </p>
                  <p className="text-xs text-gray-400">
                    {pair.sources.join(", ")}
                  </p>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}