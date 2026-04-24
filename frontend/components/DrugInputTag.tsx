// components/DrugInputTag.tsx
"use client";

import {
  useState,
  useRef,
  useCallback,
  useEffect,
  KeyboardEvent,
} from "react";
import { X, Search, Loader2, CheckCircle } from "lucide-react";
import { DrugSuggestion } from "@/types";
import { getDrugAutocomplete } from "@/lib/api";
import { cn } from "@/lib/utils";

interface DrugTag {
  id: string;
  inputName: string;
  displayName: string;
  rxcui?: string;
  isValidated: boolean;
}

interface Props {
  drugs: DrugTag[];
  onAdd: (drug: DrugTag) => void;
  onRemove: (id: string) => void;
  onClearAll: () => void;
  maxDrugs?: number;
  disabled?: boolean;
}

export default function DrugInputTag({
  drugs,
  onAdd,
  onRemove,
  onClearAll,
  maxDrugs = 15,
  disabled = false,
}: Props) {
  const [inputValue, setInputValue] = useState("");
  const [suggestions, setSuggestions] = useState<DrugSuggestion[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [error, setError] = useState("");

  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const isAtMax = drugs.length >= maxDrugs;

  const fetchSuggestions = useCallback(async (query: string) => {
    const cleaned = query.trim();

    if (cleaned.length < 2) {
      setSuggestions([]);
      setShowDropdown(false);
      setActiveIndex(-1);
      return;
    }

    setIsLoading(true);
    try {
      const results = await getDrugAutocomplete(cleaned);
      setSuggestions(results);
      setShowDropdown(true);
      setActiveIndex(-1);
    } catch {
      setSuggestions([]);
      setShowDropdown(true);
      setActiveIndex(-1);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleInputChange = (value: string) => {
    setInputValue(value);
    setError("");

    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);
  };

  const addDrug = useCallback(
    (name: string, rxcui?: string, isValidated = false) => {
      const trimmed = name.trim();
      if (!trimmed) return;

      if (trimmed.length < 2) {
        setError("Drug name must be at least 2 characters.");
        return;
      }

      if (drugs.length >= maxDrugs) {
        setError(`Maximum ${maxDrugs} medications allowed.`);
        return;
      }

      const normalized = trimmed.toLowerCase().trim();
      const duplicate = drugs.some(
        (d) => d.displayName.toLowerCase().trim() === normalized
      );

      if (duplicate) {
        setError(`"${trimmed}" is already in your list.`);
        return;
      }

      const newDrug: DrugTag = {
        id: `${Date.now()}-${Math.random()}`,
        inputName: trimmed,
        displayName: trimmed,
        rxcui,
        isValidated,
      };

      onAdd(newDrug);
      setInputValue("");
      setSuggestions([]);
      setShowDropdown(false);
      setActiveIndex(-1);
      setError("");
      inputRef.current?.focus();
    },
    [drugs, maxDrugs, onAdd]
  );

  const selectSuggestion = useCallback(
    (suggestion: DrugSuggestion) => {
      addDrug(suggestion.name, suggestion.rxcui, true);
    },
    [addDrug]
  );

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      if (!showDropdown) setShowDropdown(true);
      setActiveIndex((prev) =>
        prev < suggestions.length - 1 ? prev + 1 : prev
      );
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : -1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (isLoading) return;

      if (activeIndex >= 0 && suggestions[activeIndex]) {
        selectSuggestion(suggestions[activeIndex]);
      } else if (inputValue.trim()) {
        addDrug(inputValue);
      }
    } else if (e.key === "Escape") {
      setShowDropdown(false);
      setActiveIndex(-1);
    } else if (e.key === "Backspace" && !inputValue && drugs.length > 0) {
      onRemove(drugs[drugs.length - 1].id);
    }
  };

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        !inputRef.current?.contains(e.target as Node)
      ) {
        setShowDropdown(false);
        setActiveIndex(-1);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () =>
      document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  return (
    <div className="w-full">
      <div
        className={cn(
          "relative min-h-14 w-full rounded-xl border-2 bg-white",
          "p-2 transition-colors",
          disabled
            ? "cursor-not-allowed border-gray-100 bg-gray-50"
            : "border-gray-200 hover:border-indigo-200 focus-within:border-indigo-400"
        )}
        onClick={() => !disabled && inputRef.current?.focus()}
      >
        <div className="flex min-h-10 flex-wrap items-center gap-1.5">
          {drugs.map((drug) => (
            <DrugTagPill
              key={drug.id}
              drug={drug}
              onRemove={onRemove}
              disabled={disabled}
            />
          ))}

          {!isAtMax && !disabled && (
            <div className="relative min-w-40 flex-1">
              <input
                ref={inputRef}
                type="text"
                value={inputValue}
                onChange={(e) => handleInputChange(e.target.value)}
                onKeyDown={handleKeyDown}
                onFocus={() => {
                  if (suggestions.length > 0 || inputValue.trim().length >= 2) {
                    setShowDropdown(true);
                  }
                }}
                placeholder={
                  drugs.length === 0
                    ? "Type a medicine name..."
                    : "Add another..."
                }
                className="w-full bg-transparent px-2 py-1 pr-8 text-sm text-gray-800 outline-none placeholder:text-gray-400"
                disabled={disabled}
                aria-label="Medication name"
              />

              {isLoading && (
                <Loader2 className="absolute right-2 top-1.5 h-4 w-4 animate-spin text-indigo-400" />
              )}
            </div>
          )}

          {isAtMax && (
            <span className="px-2 text-xs font-medium text-orange-500">
              Maximum {maxDrugs} drugs reached
            </span>
          )}
        </div>

        {showDropdown && (
          <div
            ref={dropdownRef}
            className="absolute left-0 right-0 top-full z-50 mt-1 overflow-hidden rounded-xl border border-gray-200 bg-white shadow-lg"
          >
            {suggestions.length > 0 ? (
              <>
                <div className="max-h-60 overflow-y-auto p-1">
                  {suggestions.map((suggestion, idx) => (
                    <button
                      key={suggestion.rxcui || idx}
                      type="button"
                      onClick={() => selectSuggestion(suggestion)}
                      className={cn(
                        "flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
                        idx === activeIndex
                          ? "bg-indigo-50 text-indigo-700"
                          : "text-gray-700 hover:bg-gray-50"
                      )}
                    >
                      <Search className="h-3.5 w-3.5 shrink-0 text-gray-400" />
                      <span className="flex-1 font-medium">
                        {suggestion.name}
                      </span>
                      {suggestion.rxcui && (
                        <span className="text-xs text-gray-400">
                          RxCUI: {suggestion.rxcui}
                        </span>
                      )}
                    </button>
                  ))}
                </div>

                <div className="border-t border-gray-100 px-3 py-2">
                  <p className="text-xs text-gray-400">
                    Press Enter to add · ↑↓ to navigate · Esc to close
                  </p>
                </div>
              </>
            ) : (
              !isLoading &&
              inputValue.trim().length >= 2 && (
                <div className="px-3 py-2 text-xs text-gray-400">
                  No matches found
                </div>
              )
            )}
          </div>
        )}
      </div>

      {error && (
        <p className="mt-1.5 text-xs font-medium text-red-500">{error}</p>
      )}

      <div className="mt-2 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <span
            className={cn(
              "text-sm font-semibold",
              drugs.length >= 2 ? "text-indigo-600" : "text-gray-400"
            )}
          >
            {drugs.length}
          </span>
          <span className="text-sm text-gray-400">
            medication{drugs.length !== 1 ? "s" : ""} added
          </span>
          {drugs.length >= 2 && (
            <span className="text-xs text-indigo-500">
              ({(drugs.length * (drugs.length - 1)) / 2} pairs to check)
            </span>
          )}
        </div>

        {drugs.length > 0 && (
          <button
            type="button"
            onClick={onClearAll}
            className="text-xs font-medium text-gray-400 transition-colors hover:text-red-500"
          >
            Clear all
          </button>
        )}
      </div>

      {drugs.length === 1 && (
        <p className="mt-1 text-xs text-amber-600">
          Add at least one more medication to check interactions.
        </p>
      )}
    </div>
  );
}

function DrugTagPill({
  drug,
  onRemove,
  disabled,
}: {
  drug: DrugTag;
  onRemove: (id: string) => void;
  disabled: boolean;
}) {
  return (
    <div
      className={cn(
        "flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-medium transition-colors",
        drug.isValidated
          ? "border-indigo-200 bg-indigo-100 text-indigo-800"
          : "border-gray-200 bg-gray-100 text-gray-700"
      )}
    >
      {drug.isValidated && (
        <CheckCircle className="h-3.5 w-3.5 text-indigo-500" />
      )}

      <span>{drug.displayName}</span>

      {!disabled && (
        <button
          type="button"
          aria-label={`Remove ${drug.displayName}`}
          onClick={(e) => {
            e.stopPropagation();
            onRemove(drug.id);
          }}
          className={cn(
            "rounded-full p-1 transition-all",
            "focus:outline-none focus:ring-2 focus:ring-indigo-400",
            "active:scale-95",
            drug.isValidated
              ? "hover:scale-110 hover:bg-indigo-200"
              : "hover:scale-110 hover:bg-gray-200"
          )}
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}

export type { DrugTag };