// components/PersonalizeSection.tsx
"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, User } from "lucide-react";

interface Props {
  age?:      number;
  gender?:   string;
  onChange:  (data: { age?: number; gender?: string }) => void;
}

export default function PersonalizeSection({
  age,
  gender,
  onChange,
}: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="rounded-xl border border-gray-200 bg-white">
      {/* Toggle header */}
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center justify-between
                   px-4 py-3 text-left"
      >
        <div className="flex items-center gap-2">
          <User className="h-4 w-4 text-gray-400" />
          <span className="text-sm font-medium text-gray-700">
            Personalise (optional)
          </span>
          {(age || gender) && (
            <span className="rounded-full bg-indigo-100 px-2 py-0.5
                             text-xs text-indigo-700 font-medium">
              Added
            </span>
          )}
        </div>
        {open
          ? <ChevronUp   className="h-4 w-4 text-gray-400" />
          : <ChevronDown className="h-4 w-4 text-gray-400" />
        }
      </button>

      {/* Collapsible body */}
      {open && (
        <div className="border-t border-gray-100 px-4 py-4">
          <p className="text-xs text-gray-500 mb-3">
            Providing your details helps the AI personalise
            the explanation. Not required.
          </p>

          <div className="grid grid-cols-2 gap-3">
            {/* Age */}
            <div>
              <label className="block text-xs font-medium
                               text-gray-600 mb-1">
                Age
              </label>
              <input
                type="number"
                min={0}
                max={120}
                value={age || ""}
                onChange={(e) =>
                  onChange({
                    age:    e.target.value
                              ? parseInt(e.target.value)
                              : undefined,
                    gender,
                  })
                }
                placeholder="e.g. 65"
                className="w-full rounded-lg border border-gray-200
                           px-3 py-2 text-sm outline-none
                           focus:border-indigo-400"
              />
            </div>

            {/* Gender */}
            <div>
              <label className="block text-xs font-medium
                               text-gray-600 mb-1">
                Gender
              </label>
              <select
                value={gender || ""}
                onChange={(e) =>
                  onChange({ age, gender: e.target.value || undefined })
                }
                className="w-full rounded-lg border border-gray-200
                           px-3 py-2 text-sm outline-none
                           focus:border-indigo-400 bg-white"
              >
                <option value="">Prefer not to say</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}