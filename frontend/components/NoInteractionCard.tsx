// components/NoInteractionCard.tsx
import { CheckCircle2 } from "lucide-react";

interface Props {
  drug1: string;
  drug2: string;
}

export default function NoInteractionCard({ drug1, drug2 }: Props) {
  return (
    <div className="rounded-xl border border-gray-200 bg-gray-50 p-4">
      <div className="flex items-center gap-2">
        <CheckCircle2 className="h-4 w-4 text-gray-400 shrink-0" />
        <p className="text-sm text-gray-600">
          <span className="font-medium text-gray-800">{drug1}</span>
          <span className="mx-1.5 text-gray-400">+</span>
          <span className="font-medium text-gray-800">{drug2}</span>
          <span className="ml-1.5 text-gray-500">
            — No known interaction detected
          </span>
        </p>
        <span className="ml-auto text-base">⚪</span>
      </div>
    </div>
  );
}