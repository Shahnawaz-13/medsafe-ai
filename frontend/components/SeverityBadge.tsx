// components/SeverityBadge.tsx
import { Severity } from "@/types";
import { getSeverityConfig } from "@/lib/utils";

interface Props {
  severity: Severity;
  size?: "sm" | "md" | "lg";
}

export default function SeverityBadge({
  severity,
  size = "md",
}: Props) {
  const config = getSeverityConfig(severity);

  const sizeClass = {
    sm: "text-xs px-2 py-0.5",
    md: "text-sm px-3 py-1",
    lg: "text-base px-4 py-1.5",
  }[size];

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full
                  font-semibold ${sizeClass} ${config.badge}`}
    >
      <span>{config.emoji}</span>
      <span>{config.label}</span>
    </span>
  );
}