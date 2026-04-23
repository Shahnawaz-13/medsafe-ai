// components/SummaryBanner.tsx
import { Severity } from "@/types";
import { getSeverityConfig } from "@/lib/utils";
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Info,
} from "lucide-react";

interface Props {
  overallSeverity:  Severity;
  summary:          string;
  interactionCount: number;
  totalPairs:       number;
  drugsCount:       number;
}

export default function SummaryBanner({
  overallSeverity,
  summary,
  interactionCount,
  totalPairs,
  drugsCount,
}: Props) {
  const config = getSeverityConfig(overallSeverity);

  const Icon =
    overallSeverity === "contraindicated" || overallSeverity === "high"
      ? ShieldAlert
      : overallSeverity === "moderate"
      ? AlertTriangle
      : overallSeverity === "low"
      ? Info
      : ShieldCheck;

  return (
    <div
      className={`
        rounded-xl border-2 p-5
        ${config.bg} ${config.border}
      `}
    >
      {/* Top row */}
      <div className="flex items-start gap-3">
        <div
          className={`
            flex h-10 w-10 shrink-0 items-center justify-center
            rounded-xl bg-white/60
          `}
        >
          <Icon className={`h-5 w-5 ${config.text}`} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-2xl">{config.emoji}</span>
            <h2 className={`text-lg font-bold ${config.text}`}>
              Overall Risk: {config.label}
            </h2>
          </div>
          <p className={`mt-1 text-sm ${config.text} opacity-80`}>
            {summary}
          </p>
        </div>
      </div>

      {/* Stats row */}
      <div className="mt-4 flex gap-4 flex-wrap">
        <div className="text-center">
          <p className={`text-2xl font-bold ${config.text}`}>
            {drugsCount}
          </p>
          <p className="text-xs text-gray-500">Drugs checked</p>
        </div>
        <div className="w-px bg-gray-200" />
        <div className="text-center">
          <p className={`text-2xl font-bold ${config.text}`}>
            {totalPairs}
          </p>
          <p className="text-xs text-gray-500">Pairs analysed</p>
        </div>
        <div className="w-px bg-gray-200" />
        <div className="text-center">
          <p className={`text-2xl font-bold ${config.text}`}>
            {interactionCount}
          </p>
          <p className="text-xs text-gray-500">Interactions found</p>
        </div>
      </div>

      {/* Urgent warning */}
      {config.urgent && (
        <div className="mt-4 rounded-lg bg-white/60 border
                        border-red-200 p-3">
          <p className="text-xs font-semibold text-red-800">
            ⚠️ One or more serious interactions detected. Please
            consult your doctor or pharmacist before taking these
            medications together.
          </p>
        </div>
      )}
    </div>
  );
}