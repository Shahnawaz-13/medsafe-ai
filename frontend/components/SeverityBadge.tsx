// components/SeverityBadge.tsx
import { Severity } from "@/types";
import { getSeverityConfig } from "@/lib/utils";

interface Props {
  severity: Severity;
  size?:    "sm" | "md" | "lg";
  showEmoji?: boolean;
}

export default function SeverityBadge({
  severity,
  size = "md",
  showEmoji = true,
}: Props) {
  const config = getSeverityConfig(severity);

  const sizeClass = {
    sm: "text-xs px-2   py-0.5 gap-1",
    md: "text-sm px-3   py-1   gap-1.5",
    lg: "text-base px-4 py-1.5 gap-2",
  }[size];

  return (
    <span
      className={`
        inline-flex items-center rounded-full font-semibold
        ${sizeClass} ${config.badge}
      `}
    >
      {showEmoji && <span>{config.emoji}</span>}
      <span>{config.label}</span>
    </span>
  );
}