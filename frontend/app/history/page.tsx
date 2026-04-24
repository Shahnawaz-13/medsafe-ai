// app/history/page.tsx
"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  History,
  Clock,
  Pill,
  ChevronDown,
  ChevronUp,
  Trash2,
  ArrowRight,
  Shield,
  Loader2,
  RefreshCw,
} from "lucide-react";
import SeverityBadge from "@/components/SeverityBadge";
import Disclaimer from "@/components/Disclaimer";
import { getHistory } from "@/lib/api";
import { Severity } from "@/types";
import { cn, formatDate } from "@/lib/utils";

interface HistoryCheck {
  check_id: string;
  drugs: { normalized_name?: string; input_name?: string }[];
  overall_severity: Severity;
  interactions_found: number;
  timestamp: string;
}

interface HistoryResponse {
  checks: HistoryCheck[];
  total: number;
}

function HistoryCard({
  check,
  onDelete,
}: {
  check: HistoryCheck;
  onDelete: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const drugNames = check.drugs.map(
    (d) => d.normalized_name || d.input_name || "Unknown"
  );

  const handleDelete = async () => {
    if (!confirm("Delete this check from history?")) return;

    setDeleting(true);

    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/history/${check.check_id}`,
        { method: "DELETE" }
      );

      if (res.ok) {
        onDelete(check.check_id);
      } else {
        alert("Could not delete. Please try again.");
      }
    } catch {
      alert("Could not delete. Please try again.");
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
      <div className="p-5">
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <div className="mb-2 flex items-center gap-1.5">
              <Clock className="h-3.5 w-3.5 text-gray-400" />
              <p className="text-xs text-gray-400">
                {formatDate(check.timestamp)}
              </p>
            </div>

            <div className="mb-3 flex flex-wrap gap-1.5">
              {drugNames.map((name, index) => (
                <span
                  key={`${name}-${index}`}
                  className="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700"
                >
                  <Pill className="h-3 w-3" />
                  {name}
                </span>
              ))}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <SeverityBadge severity={check.overall_severity} size="sm" />

              <span className="text-xs text-gray-500">
                {check.interactions_found} interaction
                {check.interactions_found !== 1 ? "s" : ""} found
              </span>

              <span className="text-xs text-gray-400">
                {drugNames.length} drugs ·{" "}
                {(drugNames.length * (drugNames.length - 1)) / 2} pairs
              </span>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-1">
            <button
              type="button"
              onClick={handleDelete}
              disabled={deleting}
              className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-red-50 hover:text-red-500 disabled:cursor-not-allowed disabled:opacity-50"
              title="Delete this check"
              aria-label="Delete this check"
            >
              {deleting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Trash2 className="h-4 w-4" />
              )}
            </button>

            <button
              type="button"
              onClick={() => setExpanded((prev) => !prev)}
              className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-50 hover:text-gray-600"
              aria-label={expanded ? "Collapse details" : "Expand details"}
            >
              {expanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-100 bg-gray-50 px-5 py-4">
          <p className="mb-2 text-xs font-medium text-gray-500">
            Check ID: {check.check_id.slice(0, 16)}...
          </p>

          <div className="flex flex-wrap gap-2">
            <Link
              href={`/check?drugs=${encodeURIComponent(drugNames.join(","))}`}
              className="inline-flex items-center gap-1.5 rounded-lg bg-indigo-600 px-3 py-2 text-xs font-semibold text-white transition-colors hover:bg-indigo-700"
            >
              <Shield className="h-3.5 w-3.5" />
              Re-run this check
              <ArrowRight className="h-3 w-3" />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}

export default function HistoryPage() {
  const [checks, setChecks] = useState<HistoryCheck[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const LIMIT = 10;

  const fetchHistory = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await getHistory();

      const historyChecks: HistoryCheck[] = Array.isArray(data)
        ? (data as unknown as HistoryCheck[])
        : ((data as unknown as HistoryResponse).checks || []);

      const historyTotal: number = Array.isArray(data)
        ? data.length
        : ((data as unknown as HistoryResponse).total || historyChecks.length);

      setChecks(historyChecks);
      setTotal(historyTotal);
    } catch {
      setError("Could not load history. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [page]);

  const handleDelete = (id: string) => {
    setChecks((prev) => prev.filter((c) => c.check_id !== id));
    setTotal((prev) => Math.max(0, prev - 1));
  };

  const totalPages = Math.ceil(total / LIMIT);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-3xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <div className="mb-1 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600">
                <History className="h-5 w-5 text-white" />
              </div>

              <h1 className="text-2xl font-bold text-gray-900">
                Check History
              </h1>
            </div>

            <p className="ml-13 text-sm text-gray-500">
              Your past medication interaction checks
            </p>
          </div>

          <button
            type="button"
            onClick={fetchHistory}
            className="flex items-center gap-1.5 rounded-lg border border-gray-200 bg-white px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50"
          >
            <RefreshCw className="h-4 w-4" />
            Refresh
          </button>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center">
              <Loader2 className="mx-auto mb-3 h-8 w-8 animate-spin text-indigo-400" />
              <p className="text-sm text-gray-500">Loading history...</p>
            </div>
          </div>
        )}

        {error && !loading && (
          <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-center">
            <p className="mb-3 text-sm text-red-700">{error}</p>
            <button
              type="button"
              onClick={fetchHistory}
              className="text-sm font-medium text-red-600 underline hover:text-red-800"
            >
              Try again
            </button>
          </div>
        )}

        {!loading && !error && checks.length === 0 && (
          <div className="rounded-2xl border-2 border-dashed border-gray-200 bg-white p-12 text-center">
            <Shield className="mx-auto mb-4 h-12 w-12 text-gray-300" />

            <h3 className="mb-2 text-base font-semibold text-gray-700">
              No history yet
            </h3>

            <p className="mx-auto mb-6 max-w-xs text-sm text-gray-400">
              Your medication checks will appear here after you use the drug
              checker.
            </p>

            <Link
              href="/check"
              className="inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-indigo-700"
            >
              <Shield className="h-4 w-4" />
              Start Your First Check
            </Link>
          </div>
        )}

        {!loading && !error && checks.length > 0 && (
          <>
            <div className="mb-4 flex items-center justify-between">
              <p className="text-sm text-gray-500">
                {total} check{total !== 1 ? "s" : ""} total
              </p>
            </div>

            <div className="space-y-3">
              {checks.map((check) => (
                <HistoryCard
                  key={check.check_id}
                  check={check}
                  onDelete={handleDelete}
                />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-center gap-2">
                <button
                  type="button"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                  className={cn(
                    "rounded-lg border px-4 py-2 text-sm font-medium",
                    page === 1
                      ? "cursor-not-allowed border-gray-100 text-gray-300"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  )}
                >
                  Previous
                </button>

                <span className="text-sm text-gray-500">
                  Page {page} of {totalPages}
                </span>

                <button
                  type="button"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                  className={cn(
                    "rounded-lg border px-4 py-2 text-sm font-medium",
                    page === totalPages
                      ? "cursor-not-allowed border-gray-100 text-gray-300"
                      : "border-gray-200 text-gray-600 hover:bg-gray-50"
                  )}
                >
                  Next
                </button>
              </div>
            )}
          </>
        )}

        <div className="mt-8">
          <Disclaimer compact />
        </div>
      </div>
    </div>
  );
}