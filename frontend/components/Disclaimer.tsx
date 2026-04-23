// components/Disclaimer.tsx
import { TriangleAlert } from "lucide-react";
import { DISCLAIMER } from "@/lib/utils";

interface Props {
  className?: string;
  compact?:   boolean;
}

export default function Disclaimer({
  className = "",
  compact   = false,
}: Props) {
  return (
    <div
      className={`
        flex gap-3 rounded-xl border border-yellow-200
        bg-yellow-50 p-4 ${className}
      `}
    >
      <TriangleAlert
        className="mt-0.5 h-5 w-5 shrink-0 text-yellow-600"
      />
      <div>
        <p className="text-sm font-semibold text-yellow-800">
          Medical Disclaimer
        </p>
        {!compact && (
          <p className="mt-1 text-sm leading-relaxed text-yellow-700">
            {DISCLAIMER}
          </p>
        )}
        {compact && (
          <p className="mt-0.5 text-xs text-yellow-700">
            For educational purposes only. Not medical advice.
            Always consult your doctor or pharmacist.
          </p>
        )}
      </div>
    </div>
  );
}