// components/Disclaimer.tsx
import { TriangleAlert } from "lucide-react";
import { DISCLAIMER } from "@/lib/utils";

export default function Disclaimer() {
  return (
    <div className="flex gap-3 rounded-xl border border-yellow-200
                    bg-yellow-50 p-4">
      <TriangleAlert
        className="mt-0.5 h-5 w-5 shrink-0 text-yellow-600"
      />
      <p className="text-sm leading-relaxed text-yellow-800">
        <span className="font-semibold">Medical Disclaimer: </span>
        {DISCLAIMER}
      </p>
    </div>
  );
}